from .base import *
from .hook import *
from .page import *


def setToolTip(widget: QWidget, text: str):
    widget.setToolTip(text)
    widget.installEventFilter(ToolTipFilter(widget, 1000))


class AnimationBase:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.duration = 500

        self.pos_animation = QPropertyAnimation(self.widget, b"pos")
        self.pos_animation.setDuration(self.duration)

        self.widget.show()
        self._originalPos = self.widget.pos()
        self.widget.showEvent = self.show
        self.widget.moveEvent = self.move

    def move(self, msg):
        if not self.pos_animation.state() == QParallelAnimationGroup.Running:
            self._originalPos = self.widget.pos()

    def show(self, msg):

        self.pos_animation.setStartValue(QPoint(self._originalPos.x(), self._originalPos.y() + 25))
        self.pos_animation.setEndValue(self._originalPos)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        if self.pos_animation.state() == QParallelAnimationGroup.Running:
            self.pos_animation.stop()
            self.widget.setWindowOpacity(1.0)
            self.widget.move(self._originalPos)
        self.pos_animation.start()


class StatisticsWidget(QWidget):
    """
    两行信息组件
    """

    def __init__(self, title: str, value: str, parent=None):
        """
        @param title: 标题
        @param value: 值
        """
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)
        self.valueLabel = BodyLabel(value, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignBottom)

        setFont(self.valueLabel, 18, QFont.Weight.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class Image(QLabel):
    """
    图片组件（可实时下载）
    """

    @functools.singledispatchmethod
    def __init__(self, parent=None, fixed_size=True, thread_pool: QThreadPool = None):
        super().__init__(parent=parent)
        if fixed_size:
            self.setFixedSize(48, 48)
        self.setScaledContents(True)
        self.loading = False
        self.threadPool = thread_pool

    @__init__.register
    def _(self, path: str, url: str = None, parent=None, fixed_size=True, thread_pool: QThreadPool = None):
        """
        @param path: 路径
        @param url: 链接
        """
        self.__init__(parent, fixed_size, thread_pool)
        if path:
            self.setImg(path, url)

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        if url:
            self.loading = True
            self.path = path
            self.url = url
            self.downloadImageThread = self.threadPool.submit(self.downloadImage)
        else:
            self.loading = False
            self.setPixmap(QPixmap(path))

    def downloadImage(self):
        msg = f.singleDownload(self.url, self.path, True, True, Info.REQUEST_HEADER)
        if msg:
            self.loading = False
            self.setPixmap(QPixmap(self.path))


class CopyTextButton(ToolButton):
    """
    复制文本按钮
    """

    def __init__(self, text, data: str | None = "", parent=None):
        """
        复制文本按钮
        @param text: 复制的文本
        @param data: 复制文本的提示信息，可以提示复制文本的内容类型
        @param parent: 父组件
        """
        super().__init__(parent)
        self.setIcon(FIF.COPY)
        self.clicked.connect(self.copyButtonClicked)
        if data is None:
            data = ""
        self.load(text, data)

    def load(self, text, data):
        if not text:
            self.setEnabled(False)
            return
        self.text = str(text)

        setToolTip(self, f"点击复制{data}信息！")

    def setData(self, text, data):
        self.load(text, data)

    def copyButtonClicked(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text)


class DisplayCard(ElevatedCardWidget):
    """
    大图片卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(168, 176)
        self.setStyleSheet("QLabel {background-color: rgba(0,0,0,0); border: none;}")

        self.widget = Image(self)

        self.bodyLabel = CaptionLabel(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.widget, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.bodyLabel, 0, Qt.AlignHCenter | Qt.AlignBottom)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def setText(self, text: str):
        """
        设置文本
        @param text: 文本
        """
        self.bodyLabel.setText(text)

    def setDisplay(self, widget):
        """
        设置展示组件
        @param widget: 组件
        """
        self.widget = widget
        self.vBoxLayout.replaceWidget(self.vBoxLayout.itemAt(1).widget(), self.widget)


class IntroductionCard(ElevatedCardWidget):
    """
    简介卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(190, 200)

        self.image = Image(self)
        self.titleLabel = SubtitleLabel(self)
        self.titleLabel.setWordWrap(True)
        self.bodyLabel = BodyLabel(self)
        self.bodyLabel.setWordWrap(True)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(16, 16, 16, 16)
        self.vBoxLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.bodyLabel, 0, Qt.AlignLeft)

    def setImg(self, path: str, url: str = None):
        self.image.setImg(path, url)

    def setTitle(self, text: str):
        self.titleLabel.setText(text)

    def setText(self, text: str):
        self.bodyLabel.setText(text)


class LoadingCard(DisplayCard):
    """
    加载中卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progressRingLoading = IndeterminateProgressRing(self)
        self.setDisplay(self.progressRingLoading)
        self.setText("加载中...")


class GrayCard(QWidget):
    """
    灰色背景组件卡片
    """

    def __init__(self, title: str = None, parent=None, alignment=Qt.AlignLeft, animation: bool = True):
        """
        @param title: 标题
        """
        super().__init__(parent=parent)

        self.titleLabel = StrongBodyLabel(self)
        if title:
            self.titleLabel.setText(title)
        else:
            self.titleLabel.hide()

        self.card = QFrame(self)
        self.card.setObjectName("GrayCard")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignTop)

        self.hBoxLayout = QHBoxLayout(self.card)
        self.hBoxLayout.setAlignment(alignment)
        self.hBoxLayout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(12, 12, 12, 12)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

        if animation:
            self.animation = AnimationBase(self)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
            self.card.setStyleSheet("#GrayCard {background-color: rgba(25,25,25,0.5); border:1px solid rgba(20,20,20,0.15); border-radius: 10px}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")
            self.card.setStyleSheet("#GrayCard {background-color: rgba(175,175,175,0.1); border:1px solid rgba(150,150,150,0.15); border-radius: 10px}")

    def addWidget(self, widget, spacing=0, alignment=Qt.AlignTop):
        """
        添加组件
        @param widget: 组件
        @param spacing: 间隔
        @param alignment: 对齐方式
        """
        self.hBoxLayout.addWidget(widget, alignment=alignment)
        self.hBoxLayout.addSpacing(spacing)

    def insertWidget(self, index: int, widget, alignment=Qt.AlignTop):
        """
        插入组件
        @param index: 序号
        @param widget: 组件
        @param alignment: 对齐方式
        """
        self.hBoxLayout.insertWidget(index, widget, 0, alignment)


class BigInfoCard(CardWidget):
    """
    详细信息卡片（资源主页展示）
    """

    def __init__(self, parent=None, url: bool = True, tag: bool = True, data: bool = True, animation: bool = True):
        """
        @param url: 是否展示链接
        @param tag: 是否展示标签
        @param data: 是否展示数据
        """
        super().__init__(parent)
        self.setMinimumWidth(100)

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.move(8, 8)
        self.backButton.setMaximumSize(32, 32)
        self.backButton.clicked.connect(self.backButtonClicked)

        self.image = Image(self)

        self.titleLabel = TitleLabel(self)

        self.mainButton = PrimaryPushButton("", self)
        self.mainButton.setFixedWidth(160)

        self.infoLabel = BodyLabel(self)
        self.infoLabel.setWordWrap(True)

        self.hBoxLayout1 = QHBoxLayout()
        self.hBoxLayout1.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout1.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        self.hBoxLayout1.addWidget(self.mainButton, 0, Qt.AlignRight)

        self.hBoxLayout2 = FlowLayout()
        self.hBoxLayout2.setAnimation(200)
        self.hBoxLayout2.setSpacing(0)
        self.hBoxLayout2.setAlignment(Qt.AlignLeft)

        self.hBoxLayout3 = FlowLayout()
        self.hBoxLayout3.setAnimation(200)
        self.hBoxLayout3.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout3.setSpacing(10)
        self.hBoxLayout3.setAlignment(Qt.AlignLeft)

        self.hBoxLayout4 = FlowLayout()
        self.hBoxLayout4.setAnimation(200)
        self.hBoxLayout4.setSpacing(8)
        self.hBoxLayout4.setAlignment(Qt.AlignLeft)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addLayout(self.hBoxLayout1)

        if url:
            self.vBoxLayout.addSpacing(3)
            self.vBoxLayout.addLayout(self.hBoxLayout2)
        else:
            self.hBoxLayout2.deleteLater()
        if data:
            self.vBoxLayout.addSpacing(20)
            self.vBoxLayout.addLayout(self.hBoxLayout3)
            self.vBoxLayout.addSpacing(20)
        else:
            self.hBoxLayout3.deleteLater()
        self.vBoxLayout.addWidget(self.infoLabel)
        if tag:
            self.vBoxLayout.addSpacing(12)
            self.vBoxLayout.addLayout(self.hBoxLayout4)
        else:
            self.hBoxLayout4.deleteLater()

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.image, 0, Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

        if animation:
            self.animation = AnimationBase(self)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def backButtonClicked(self):
        self.hide()

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None, thread_pool: QThreadPool = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        @param thread_pool: 线程池
        """
        self.image.threadPool = thread_pool
        self.image.setImg(path, url)

    def setInfo(self, data: str):
        """
        设置信息
        @param data: 文本
        """
        self.infoLabel.setText(data)

    def addUrl(self, text: str, url: str, icon=None):
        """
        添加链接
        @param text: 文本
        @param url: 链接
        @param icon: 图标
        """
        button = HyperlinkButton(url, text, self)
        if icon:
            button.setIcon(icon)
        self.hBoxLayout2.addWidget(button)

    def addData(self, title: str, data: str | int):
        """
        添加数据
        @param title: 标题
        @param data: 数据
        """
        widget = StatisticsWidget(title, str(data), self)
        if self.hBoxLayout3.count() >= 1:
            seperator = VerticalSeparator(widget)
            seperator.setMinimumHeight(50)
            self.hBoxLayout3.addWidget(seperator)
        self.hBoxLayout3.addWidget(widget)

    def addTag(self, name: str):
        """
        添加标签
        @param name: 名称
        """
        self.tagButton = PillPushButton(name, self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)
        self.hBoxLayout4.addWidget(self.tagButton)


class SmallInfoCard(CardWidget):
    """
    普通信息卡片（搜索列表展示）
    """

    def __init__(self, parent=None, animation: bool = True):
        super().__init__(parent)
        self.setMinimumWidth(100)
        self.setFixedHeight(73)

        self.image = Image(self)

        self.titleLabel = BodyLabel(self)

        self.info = ["", "", "", ""]
        self.contentLabel1 = CaptionLabel(f"{self.info[0]}\n{self.info[1]}", self)
        self.contentLabel1.setTextColor("#606060", "#d2d2d2")
        self.contentLabel1.setAlignment(Qt.AlignLeft)

        self.contentLabel2 = CaptionLabel(f"{self.info[2]}\n{self.info[3]}", self)
        self.contentLabel2.setTextColor("#606060", "#d2d2d2")
        self.contentLabel2.setAlignment(Qt.AlignRight)

        self.mainButton = PushButton("", self)

        self.vBoxLayout1 = QVBoxLayout()

        self.vBoxLayout1.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout1.setSpacing(0)
        self.vBoxLayout1.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout1.addWidget(self.contentLabel1, 0, Qt.AlignVCenter)
        self.vBoxLayout1.setAlignment(Qt.AlignVCenter)

        self.vBoxLayout2 = QVBoxLayout()
        self.vBoxLayout2.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout2.setSpacing(0)
        self.vBoxLayout2.addWidget(self.contentLabel2, 0, Qt.AlignVCenter)
        self.vBoxLayout2.setAlignment(Qt.AlignRight)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(16)
        self.hBoxLayout.addWidget(self.image)
        self.hBoxLayout.addLayout(self.vBoxLayout1)
        self.hBoxLayout.addStretch(5)
        self.hBoxLayout.addLayout(self.vBoxLayout2)
        self.hBoxLayout.addStretch(0)
        self.hBoxLayout.addWidget(self.mainButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

        if animation:
            self.animation = AnimationBase(self)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None, thread_pool: QThreadPool = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        self.image.threadPool = thread_pool
        self.image.setImg(path, url)

    def setInfo(self, data: str, pos: int):
        """
        设置信息
        @param data: 文本
        @param pos: 位置：0 左上 1 左下 2 右上 3 右下
        """
        self.info[pos] = f.clearCharacters(data)
        self.contentLabel1.setText(f"{self.info[0]}\n{self.info[1]}".strip())
        self.contentLabel2.setText(f"{self.info[2]}\n{self.info[3]}".strip())

        self.contentLabel1.adjustSize()


class CardGroup(QWidget):
    """
    卡片组
    """

    @functools.singledispatchmethod
    def __init__(self, parent=None, animation: bool = True):
        super().__init__(parent=parent)
        self.setMinimumSize(0, 0)

        self.titleLabel = StrongBodyLabel(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = FixedExpandLayout()

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSpacing(0)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(2)

        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addLayout(self.cardLayout, 1)

        FluentStyleSheet.SETTING_CARD_GROUP.apply(self)
        self.titleLabel.adjustSize()

        if animation:
            self.animation = AnimationBase(self)

    @__init__.register
    def _(self, title: str = None, parent=None, animation: bool = True):
        self.__init__(parent, animation)
        if title:
            self.titleLabel.setText(title)

    def addWidget(self, card: QWidget):
        """
        添加卡片
        @param card: 卡片对象
        """
        card.setParent(self)
        card.show()
        self.cardLayout.addWidget(card)

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setTitleEnabled(self, enabled: bool):
        """
        是否展示标题
        @param enabled: 是否
        """
        self.titleLabel.setHidden(not enabled)

    def clearWidget(self):
        """
        自定义清空组件函数
        """
        self.cardLayout.clearWidget()


Log.info("组件库api初始化成功！")
