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
        if self.mode == "搜索资源":
            try:
                data = mc.searchMod(self.data[0], self.data[1], self.data[2], type=self.data[3])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得游戏版本列表":
            try:
                self.signalList.emit(mc.getVersionList())
            except:
                self.signalBool.emit(False)
        elif self.mode == "获得资源信息":
            try:
                data = mc.getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得资源文件":
            try:
                data = mc.getModFile(self.data[0], self.data[1], self.data[2], self.data[3])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得单独模组信息":
            try:
                data = mc.getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得文件信息":
            try:
                try:
                    data1 = mc.getInfoFromHash(self.data)
                except:
                    data1 = []
                try:
                    data2 = mc.getInfoFromHash(self.data, source="Modrinth")
                except:
                    data2 = []
                if not data1 and not data2:
                    self.signalBool.emit(False)
                self.signalList.emit(data1 + data2)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "从文件获得模组信息":
            try:
                list = [i["模组id"] for i in self.data]
                try:
                    data2 = mc.getModsInfo([i for i in list if isinstance(i, int)])
                except:
                    data2 = []
                try:
                    data1 = mc.getModsInfo([i for i in list if isinstance(i, str)], source="Modrinth")
                except:
                    data1 = []
                if not data1 and not data2:
                    self.signalBool.emit(False)
                self.signalList.emit(data1 + data2)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得模组最新版本":
            try:
                if self.data[3] == "Modrinth":
                    self.signalInt.emit(0)
                    response = mc.getInfoFromHash(self.data[0], self.data[3])
                    self.signalInt.emit(50)
                    data = mc.getNewestFromHash(self.data[0], self.data[1], self.data[2], self.data[3])
                elif self.data[3] == "CurseForge":
                    self.signalInt.emit(0)
                    response = mc.getInfoFromHash(self.data[0], self.data[3])
                    data = []
                    self.signalInt.emit(int(100 / (len(response) + 1)))
                    for i in range(len(response)):
                        try:
                            data1 = mc.getModFile(response[i]["模组id"], self.data[1], self.data[2], self.data[3])
                            data.append(data1[self.data[1]][0])
                        except:
                            pass
                        self.signalInt.emit(int(100 * (i + 2) / (len(response) + 1)))
                self.signalInt.emit(100)
                self.signalDict.emit({"old": response, "new": data})
            except:
                self.signalBool.emit(False)
        logging.info(f"MC资源管理器插件 {self.mode} 线程结束")


class MinecraftPathSettingCard(SettingCard):
    """
    我的世界路径设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "Java版目录", f"当前路径：{setting.read("minecraftJavaPath")}", parent)
        self.button1 = PushButton("选择", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("设置Java版目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setAcceptDrops(True)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择要添加的Minecraft Java版目录", setting.read("minecraftJavaPath"))
        if get:
            self.saveSetting(get)

    def saveSetting(self, path: str):
        if mc.isMinecraftPath(path):
            setting.save("minecraftJavaPath", path)
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"您选择的目录保存成功！\n{path}", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            self.contentLabel.setText(f"当前路径：{path}")
            mc.FILE_DOWNLOAD_PATH = setting.read("minecraftJavaPath")
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "您选择的目录无效！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            self.contentLabel.setText(f"当前路径：{setting.read("minecraftJavaPath")}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if f.isDir(event.mimeData().urls()[0].toLocalFile()):
                    event.acceptProposedAction()
                    self.contentLabel.setText("拖拽到此卡片即可快速导入目录！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"当前路径：{setting.read("minecraftJavaPath")}")

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
        self.data = mc.getPathGameInfo(path)

        self.mainButton.setText("管理")
        self.mainButton.setIcon(FIF.INFO)

        self.setImg(mc.getVersionImg(self.data["游戏版本"])[0], mc.getVersionImg(self.data["游戏版本"])[1])

        self.setTitle(self.data["id"])
        data = self.data["游戏版本"]
        for j in self.data["加载器"]:
            data += f" | {j[0]} {j[1]}"
        self.setInfo(data, 0)

    def mainButtonClicked(self):
        self.parent().parent().parent().parent().parent().page["版本"].setData(self.data)
        self.parent().parent().parent().parent().parent().showPage("版本")


class VersionsManageTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("管理")

        self.cardGroup1 = CardGroup("管理", self)

        self.grayCard1 = GrayCard("设置", self)

        self.settingButton = PushButton("设置", self, FIF.SETTING)
        self.settingButton.clicked.connect(self.settingButtonClicked)
        self.settingButton.setToolTip("打开插件设置")
        self.settingButton.installEventFilter(ToolTipFilter(self.settingButton, 1000))

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadPage)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.grayCard1.addWidget(self.settingButton)
        self.grayCard1.addWidget(self.reloadButton)

        self.grayCard2 = GrayCard("资源下载", self)

        self.downloadButton = PrimaryPushButton("资源下载", self, FIF.DOWNLOAD)
        self.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.downloadButton.setToolTip("下载资源")
        self.downloadButton.installEventFilter(ToolTipFilter(self.downloadButton, 1000))

        self.grayCard2.addWidget(self.downloadButton)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.grayCard1)
        self.vBoxLayout.addWidget(self.grayCard2)

        self.loadPage()

    def settingButtonClicked(self):
        self.parent().showPage("设置")

    def downloadButtonClicked(self):
        self.parent().showPage("搜索")

    def loadPage(self):
        mc.FILE_DOWNLOAD_PATH = setting.read("minecraftJavaPath")
        self.cardGroup1.clearWidget()

        if mc.isMinecraftPath(setting.read("minecraftJavaPath")) == "version":
            versionList = [setting.read("minecraftJavaPath")]
        elif mc.isMinecraftPath(setting.read("minecraftJavaPath")) == "minecraft":
            versionList = [i for i in f.walkDir(f.pathJoin(setting.read("minecraftJavaPath"), "versions"), 1) if mc.isMinecraftPath(i)]
        else:
            return
        for i in versionList:
            self.smallInfoCard = VersionCard(i, self)
            self.cardGroup1.addWidget(self.smallInfoCard)

    def thread1_2(self, msg):
        if not msg:
            self.smallInfoCard.setInfo(f"目录{setting.read("minecraftJavaPath")}的Minecraft版本信息读取失败！", 0)


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
        self.screenshotButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["截图"])))
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
        mc.FILE_DOWNLOAD_PATH = data["路径"]
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
        self.bigInfoCard.setImg(mc.getVersionImg(self.data["游戏版本"])[0], mc.getVersionImg(self.data["游戏版本"])[1])
        self.bigInfoCard.addData("游戏版本", self.data["游戏版本"])
        self.bigInfoCard.setInfo(f"该版本为Minecraft Java版{"正式版" if mc.isRelease(self.data["游戏版本"]) else "测试版"}，{"已安装" if self.data["加载器"] else "未安装"}模组加载器！")
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
        img = [i for i in f.walkFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["截图"]), 1) if i.endswith(".png") or i.endswith(".jpg")]
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
        self.vBoxLayout.insertWidget(7, self.pager, 0, Qt.AlignCenter | Qt.AlignTop)

        self.saveButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], mc.FILE_PATH["存档"])))
        self.modButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], mc.FILE_PATH["模组"])))
        self.resourcePackButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], mc.FILE_PATH["资源包"])))
        self.shaderPackButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], mc.FILE_PATH["光影包"])))
        self.screenshotButton.setEnabled(f.existPath(f.pathJoin(self.data["路径"], mc.FILE_PATH["截图"])))

    def backButtonClicked(self):
        self.parent().page["管理"].loadPage()
        self.parent().showPage("管理")

    def saveButtonClicked(self):
        self.parent().page["存档"].setData(self.data)
        self.parent().showPage("存档")

    def modButtonClicked(self):
        self.parent().page["模组"].setData(self.data)
        self.parent().showPage("模组")

    def resourcePackButtonClicked(self):
        self.parent().page["资源包"].setData(self.data)
        self.parent().showPage("资源包")

    def shaderPackButtonClicked(self):
        self.parent().page["光影包"].setData(self.data)
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
        self.data = mc.getSaveInfo(path)

        self.mainButton.setText("打开")
        self.mainButton.setIcon(FIF.FOLDER)

        if self.data["封面"]:
            self.setImg(self.data["封面"])

        self.setTitle(self.data["名称"])
        self.setInfo(f"{self.data["游戏模式"]} | {self.data["游戏难度"]}", 0)
        self.setInfo(self.data["最近游玩"], 1)

        self.hBoxLayout.insertWidget(3, CopyTextButton(self.data["种子"], "种子", self))
        self.hBoxLayout.insertWidget(4, CopyTextButton(self.data["路径"], "路径", self))
        self.hBoxLayout.insertSpacing(5, -24)
        self.hBoxLayout.insertSpacing(4, -8)

    def mainButtonClicked(self):
        f.showFile(self.path)


class SaveManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("存档")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["存档"])))
        self.openButton.setToolTip("打开存档目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

        self.cardGroup = CardGroup("存档", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def loadPage(self, data=None):
        if data:
            self.data = data
        self.cardGroup.clearWidget()

        savelist = [i for i in f.walkDir(f.pathJoin(self.data["路径"], mc.FILE_PATH["存档"]), 1) if f.existPath(f.pathJoin(i, "level.dat"))]
        for i in savelist:
            self.saveCard = SaveCard(i, self)
            self.cardGroup.addWidget(self.saveCard)
        self.cardGroup.setTitle(f"存档（{len(savelist)}个）")


class SourceCard(SmallInfoCard):
    """
    资源（模组光影资源包）卡片
    """

    def __init__(self, path: str, type: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.type = type

        self.setTitle(f"{f.splitPath(path)} | {type}")
        self.setInfo(f"文件大小：{f.fileSizeAddUnit(f.getSize(self.path))}", 0)


class ModManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("模组")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["模组"])))
        self.openButton.setToolTip("打开模组目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

        self.cardGroup = CardGroup("模组", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def loadPage(self, data=None):
        if data:
            self.data = data
        self.cardGroup.deleteLater()
        self.cardGroup = CardGroup("模组", self)
        self.vBoxLayout.addWidget(self.cardGroup)

        modlist = [i for i in f.walkFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["模组"]), 1) if f.splitPath(i, 2) in mc.FILE_SUFFIX["模组"]]
        for i in modlist:
            self.card = SourceCard(i, "模组", self)
            self.cardGroup.addWidget(self.card)
        self.cardGroup.setTitle(f"模组（{len(modlist)}个）")


class ResourcePackManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源包")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["资源包"])))
        self.openButton.setToolTip("打开资源包目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

        self.cardGroup = CardGroup("资源包", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def loadPage(self, data=None):
        if data:
            self.data = data
        self.cardGroup.deleteLater()
        self.cardGroup = CardGroup("资源包", self)
        self.vBoxLayout.addWidget(self.cardGroup)

        packlist = [i for i in f.walkFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["资源包"]), 1) if f.splitPath(i, 2) in mc.FILE_SUFFIX["资源包"]]
        for i in packlist:
            self.card = SourceCard(i, "资源包", self)
            self.cardGroup.addWidget(self.card)
        self.cardGroup.setTitle(f"资源包（{len(packlist)}个）")


class ShaderPackManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("光影包")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["光影包"])))
        self.openButton.setToolTip("打开光影包目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.grayCard.insertWidget(0, self.openButton)

        self.cardGroup = CardGroup("光影包", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def loadPage(self, data=None):
        if data:
            self.data = data
        self.cardGroup.deleteLater()
        self.cardGroup = CardGroup("光影包", self)
        self.vBoxLayout.addWidget(self.cardGroup)

        packlist = [i for i in f.walkFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["光影包"]), 1) if f.splitPath(i, 2) in mc.FILE_SUFFIX["光影包"]]
        for i in packlist:
            self.card = SourceCard(i, "光影包", self)
            self.cardGroup.addWidget(self.card)
        self.cardGroup.setTitle(f"光影包（{len(packlist)}个）")


class SmallModInfoCard(SmallInfoCard, SignalBase):
    """
    资源信息小卡片
    """

    def __init__(self, data: dict, source: str, parent: QWidget = None):
        """
        @param data: 资源数据
        @param source: 资源来源
        """
        super().__init__(parent)

        self.data = data
        self.source = source

        self.mainButton.deleteLater()

        if isinstance(self.data, dict):
            self.loadInfo()
        else:
            self.setTitle("信息正在加载中...")
            self.thread1 = AddonThread("获得单独模组信息", [self.data, self.source])
            self.thread1.signalDict.connect(self.thread1_1)
            self.thread1.signalBool.connect(self.thread1_2)
            self.thread1.start()

    def thread1_1(self, msg):
        self.data = msg
        self.loadInfo()

    def thread1_2(self, msg):
        if not msg:
            self.setTitle("信息加载失败！")

    def loadInfo(self):
        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data['名称'])}.png", self.data["图标"])
        self.setTitle(f"{self.data['名称']}")
        self.setInfo(self.data["介绍"], 0)
        self.setInfo(f"下载量：{f.numberAddUnit(self.data['下载量'])}", 1)
        self.setInfo(f"游戏版本：{self.data['游戏版本'][0] + '-' + self.data['游戏版本'][-1] if len(self.data['游戏版本']) > 1 else self.data['游戏版本'][0] if len(self.data['游戏版本']) > 0 else '无'}", 2)
        self.setInfo(f"更新日期：{self.data['更新日期']}", 3)

    def mousePressEvent(self, event):
        if isinstance(self.data, dict):
            self.signalDict.emit(self.data)


class SearchTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("搜索")
        self.isInit = False

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.backButton.setToolTip("返回版本页面")
        self.backButton.installEventFilter(ToolTipFilter(self.backButton, 1000))
        self.backButton.move(8, 8)
        self.backButton.setFixedSize(32, 32)

        self.vBoxLayout.setSpacing(8)

        self.lineEdit = AcrylicSearchLineEdit(self)
        self.lineEdit.setPlaceholderText("资源名称")
        self.lineEdit.setToolTip("搜索资源，数据来源：\n CurseForge\n Modrinth")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.returnPressed.connect(self.lineEditReturnPressed)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)
        self.lineEdit.searchButton.setEnabled(True)

        self.label1 = StrongBodyLabel("数据源", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("下载应用来源")
        self.comboBox1.addItems(["CurseForge", "Modrinth"])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择下载应用来源")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.currentIndexChanged.connect(self.searchButtonClicked)

        self.label2 = StrongBodyLabel("版本", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("版本")
        self.comboBox2.addItems(["全部"])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择资源版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox2, 1000))
        self.comboBox2.setMaxVisibleItems(15)
        self.comboBox2.currentIndexChanged.connect(self.searchButtonClicked)

        self.label3 = StrongBodyLabel("类型", self)

        self.comboBox3 = AcrylicComboBox(self)
        self.comboBox3.setPlaceholderText("类型")
        self.comboBox3.addItems(list(mc.CURSEFORGE_TYPE.keys()))
        self.comboBox3.setCurrentIndex(0)
        self.comboBox3.setToolTip("选择资源类型")
        self.comboBox3.installEventFilter(ToolTipFilter(self.comboBox3, 1000))
        self.comboBox3.setMaxVisibleItems(15)
        self.comboBox3.currentIndexChanged.connect(self.searchButtonClicked)

        self.card1 = GrayCard("搜索")
        self.card1.addWidget(self.lineEdit)

        self.card2 = GrayCard("筛选")
        self.card2.addWidget(self.label1, alignment=Qt.AlignCenter)
        self.card2.addWidget(self.comboBox1)
        self.card2.addWidget(self.label2, alignment=Qt.AlignCenter)
        self.card2.addWidget(self.comboBox2)
        self.card2.addWidget(self.label3, alignment=Qt.AlignCenter)
        self.card2.addWidget(self.comboBox3)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

    def backButtonClicked(self):
        self.parent().page["管理"].loadPage()
        self.parent().showPage("管理")

    def showEvent(self, QShowEvent):
        if not self.isInit:
            self.isInit = True
            self.thread1 = AddonThread("获得游戏版本列表")
            self.thread1.signalList.connect(self.threadEvent1_1)
            self.thread1.signalBool.connect(self.threadEvent1_2)
            self.thread1.start()

            self.loadingCard.setText("正在获得游戏版本列表")
            self.loadingCard.show()
            self.lineEdit.setEnabled(False)
            self.comboBox1.setEnabled(False)
            self.comboBox2.setEnabled(False)
            self.comboBox3.setEnabled(False)

    def lineEditReturnPressed(self):
        self.lineEdit.searchButton.click()

    def searchButtonClicked(self):
        if self.comboBox1.currentText() == "Modrinth":
            if self.comboBox3.currentText() not in mc.MODRINTH_TYPE.keys():
                self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"{self.comboBox1.currentText()}不支持搜索{self.comboBox3.currentText()}类资源", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
                self.infoBar.show()
                return
        self.cardGroup1.deleteLater()
        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.cardGroup1.setTitleEnabled(False)
        self.lineEdit.setEnabled(False)
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)
        self.comboBox3.setEnabled(False)

        self.loadingCard.setText("搜索中...")
        self.loadingCard.show()

        self.thread2 = AddonThread("搜索资源", [self.lineEdit.text(), self.comboBox1.currentText(), self.comboBox2.currentText(), self.comboBox3.currentText()])
        self.thread2.signalList.connect(self.threadEvent2_1)
        self.thread2.signalBool.connect(self.threadEvent2_2)
        self.thread2.start()

    def threadEvent1_1(self, msg):
        self.loadingCard.hide()
        self.comboBox2.addItems(msg)
        self.lineEdit.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)
        self.lineEdit.searchButton.click()

    def threadEvent1_2(self, msg):
        if not msg:
            self.comboBox2.addItems(mc.RELEASE_VERSIONS)

    def threadEvent2_1(self, msg):
        self.loadingCard.hide()
        for i in msg:
            self.infoCard = SmallModInfoCard(i, self.comboBox1.currentText(), self)
            # self.infoCard.signalDict.connect(self.showModPage)
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignTop)
            self.cardGroup1.addWidget(self.infoCard)
        if msg:
            self.cardGroup1.setTitle(f"搜索结果（{len(msg)}个）")
        else:
            self.cardGroup1.setTitle(f"无搜索结果")
        self.cardGroup1.setTitleEnabled(True)

        self.lineEdit.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)

    def threadEvent2_2(self, msg):
        if not msg:
            self.loadingCard.setText("搜索失败！")
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox1.setEnabled(True)
            self.comboBox2.setEnabled(True)
            self.comboBox3.setEnabled(True)


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

            self.versionsManageTab = VersionsManageTab(self)
            self.addonSettingTab = AddonSettingTab(self)
            self.versionManageTab = VersionManageTab(self)
            self.saveManageTab = SaveManageTab(self)
            self.modManageTab = ModManageTab(self)
            self.resourcePackManageTab = ResourcePackManageTab(self)
            self.shaderPackManageTab = ShaderPackManageTab(self)
            self.downloadTab = SearchTab(self)

            self.addPage(self.versionsManageTab)
            self.addPage(self.addonSettingTab)
            self.addPage(self.versionManageTab)
            self.addPage(self.saveManageTab)
            self.addPage(self.modManageTab)
            self.addPage(self.resourcePackManageTab)
            self.addPage(self.shaderPackManageTab)
            self.addPage(self.downloadTab)
            self.showPage("管理")
