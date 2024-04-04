from .web_ui import *


class AddonThread(QThread):
    """
    多线程模块
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data

    def run(self):
        logging.info(f"MC资源管理器插件 {self.mode} 线程开始")

        logging.info(f"MC资源管理器插件 {self.mode} 线程结束")


class MinecraftPathSettingCard(SettingCard):
    """
    我的世界路径设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "Java版目录", f"当前路径：{setting.read('minecraftJavaPath')}", parent)
        self.button1 = PushButton("选择", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("设置Java版目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setAcceptDrops(True)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择要添加的Minecraft Java版目录", setting.read("minecraftJavaPath"))
        if get:
            self.saveSetting(get)

    def saveSetting(self, path: str):
        if isMinecraftPath(path):
            setting.save("minecraftJavaPath", path)
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"您选择的目录保存成功！\n{path}", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            self.contentLabel.setText(f"当前路径：{path}")
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "您选择的目录无效！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            self.contentLabel.setText(f"当前路径：{setting.read('minecraftJavaPath')}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if f.isDir(event.mimeData().urls()[0].toLocalFile()):
                    event.acceptProposedAction()
                    self.contentLabel.setText("拖拽到此卡片即可快速导入目录！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"当前路径：{setting.read('minecraftJavaPath')}")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            self.saveSetting(file)


class AddonSettingTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("设置")
        self.cardGroup1 = CardGroup("设置", self)

        self.cardGroup1.addWidget(MinecraftPathSettingCard(self))

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.backButton.setToolTip("返回管理页面")
        self.backButton.installEventFilter(ToolTipFilter(self.backButton, 1000))
        self.backButton.move(8, 8)
        self.backButton.setFixedSize(32, 32)

        self.vBoxLayout.addWidget(self.cardGroup1)

    def backButtonClicked(self):
        self.parent().page["管理"].loadPage()
        self.parent().showPage("管理")


class MinecraftVersionCard(SmallInfoCard):
    """
    我的世界版本信息卡片
    """

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.data = getPathGameInfo(path)

        self.mainButton.setText("管理")
        self.mainButton.setIcon(FIF.INFO)
        self.mainButton.setEnabled(False)

        self.setImg(getVersionImg(self.data["游戏版本"])[0], getVersionImg(self.data["游戏版本"])[1])

        self.setTitle(self.data["id"])
        data = self.data["游戏版本"]
        for j in self.data["加载器"]:
            data += f" | {j[0]} {j[1]}"
        self.setInfo(data, 0)

        self.mainButton.setEnabled(True)

    def mainButtonClicked(self):
        self.parent().parent().parent().parent().parent().page["版本"].setData(self.data)
        self.parent().parent().parent().parent().parent().showPage("版本")


class AddonManageTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("管理")

        self.cardGroup1 = CardGroup("管理", self)

        self.grayCard = GrayCard("设置", self)

        self.settingButton = PushButton("设置", self, FIF.SETTING)
        self.settingButton.clicked.connect(self.settingButtonClicked)
        self.settingButton.setToolTip("打开插件设置")
        self.settingButton.installEventFilter(ToolTipFilter(self.settingButton, 1000))

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadPage)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.grayCard.addWidget(self.settingButton)
        self.grayCard.addWidget(self.reloadButton)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.grayCard)

        self.loadPage()

    def settingButtonClicked(self):
        self.parent().showPage("设置")

    def loadPage(self):
        self.cardGroup1.clearWidget()

        if isMinecraftPath(setting.read("minecraftJavaPath")) == "version":
            versionList = [setting.read("minecraftJavaPath")]
        elif isMinecraftPath(setting.read("minecraftJavaPath")) == "minecraft":
            versionList = [i for i in f.walkDir(f.pathJoin(setting.read("minecraftJavaPath"), "versions"), 1) if isMinecraftPath(i)]
        else:
            return
        for i in versionList:
            self.smallInfoCard = MinecraftVersionCard(i, self)
            self.cardGroup1.addWidget(self.smallInfoCard)

    def thread1_2(self, msg):
        if not msg:
            self.smallInfoCard.setInfo(f"目录{setting.read('minecraftJavaPath')}的Minecraft版本信息读取失败！", 0)


class VersionManageTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("版本")
        self.data = []

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.backButton.setToolTip("返回管理页面")
        self.backButton.installEventFilter(ToolTipFilter(self.backButton, 1000))
        self.backButton.move(8, 8)
        self.backButton.setFixedSize(32, 32)

        self.grayCard = GrayCard("功能", self)

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadPage)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.grayCard.addWidget(self.reloadButton)

        self.bigInfoCard = BigInfoCard(self)
        self.cardGroup = CardGroup("管理", self)
        self.label = StrongBodyLabel("截图", self)
        self.flipView = HorizontalFlipView(self)
        self.pager = HorizontalPipsPager(self)

        self.vBoxLayout.addWidget(self.bigInfoCard)
        self.vBoxLayout.addWidget(self.grayCard)
        self.vBoxLayout.addWidget(self.cardGroup)
        self.vBoxLayout.addWidget(self.label)
        self.vBoxLayout.addWidget(self.flipView)
        self.vBoxLayout.addWidget(self.pager)

    def backButtonClicked(self):
        self.parent().page["管理"].loadPage()
        self.parent().showPage("管理")

    def setData(self, data):
        if data == self.data:
            return
        else:
            self.loadPage(data)

    def loadPage(self, data=None):
        if data:
            self.data = data

        if self.data["加载器"] and isRelease(self.data["游戏版本"]):
            for i in FILE_PATH.values():
                f.makeDir(f.pathJoin(self.data["路径"], i))

        self.bigInfoCard.deleteLater()
        self.bigInfoCard = BigInfoCard(self, url=False)
        self.bigInfoCard.setTitle(self.data["id"])
        self.bigInfoCard.setImg(getVersionImg(self.data["游戏版本"])[0], getVersionImg(self.data["游戏版本"])[1])
        self.bigInfoCard.addData("游戏版本", self.data["游戏版本"])
        self.bigInfoCard.setInfo(f"该版本为Minecraft Java版{"正式版" if isRelease(self.data["游戏版本"]) else "测试版"}，{"已安装" if self.data["加载器"] else "未安装"}模组加载器，{"支持" if self.data["加载器"] and isRelease(self.data["游戏版本"]) else "不支持"}本程序的模组管理")
        for i in self.data["加载器"]:
            self.bigInfoCard.addData(i[1], i[0])
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.setText("打开")
        self.bigInfoCard.mainButton.setIcon(FIF.FOLDER)
        self.bigInfoCard.mainButton.clicked.connect(lambda: f.showFile(self.data["路径"]))
        self.vBoxLayout.insertWidget(0, self.bigInfoCard)

        self.flipView.deleteLater()
        self.pager.deleteLater()
        self.flipView = HorizontalFlipView(self)
        self.flipView.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        img = [i for i in f.walkFile(f.pathJoin(self.data["路径"], "screenshots"), 1) if i.endswith(".png") or i.endswith(".jpg")]
        self.flipView.addImages(img if len(img) <= 15 else img[:15])
        self.pager = HorizontalPipsPager(self)
        self.pager.setPageNumber(self.flipView.count())
        self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
        self.pager.setVisibleNumber(self.flipView.count() if self.flipView.count() <= 25 else 25)
        self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)
        self.label.setHidden(not bool(img))
        self.flipView.setHidden(not bool(img))
        self.pager.setHidden(not bool(img))

        self.vBoxLayout.insertWidget(7, self.flipView)
        self.vBoxLayout.insertWidget(8, self.pager, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)


class AddonPage(ChangeableTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.GAME)
        self.setObjectName("MC资源管理器")
        self.isInit = False

    def showEvent(self, QShowEvent):
        if not self.isInit:
            self.isInit = True

            self.addonManageTab = AddonManageTab(self)
            self.addonSettingTab = AddonSettingTab(self)
            self.versionManageTab = VersionManageTab(self)

            self.addPage(self.addonManageTab)
            self.addPage(self.addonSettingTab)
            self.addPage(self.versionManageTab)
            self.showPage("管理")
