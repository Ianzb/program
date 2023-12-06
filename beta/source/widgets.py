from .functions import *


# UI多线程


class NewThread(QThread):
    """
    多线程模块
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data
        self.isCancel = False

    def run(self):
        if self.mode == "更新运行库":
            for i in range(len(program.REQUIRE_LIB)):
                self.signalDict.emit({"名称": program.REQUIRE_LIB[i], "序号": i, "完成": False})
                f.pipUpdate(program.REQUIRE_LIB[i])
            self.signalDict.emit({"完成": True})
        if self.mode == "检查更新":
            try:
                data = f.getNewestVersion()
            except Exception as ex:
                self.signalDict.emit({"更新": False})
                return
            if f.compareVersion(data, program.PROGRAM_VERSION) == program.PROGRAM_VERSION:
                self.signalDict.emit({"更新": False})
            else:
                self.signalDict.emit({"更新": True, "版本": data})
        if self.mode == "立刻更新":
            try:
                data = f.getNewestVersion()
            except:
                self.signalDict.emit({"更新": False})
                return
            if f.compareVersion(data, program.PROGRAM_VERSION) == program.PROGRAM_VERSION:
                self.signalDict.emit({"更新": False})
                return
            response = requests.get(program.UPDATE_URL, headers=program.REQUEST_HEADER, stream=True).text
            data = json.loads(response)["list"]
            for i in range(len(data)):
                self.signalDict.emit({"更新": True, "数量": len(data), "完成": False, "名称": data[i], "序号": i})
                f.downloadFile(f.urlJoin(program.UPDATE_URL, data[i]), f.pathJoin(program.PROGRAM_PATH, data[i]))
            self.signalDict.emit({"更新": True, "完成": True})
            logging.debug(f"更新{data}成功")
        if self.mode == "一键整理+清理":
            try:
                Thread(lambda: f.clearRubbish())
                Thread(lambda: f.clearSystemCache())
                f.sortDir(program.DESKTOP_PATH, setting.read("sortPath"))
                if setting.read("wechatPath") != "":
                    f.sortWechatFiles()
                for i in list(f.SORT_FILE_DIR.keys()) + ["文件夹"]:
                    f.clearFile(f.pathJoin(setting.read("sortPath"), i))
                f.clearFile(setting.read("sortPath"))
                self.signalBool.emit(True)
                logging.debug("一键整理成功")
            except Exception as ex:
                self.signalBool.emit(False)
                logging.warning("一键整理失败")
        if self.mode == "重启文件资源管理器":
            f.cmd("taskkill /f /im explorer.exe", True)
            self.signalStr.emit("完成")
            f.cmd("start C:/windows/explorer.exe", True)
            logging.debug("重启文件资源管理器")
        if self.mode == "Minecraft最新版本":
            self.signalStr.emit(f.getMC())
        if self.mode == "下载图片":
            if not f.existPath(self.data[1]):
                f.downloadFile(self.data[0], self.data[1])
            self.signalBool.emit(True)
        if self.mode == "清理程序缓存":
            f.clearProgramCache()
            self.signalBool.emit(True)
        if self.mode == "搜索应用":
            try:
                data = f.searchSoftware(self.data[0], self.data[1])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "下载文件":
            path = f.pathJoin(setting.read("downloadPath"), self.data[0])
            if f.existPath(path):
                i = 1
                while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))):
                    i = i + 1
                path = f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))
            logging.debug(f"开始下载文件{path}")
            path += ".zb.appstore.downloading"
            url = self.data[1]
            self.signalStr.emit(path)
            response = requests.get(url, headers=program.REQUEST_HEADER, stream=True)
            size = 0
            file_size = int(response.headers["content-length"])
            if response.status_code == 200:
                with open(path, "wb") as file:
                    for data in response.iter_content(256):
                        if self.isCancel:
                            self.signalBool.emit(True)
                            return
                        file.write(data)
                        size += len(data)
                        self.signalInt.emit(int(100 * size / file_size))
            logging.debug(f"文件{path}下载成功")

    def cancel(self):
        logging.debug("取消下载")
        self.isCancel = True


class BasicPage(ScrollArea):
    """
    页面模板（优化样式的滚动区域）
    """
    title = ""
    subtitle = ""
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.title)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea {background-color: rgba(0,0,0,0); border: none}")

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


class ToolBar(QWidget):
    """
    页面顶端工具栏
    """

    def __init__(self, title: str, subtitle: str, parent: QWidget = None):
        """
        @param title: 主标题
        @param subtitle: 副标题
        """
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


class StatisticsWidget(QWidget):
    """
    两行信息组件
    """

    def __init__(self, title: str, value: str, parent: QWidget = None):
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

        setFont(self.valueLabel, 18, QFont.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class Image(QLabel):
    """
    图片组件（可实时下载）
    """

    @functools.singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.setFixedSize(48, 48)
        self.setScaledContents(True)
        self.loading = False

    @__init__.register
    def _(self, path: str, url: str = None, parent: QWidget = None):
        """
        @param path: 路径
        @param url: 链接
        """
        self.__init__(parent)
        if path:
            self.setImg(path, url)

    def thread1(self, msg):
        if msg:
            self.loading = False
            self.setPixmap(QPixmap(self.path))

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        if url:
            self.loading = True
            self.path = program.cache(path)
            self.url = url
            self.thread = NewThread("下载图片", [self.url, self.path])
            self.thread.signalBool.connect(self.thread1)
            self.thread.start()
        else:
            self.loading = False
            self.setPixmap(QPixmap(path))


class DisplayCard(ElevatedCardWidget):
    """
    大图片卡片
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedSize(168, 176)
        self.setStyleSheet("QLabel {background-color: rgba(0,0,0,0); border: none;}")

        self.widget = Image(self)

        self.label = CaptionLabel(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.widget, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

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
        self.label.setText(text)

    def setDisplay(self, widget: QWidget):
        """
        设置展示组件
        @param widget: 组件
        """
        self.widget = widget
        self.vBoxLayout.replaceWidget(self.vBoxLayout.itemAt(1).widget(), self.widget)


class GrayCard(QWidget):
    """
    灰色背景组件卡片
    """

    def __init__(self, title: str = None, parent: QWidget = None, alignment=Qt.AlignLeft):
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

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignTop)

        self.hBoxLayout = QHBoxLayout(self.card)
        self.hBoxLayout.setAlignment(alignment)
        self.hBoxLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(12, 12, 12, 12)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
            self.card.setStyleSheet("QFrame {background-color: rgba(25,25,25,0.5); border:1px solid rgba(20,20,20,0.15); border-radius: 10px}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")
            self.card.setStyleSheet("QFrame {background-color: rgba(175,175,175,0.1); border:1px solid rgba(150,150,150,0.15); border-radius: 10px}")

    def addWidget(self, widget: object, spacing=0, alignment=Qt.AlignTop):
        """
        添加组件
        @param widget: 组件
        @param spacing: 间隔
        @param alignment: 对齐方式
        """
        self.hBoxLayout.addWidget(widget, alignment=alignment)
        self.hBoxLayout.addSpacing(spacing)


class BigInfoCard(CardWidget):
    """
    详细信息卡片（资源主页展示）
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setMinimumWidth(0)

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.move(8, 8)
        self.backButton.setMaximumSize(32, 32)
        self.backButton.clicked.connect(self.backButtonClicked)

        self.image = Image(self)

        self.titleLabel = TitleLabel(self)

        self.mainButton = PrimaryPushButton("下载", self)
        self.mainButton.clicked.connect(self.mainButtonClicked)
        self.mainButton.setFixedWidth(160)

        self.infoLabel = BodyLabel(self)
        self.infoLabel.setWordWrap(True)

        self.hBoxLayout1 = QHBoxLayout()
        self.hBoxLayout1.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout1.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        self.hBoxLayout1.addWidget(self.mainButton, 0, Qt.AlignRight)

        self.hBoxLayout2 = QHBoxLayout()
        self.hBoxLayout2.setSpacing(16)
        self.hBoxLayout2.setAlignment(Qt.AlignLeft)

        self.hBoxLayout3 = QHBoxLayout()
        self.hBoxLayout3.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout3.setSpacing(10)
        self.hBoxLayout3.setAlignment(Qt.AlignLeft)

        self.hBoxLayout4 = QHBoxLayout()
        self.hBoxLayout4.setSpacing(8)
        self.hBoxLayout4.setAlignment(Qt.AlignLeft)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addLayout(self.hBoxLayout1)
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addLayout(self.hBoxLayout2)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.hBoxLayout3)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.infoLabel)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addLayout(self.hBoxLayout4)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.image)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def backButtonClicked(self):
        self.hide()

    def mainButtonClicked(self):
        pass

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        self.image.setImg(path, url)

    def setInfo(self, data: str):
        """
        设置信息
        @param data: 文本
        """
        self.infoLabel.setText(data)

    def addUrl(self, text: str, url: str):
        """
        添加链接
        @param text: 文本
        @param url: 链接
        """
        self.hBoxLayout2.addWidget(HyperlinkLabel(QUrl(url), text, self), alignment=Qt.AlignLeft)

    def addData(self, title: str, data: str | int):
        """
        添加数据
        @param title: 标题
        @param data: 数据
        """
        if self.hBoxLayout3.count() >= 1:
            self.hBoxLayout3.addWidget(VerticalSeparator(self))
        self.hBoxLayout3.addWidget(StatisticsWidget(title, data, self))

    def addTag(self, name: str):
        """
        添加标签
        @param name: 名称
        """
        self.tagButton = PillPushButton(name, self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)
        self.hBoxLayout4.addWidget(self.tagButton, 0, Qt.AlignLeft)


class SmallInfoCard(CardWidget):
    """
    普通信息卡片（搜索列表展示）
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setMinimumWidth(0)
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

        self.mainButton = PushButton("进入", self, FIF.CHEVRON_RIGHT)
        self.mainButton.clicked.connect(self.mainButtonClicked)

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

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def mainButtonClicked(self):
        pass

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        self.image.setImg(path, url)

    def setInfo(self, data: str, pos: int):
        """
        设置信息
        @param data: 文本
        @param pos: 位置：0 左上 1 左下 2 右上 3 右下
        """
        self.info[pos] = data
        self.contentLabel1.setText(f"{self.info[0]}\n{self.info[1]}")
        self.contentLabel2.setText(f"{self.info[2]}\n{self.info[3]}")

        self.contentLabel1.adjustSize()


class CardGroup(QWidget):
    """
    卡片组
    """

    @functools.singledispatchmethod
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumSize(0, 0)

        self.titleLabel = StrongBodyLabel(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = ExpandLayout()

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

    @__init__.register
    def _(self, title: str = None, parent=None):
        self.__init__(parent)
        if title:
            self.titleLabel.setText(title)

    def addWidget(self, card: QWidget):
        self.card = card
        self.card.setParent(self)
        self.cardLayout.addWidget(self.card)

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


logging.debug("widgets.py初始化成功")
