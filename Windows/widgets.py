from functions import *


class BasicPage(ScrollArea):
    """
    页面模板（优化样式的滚动区域）
    """
    title = ""
    subtitle = ""
    signalStr = pyqtSignal(str)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.title)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea {background-color: rgba(0,0,0,0); border: none; border-top-left-radius: 10px;}")

        self.toolBar = ToolBar(self.title, self.subtitle, self)

        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.view = QWidget(self)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setWidget(self.view)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)


class BasicTabPage(BasicPage):
    """
    有多标签页的页面模板
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.toolBar.deleteLater()

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.pivot = Pivot(self)
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignHCenter)

        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.vBoxLayout.addWidget(self.stackedWidget)

    def addPage(self, widget, name, icon=None):
        widget.setObjectName(name)
        widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(name, name, lambda: self.stackedWidget.setCurrentWidget(widget), icon)
        if self.stackedWidget.count() == 1:
            self.stackedWidget.setCurrentWidget(widget)
            self.pivot.setCurrentItem(widget.objectName())

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())


class BasicTab(BasicPage):
    """
    有多标签页模板
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.toolBar.deleteLater()
        self.setViewportMargins(0, 0, 0, 0)


class StatisticsWidget(QWidget):
    """
    两行信息组件
    """

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)
        self.valueLabel = BodyLabel(value, self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignBottom)

        setFont(self.valueLabel, 18, QFont.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class WebImage(QLabel):
    def __init__(self, img: str, link: str = None, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(48, 48)
        self.setScaledContents(True)
        if link:
            self.img = program.cache(img)
            self.link = link
            self.thread = NewThread("下载图片", [self.link, self.img])
            self.thread.signalBool.connect(self.thread1)
            self.thread.start()
        else:
            self.setPixmap(QPixmap(img))

    def thread1(self, msg):
        if msg:
            self.setPixmap(QPixmap(self.img))


class PhotoCard(ElevatedCardWidget):
    """
    大图片卡片
    """

    def __init__(self, img: str, name: str = "", parent=None, imageSize: int = 68, widgetSize: list | tuple = (168, 176), link: str = ""):
        super().__init__(parent)
        self.imageSize = imageSize

        self.setFixedSize(widgetSize[0], widgetSize[1])
        self.setStyleSheet("QLabel {background-color: rgba(0,0,0,0); border: none;}")

        self.image = WebImage(img, link, self)
        self.image.setMinimumSize(self.imageSize, self.imageSize)

        self.label = CaptionLabel(name, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)
        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def mousePressEvent(self, event):
        self.clickedFunction()

    def clickedFunction(self):
        pass

    def connect(self, functions):
        self.clickedFunction = functions

    def setText(self, data):
        self.label.setText(data)

    def setImage(self, img):
        self.iconWidget.setImage(img)
        self.iconWidget.scaledToHeight(self.imageSize)


class ToolBar(QWidget):
    """
    页面顶端工具栏
    """

    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(90)

        self.titleLabel = TitleLabel(title, self)
        self.subtitleLabel = CaptionLabel(subtitle, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 22, 36, 12)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")


class GrayCard(QWidget):
    """
    灰色背景组件卡片
    """

    def __init__(self, title: str, parent=None, alignment=Qt.AlignLeft):
        super().__init__(parent=parent)

        self.titleLabel = StrongBodyLabel(title, self)

        self.card = QFrame(self)
        self.card.setObjectName("卡片")

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self.card)

        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.hBoxLayout.setAlignment(alignment)

        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.hBoxLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.vBoxLayout.setSpacing(12)
        self.hBoxLayout.setSpacing(0)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setContentsMargins(12, 12, 12, 12)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignTop)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def addWidget(self, widget: object, spacing=0, alignment=Qt.AlignTop):
        self.hBoxLayout.addWidget(widget, alignment=alignment)
        self.hBoxLayout.addSpacing(spacing)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
            self.card.setStyleSheet("QWidget {background-color: rgba(25,25,25,0.5); border:1px solid rgba(20,20,20,0.15); border-radius: 10px}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")
            self.card.setStyleSheet("QWidget {background-color: rgba(175,175,175,0.1); border:1px solid rgba(150,150,150,0.15); border-radius: 10px}")


class BigInfoCard(CardWidget, QWidget):
    """
    详细信息卡片（资源主页展示）
    """

    def __init__(self, title: str, img: str, info: str, link: str = "", parent=None):
        super().__init__(parent)
        self.setMinimumWidth(0)
        self.setMaximumHeight(300)

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.move(8, 8)
        self.backButton.setMaximumSize(32, 32)
        self.backButton.clicked.connect(self.buttonClickedBack)

        self.picLabel = WebImage(img, link)

        self.titleLabel = TitleLabel(title, self)

        self.mainButton = PrimaryPushButton("下载", self)
        self.mainButton.clicked.connect(self.buttonClickedMain)
        self.mainButton.setFixedWidth(160)

        self.infoLabel = BodyLabel(info, self)
        self.infoLabel.setWordWrap(True)

        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()

        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.titleLabel)
        self.topLayout.addWidget(self.mainButton, 0, Qt.AlignRight)

        self.statisticsLayout.setContentsMargins(0, 0, 0, 0)
        self.statisticsLayout.setSpacing(10)
        self.statisticsLayout.setAlignment(Qt.AlignLeft)

        self.hBoxLayout2 = QHBoxLayout()
        self.hBoxLayout2.setSpacing(16)
        self.hBoxLayout2.setAlignment(Qt.AlignLeft)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addLayout(self.topLayout)
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addLayout(self.hBoxLayout2)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.statisticsLayout)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.infoLabel)

        self.hBoxLayout1 = QHBoxLayout(self)
        self.hBoxLayout1.setSpacing(30)
        self.hBoxLayout1.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout1.addWidget(self.picLabel)
        self.hBoxLayout1.addLayout(self.vBoxLayout)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def addUrl(self, name: str, url: str):
        self.hBoxLayout2.addWidget(HyperlinkLabel(QUrl(url), name, self), alignment=Qt.AlignLeft)

    def addInfo(self, name: str, data: str | int):
        if self.statisticsLayout.count() >= 1:
            self.statisticsLayout.addWidget(VerticalSeparator(self))
        self.statisticsLayout.addWidget(StatisticsWidget(name, data, self))

    def buttonClickedBack(self):
        self.hide()

    def buttonClickedMain(self):
        pass


class NormalInfoCard(CardWidget):
    """
    普通信息卡片（搜索列表展示）
    """

    def __init__(self, title: str, img: str, info: list | tuple, link: str = "", parent=None):
        super().__init__(parent)
        self.setMinimumWidth(0)
        self.setFixedHeight(73)

        self.picLabel = WebImage(img, link)

        self.titleLabel = BodyLabel(title, self)
        self.contentLabel1 = CaptionLabel(f"{info[0]}\n{info[1]}", self)
        self.contentLabel2 = CaptionLabel(f"{info[2]}\n{info[3]}", self)
        self.contentLabel1.setTextColor("#606060", "#d2d2d2")
        self.contentLabel2.setTextColor("#606060", "#d2d2d2")

        self.mainButton = PushButton("进入", self, FIF.CHEVRON_RIGHT)
        self.mainButton.clicked.connect(self.buttonClickedMain)

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
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.picLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout1)
        self.hBoxLayout.addStretch(5)
        self.hBoxLayout.addLayout(self.vBoxLayout2)
        self.hBoxLayout.addStretch(0)
        self.hBoxLayout.addWidget(self.mainButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def buttonClickedMain(self):
        pass
