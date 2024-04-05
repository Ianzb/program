from .web_ui import *


class AddonThread(QThread, SignalBase):
    """
    多线程模块
    """

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


class VersionCard(SmallInfoCard):
    """
    我的世界版本信息卡片
    """

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.data = getPathGameInfo(path)

        self.mainButton.setText("管理")
        self.mainButton.setIcon(FIF.INFO)

        self.setImg(getVersionImg(self.data["游戏版本"])[0], getVersionImg(self.data["游戏版本"])[1])

        self.setTitle(self.data["id"])
        data = self.data["游戏版本"]
        for j in self.data["加载器"]:
            data += f" | {j[0]} {j[1]}"
        self.setInfo(data, 0)

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
            self.smallInfoCard = VersionCard(i, self)
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

        self.grayCard = GrayCard("管理", self)

        self.saveButton = PushButton("存档", self, FIF.SAVE)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.saveButton.setToolTip("存档管理")
        self.saveButton.installEventFilter(ToolTipFilter(self.saveButton, 1000))

        self.modButton = PushButton("模组", self, FIF.APPLICATION)
        self.modButton.clicked.connect(self.modButtonClicked)
        self.modButton.setToolTip("模组管理")
        self.modButton.installEventFilter(ToolTipFilter(self.modButton, 1000))

        self.resourcePackButton = PushButton("资源包", self, FIF.TILES)
        self.resourcePackButton.clicked.connect(self.resourcePackButtonClicked)
        self.resourcePackButton.setToolTip("资源包管理")
        self.resourcePackButton.installEventFilter(ToolTipFilter(self.resourcePackButton, 1000))

        self.shaderPackButton = PushButton("光影包", self, FIF.BRIGHTNESS)
        self.shaderPackButton.clicked.connect(self.shaderPackButtonClicked)
        self.shaderPackButton.setToolTip("光影包管理")
        self.shaderPackButton.installEventFilter(ToolTipFilter(self.shaderPackButton, 1000))

        self.screenshotButton = PushButton("截图", self, FIF.PHOTO)
        self.screenshotButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], "screenshots")))
        self.screenshotButton.setToolTip("截图管理")
        self.screenshotButton.installEventFilter(ToolTipFilter(self.screenshotButton, 1000))

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadPage)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.grayCard.addWidget(self.saveButton)
        self.grayCard.addWidget(self.modButton)
        self.grayCard.addWidget(self.resourcePackButton)
        self.grayCard.addWidget(self.shaderPackButton)
        self.grayCard.addWidget(self.screenshotButton)
        self.grayCard.addWidget(self.reloadButton)

        self.bigInfoCard = BigInfoCard(self)
        self.label = StrongBodyLabel("截图", self)
        self.flipView = HorizontalFlipView(self)
        self.pager = HorizontalPipsPager(self)

        self.vBoxLayout.addWidget(self.bigInfoCard)
        self.vBoxLayout.addWidget(self.grayCard)
        self.vBoxLayout.addWidget(self.label)
        self.vBoxLayout.addWidget(self.flipView)
        self.vBoxLayout.addWidget(self.pager)

    def setData(self, data):
        if data == self.data:
            return
        else:
            self.loadPage(data)

    def loadPage(self, data=None):
        if data:
            self.data = data

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

        self.vBoxLayout.insertWidget(6, self.flipView)
        self.vBoxLayout.insertWidget(7, self.pager, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.saveButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], "saves")))
        self.modButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], "mods")))
        self.resourcePackButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], "resourcepacks")))
        self.shaderPackButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], "shaderpacks")))
        self.screenshotButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], "screenshots")))

    def backButtonClicked(self):
        self.parent().page["管理"].loadPage()
        self.parent().showPage("管理")

    def saveButtonClicked(self):
        self.parent().page["存档"].loadPage(self.data)
        self.parent().showPage("存档")

    def modButtonClicked(self):
        self.parent().page["模组"].loadPage(self.data)
        self.parent().showPage("模组")

    def resourcePackButtonClicked(self):
        self.parent().page["资源包"].loadPage(self.data)
        self.parent().showPage("资源包")

    def shaderPackButtonClicked(self):
        self.parent().page["光影包"].loadPage(self.data)
        self.parent().showPage("光影包")


class ResourceManageTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.backButton.setToolTip("返回版本页面")
        self.backButton.installEventFilter(ToolTipFilter(self.backButton, 1000))
        self.backButton.move(8, 8)
        self.backButton.setFixedSize(32, 32)

        self.grayCard = GrayCard("管理", self)

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadPage)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.grayCard.addWidget(self.reloadButton)

        self.vBoxLayout.addWidget(self.grayCard)

    def backButtonClicked(self):
        self.parent().page["版本"].loadPage()
        self.parent().showPage("版本")

    def setData(self, data):
        if data == self.data:
            return
        else:
            self.loadPage(data)

    def loadPage(self, data=None):
        if data:
            self.data = data


class SaveCard(SmallInfoCard):
    """
    存档信息卡片
    """

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.data = getSaveInfo(path)

        self.mainButton.setText("打开")
        self.mainButton.setIcon(FIF.FOLDER)

        if self.data["封面"]:
            self.setImg(self.data["封面"])

        self.setTitle(self.data["名称"])
        self.setInfo(f"{self.data["游戏模式"]} | {self.data["游戏难度"]}", 0)
        self.setInfo(self.data["最近游玩"], 1)

        self.hBoxLayout.insertWidget(3, CopyTextButton(self.data["种子"], "种子", self))
        self.hBoxLayout.insertWidget(4, CopyTextButton(self.data["路径"], "路径", self))
        self.hBoxLayout.insertSpacing(4, -24)
        self.hBoxLayout.insertSpacing(5, 16)

    def mainButtonClicked(self):
        f.showFile(self.path)


class SaveManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("存档")

        self.cardGroup = CardGroup("存档列表", self)
        self.vBoxLayout.insertWidget(0, self.cardGroup, 0)

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], "saves")))
        self.openButton.setToolTip("打开存档目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

    def loadPage(self, data=None):
        if data:
            self.data = data
        self.cardGroup.clearWidget()

        savelist = [i for i in f.walkDir(f.pathJoin(self.data["路径"], "saves"), 1) if f.existPath(f.pathJoin(i, "level.dat"))]
        for i in savelist:
            self.saveCard = SaveCard(i, self)
            self.cardGroup.addWidget(self.saveCard)
        self.cardGroup.setTitle(f"存档列表（{len(savelist)}个）")


class ModManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("模组")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], "mods")))
        self.openButton.setToolTip("打开模组目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

    def loadPage(self, data=None):
        if data:
            self.data = data


class ResourcePackManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源包")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], "resourcepacks")))
        self.openButton.setToolTip("打开资源包目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

    def loadPage(self, data=None):
        if data:
            self.data = data


class ShaderPackManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("光影包")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], "shaderpacks")))
        self.openButton.setToolTip("打开光影包目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

    def loadPage(self, data=None):
        if data:
            self.data = data


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
            self.saveManageTab = SaveManageTab(self)
            self.modManageTab = ModManageTab(self)
            self.resourcePackManageTab = ResourcePackManageTab(self)
            self.shaderPackManageTab = ShaderPackManageTab(self)

            self.addPage(self.addonManageTab)
            self.addPage(self.addonSettingTab)
            self.addPage(self.versionManageTab)
            self.addPage(self.saveManageTab)
            self.addPage(self.modManageTab)
            self.addPage(self.resourcePackManageTab)
            self.addPage(self.shaderPackManageTab)
            self.showPage("管理")
