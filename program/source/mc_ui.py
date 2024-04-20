from .mc_api import *


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
                    data1 = mc.getInfoFromHash(self.data)[0]
                except:
                    data1 = None
                try:
                    data2 = mc.getInfoFromHash(self.data, source="Modrinth")[0]
                except:
                    data2 = None
                if not data1 and not data2:
                    self.signalBool.emit(False)
                self.signalList.emit([data1, data2])
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "从文件获得模组信息":
            try:
                try:
                    data1 = mc.getModInfo(self.data[0]["模组id"])
                except:
                    data1 = []
                try:
                    data2 = mc.getModInfo(self.data[1]["模组id"], source="Modrinth")
                except:
                    data2 = []

                if not data1 and not data2:
                    self.signalBool.emit(False)
                self.signalList.emit([data1, data2])
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得模组最新版本":
            try:
                dict1 = {}
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
                            data1[self.data[1]][0]["源文件名称"] = response[i]["源文件名称"]
                            data.append(data1[self.data[1]][0])
                        except:
                            pass
                        self.signalInt.emit(int(100 * (i + 2) / (len(response) + 1)))
                self.signalInt.emit(100)
                for i in response:
                    dict1[i["源文件名称"]] = [i, None]
                for i in data:
                    if i["源文件名称"] in dict1.keys():
                        dict1[i["源文件名称"]][1] = i
                self.signalDict.emit(dict1)
            except Exception as ex:
                self.signalBool.emit(False)
        logging.info(f"MC资源管理器插件 {self.mode} 线程结束")


class UpdateModWidget(QWidget):
    """
    下载文件ui接口
    """

    def __init__(self, link: str, name: str, old: str = "", parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.name = name
        self.link = link
        self.old = old

        self.thread1 = CustomThread("下载文件", (link, name))
        self.thread1.signalInt.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

        self.progressBar = ProgressBar(self.parent)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载文件 {f.splitPath(name)}", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()
        self.infoBar.closeButton.clicked.connect(self.thread1.cancel)

    def thread1_1(self, msg):
        try:
            self.infoBar.contentLabel.setText(f"正在下载文件 {f.splitPath(self.name)}")
            self.progressBar.setValue(msg)
        except:
            return
        if msg == 100:
            self.infoBar.contentLabel.setText(f"{self.name} 下载成功")
            self.infoBar.closeButton.click()

            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载", f"资源 {f.splitPath(self.name)} 下载成功", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
            self.button1 = PushButton("打开目录", self.parent, FIF.FOLDER)
            self.button1.clicked.connect(self.button1Clicked)
            self.infoBar.addWidget(self.button1)

            if self.old:
                f.moveFile(self.old, self.old + ".old")

            self.progressBar.setValue(0)
            self.progressBar.deleteLater()

    def thread1_2(self, msg):
        if not msg:
            try:
                self.infoBar.closeButton.click()
            except:
                self.thread1.cancel()
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "下载失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()

    def button1Clicked(self):
        if f.existPath(self.name):
            f.showFile(self.name)
        else:
            f.showFile(f.splitPath(self.name, 3))

        self.infoBar.closeButton.click()


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

        self.thread1 = AddonThread("获得游戏版本列表")
        self.thread1.signalList.connect(self.threadEvent1_1)
        self.thread1.signalBool.connect(self.threadEvent1_2)
        self.thread1.start()

        self.loadingCard = LoadingCard(self)
        self.loadingCard.setText("正在初始化...")

        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

    def threadEvent1_1(self, msg):
        mc.RELEASE_VERSIONS = msg
        self.loadingCard.hide()

    def threadEvent1_2(self, msg):
        if not msg:
            self.loadingCard.setText("初始化失败！")

    def settingButtonClicked(self):
        self.parent().showPage("设置")

    def downloadButtonClicked(self):
        self.parent().page["搜索"].lastPage = "管理"
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

        self.grayCard1 = GrayCard("管理", self)

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadPage)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.grayCard1.addWidget(self.reloadButton)
        self.vBoxLayout.addWidget(self.grayCard1)

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

        self.downloadButton = PushButton("下载", self, FIF.DOWNLOAD)
        self.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.downloadButton.setToolTip("下载地图")
        self.downloadButton.installEventFilter(ToolTipFilter(self.downloadButton, 1000))

        self.grayCard1.insertWidget(0, self.openButton)
        self.grayCard1.insertWidget(0, self.downloadButton)

        self.cardGroup = CardGroup("存档", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def downloadButtonClicked(self):
        self.parent().page["搜索"].lastPage = "存档"
        self.parent().page["搜索"].comboBox2.setCurrentText(self.data["游戏版本"])
        self.parent().page["搜索"].comboBox3.setCurrentText("地图")
        self.parent().showPage("搜索")

    def loadPage(self, data=None):
        if data:
            self.data = data
        self.cardGroup.clearWidget()

        savelist = [i for i in f.walkDir(f.pathJoin(self.data["路径"], mc.FILE_PATH["存档"]), 1) if f.existPath(f.pathJoin(i, "level.dat"))]
        for i in savelist:
            self.saveCard = SaveCard(i, self)
            self.cardGroup.addWidget(self.saveCard)
        self.cardGroup.setTitle(f"存档（{len(savelist)}个）")


class FileInfoMessageBox(MessageBoxBase):
    """
    资源文件信息的弹出框
    """

    def __init__(self, type: str, path: str, parent=None):
        super().__init__(parent.parent().parent().parent().parent())
        self.data = [[], []]
        self.modData = [[], []]
        self.type = type
        self.path = path
        self.parent = parent

        self.loadingCard = LoadingCard(self)

        self.titleLabel = SubtitleLabel(f.splitPath(path), self)
        self.bodyLabel1 = BodyLabel(self)
        self.bodyLabel1.setWordWrap(True)
        self.bodyLabel1.hide()
        self.image = Image(self)
        self.image.hide()

        self.hBoxLayout1 = QHBoxLayout(self)
        self.hBoxLayout1.addWidget(self.bodyLabel1)
        self.hBoxLayout1.addWidget(self.image)

        self.bodyLabel2 = BodyLabel(f"文件大小：{f.fileSizeAddUnit(f.getSize(self.path))}", self)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.loadingCard, 0, Qt.AlignVCenter | Qt.AlignCenter)
        self.viewLayout.addLayout(self.hBoxLayout1)
        self.viewLayout.addWidget(self.bodyLabel2)

        self.yesButton.setText("确定")
        self.yesButton.hide()
        self.cancelButton.setText("返回")

        self.setMinimumWidth(650)

        self.thread1 = AddonThread("获得文件信息", self.path)
        self.thread1.signalList.connect(self.threadEvent1)
        self.thread1.start()

        self.thread2 = AddonThread("从文件获得模组信息")

        self.rejected.connect(self.stopThreadWhenClose)
        self.accepted.connect(self.stopThreadWhenClose)

    def stopThreadWhenClose(self):
        self.thread1.terminate()
        self.thread2.terminate()

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key.Key_Escape:
            self.accept()
            self.accepted.emit()

    def threadEvent1(self, msg):
        self.data = msg

        self.thread2.data = msg
        self.thread2.signalList.connect(self.threadEvent2)
        self.thread2.start()
        self.hBoxLayout2 = QHBoxLayout(self)
        self.viewLayout.addLayout(self.hBoxLayout2)
        if msg[1]:
            self.buttonLayout.insertWidget(0, CopyTextButton(msg[1]["下载链接"], "Modrinth下载链接", self))
            self.hBoxLayout2.insertWidget(0, BodyLabel(f"Modrinth：\n 更新日期：{msg[1]["更新日期"]}\n 下载量：{f.numberAddUnit(msg[1]["下载量"])}", self))
        if msg[0]:
            self.buttonLayout.insertWidget(0, CopyTextButton(msg[0]["下载链接"], "CurseForge下载链接", self))
            self.hBoxLayout2.insertWidget(0, BodyLabel(f"CurseForge：\n 更新日期：{msg[0]["更新日期"]}\n 下载量：{f.numberAddUnit(msg[0]["下载量"])}", self))
        else:
            self.hBoxLayout2.insertWidget(0, BodyLabel("文件无在线数据！", self))

    def threadEvent2(self, msg):
        self.modData = msg
        if msg[1]:
            self.modrinthButton = PrimaryPushButton("Modrinth", self, FIF.LINK)
            self.modrinthButton.clicked.connect(self.ModrinthButtonClicked)
            self.buttonLayout.insertWidget(0, self.modrinthButton)
            self.image.setImg(f"Modrinth/{f.removeIllegalPath(msg[1]["名称"])}.png", msg[1]["图标"])
            self.titleLabel.setText(msg[1]["名称"])
            self.bodyLabel1.setText(msg[1]["介绍"])
            self.bodyLabel1.show()
            self.bodyLabel2.setText(f"文件名称：{f.splitPath(self.path)}\n文件大小：{f.fileSizeAddUnit(f.getSize(self.path))}")
            self.image.show()
        if msg[0]:
            self.curseForgeButton = PrimaryPushButton("CurseForge", self, FIF.LINK)
            self.curseForgeButton.clicked.connect(self.CurseForgeButtonClicked)
            self.buttonLayout.insertWidget(0, self.curseForgeButton)
            if not self.image.imgPath:
                self.image.setImg(f"CurseForge/{f.removeIllegalPath(msg[0]["名称"])}.png", msg[0]["图标"])
            self.titleLabel.setText(msg[0]["名称"])
            self.bodyLabel1.setText(msg[0]["介绍"])
            self.bodyLabel1.show()
            self.bodyLabel2.setText(f"文件名称：{f.splitPath(self.path)}\n文件大小：{f.fileSizeAddUnit(f.getSize(self.path))}")
            self.image.show()
        self.loadingCard.hide()

    def CurseForgeButtonClicked(self):
        self.accept()
        self.parent.parent().page["信息"].lastPage = self.type
        self.parent.parent().page["信息"].version = self.parent.data["游戏版本"]
        loader = [i[0] for i in self.parent.data["加载器"] if i[0] in mc.MOD_LOADER_LIST]
        if loader:
            self.parent.parent().page["信息"].loader = loader[0]
        self.parent.parent().page["信息"].loadPage(self.modData[0])
        self.parent.parent().showPage("信息")

    def ModrinthButtonClicked(self):
        self.accept()
        self.parent.parent().page["信息"].lastPage = self.type
        self.parent.parent().page["信息"].version = self.parent.data["游戏版本"]
        loader = [i[0] for i in self.parent.data["加载器"] if i[0] in mc.MOD_LOADER_LIST]
        if loader:
            self.parent.parent().page["信息"].loader = loader[0]
        self.parent.parent().page["信息"].loadPage(self.modData[1])
        self.parent.parent().showPage("信息")


class SourceCard(SmallInfoCard):
    """
    资源（模组光影资源包）卡片
    """

    def __init__(self, path: str, type: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.type = type

        self.image.deleteLater()
        self.setTitle(f"{f.splitPath(path)}")  # | {type}
        self.setInfo(f"文件大小：{f.fileSizeAddUnit(f.getSize(self.path))}", 0)
        self.mainButton.setText("信息")
        self.mainButton.setIcon(FIF.INFO)

    def mainButtonClicked(self):
        self.fileInfoMessageBox = FileInfoMessageBox(self.type, self.path, self.parent().parent().parent().parent())
        self.fileInfoMessageBox.exec()


class ModUpdateMessageBox(MessageBoxBase):
    """
    更新资源的弹出框
    """

    def __init__(self, title: str, data: list, path: str, parent=None):
        super().__init__(parent.parent().parent().parent().parent())
        self.data = data
        self.path = path
        self.parent = parent

        self.titleLabel = SubtitleLabel(title, self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(3)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["文件名", "本地版本号", "在线版本号"])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.tableView, 0, Qt.AlignTop)

        self.yesButton.setText("更新")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(690)

        self.setMinimumWidth(690)

        import string

        abc = string.ascii_lowercase + string.ascii_uppercase + "-_. \n"

        self.tableView.setRowCount(len(data))
        for i in range(len(data)):
            self.tableView.setItem(i, 0, QTableWidgetItem(data[i][0]["源文件名称"]))
            self.tableView.setItem(i, 1, QTableWidgetItem(data[i][0]["文件名称"].strip(abc)))
            self.tableView.setItem(i, 2, QTableWidgetItem(data[i][1]["文件名称"].strip(abc)))
            if not data[i][1]["下载链接"]:
                self.tableView.hideRow(i)

    def yesButtonClicked(self):
        for i in self.data:
            if i[1]["下载链接"]:
                UpdateModWidget(i[1]["下载链接"], f.pathJoin(self.path, i[1]["文件名称"]), f.pathJoin(self.path, i[0]["源文件名称"]), self.parent.parent())


class ModManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("模组")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["模组"])))
        self.openButton.setToolTip("打开模组目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))

        self.downloadButton = PushButton("下载", self, FIF.DOWNLOAD)
        self.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.downloadButton.setToolTip("下载模组")
        self.downloadButton.installEventFilter(ToolTipFilter(self.downloadButton, 1000))

        self.grayCard1.insertWidget(0, self.openButton)
        self.grayCard1.insertWidget(0, self.downloadButton)

        self.updateButton = PushButton("立刻更新", self, FIF.UPDATE)
        self.updateButton.clicked.connect(self.updateButtonClicked)
        self.updateButton.setToolTip("更新资源")
        self.updateButton.installEventFilter(ToolTipFilter(self.updateButton, 1000))

        self.label2_1 = StrongBodyLabel("来源", self)

        self.comboBox2_1 = AcrylicComboBox(self)
        self.comboBox2_1.setPlaceholderText("来源")
        self.comboBox2_1.addItems(["CurseForge", "Modrinth"])
        self.comboBox2_1.setCurrentIndex(0)
        self.comboBox2_1.setToolTip("选择更新来源")
        self.comboBox2_1.installEventFilter(ToolTipFilter(self.comboBox2_1, 1000))

        self.label2_2 = StrongBodyLabel("版本", self)

        self.comboBox2_2 = AcrylicComboBox(self)
        self.comboBox2_2.setPlaceholderText("版本")
        self.comboBox2_2.addItems(mc.RELEASE_VERSIONS)
        self.comboBox2_2.setToolTip("选择目标版本")
        self.comboBox2_2.installEventFilter(ToolTipFilter(self.comboBox2_2, 1000))
        self.comboBox2_2.setMaxVisibleItems(15)

        self.label2_3 = StrongBodyLabel("加载器", self)

        self.comboBox2_3 = AcrylicComboBox(self)
        self.comboBox2_3.setPlaceholderText("加载器")
        self.comboBox2_3.addItems(mc.MOD_LOADER_LIST)
        self.comboBox2_3.setToolTip("选择目标加载器")
        self.comboBox2_3.installEventFilter(ToolTipFilter(self.comboBox2_3, 1000))
        self.comboBox2_3.setMaxVisibleItems(15)

        self.switchButton = SwitchButton("跨版本", self, IndicatorPosition.RIGHT)
        self.switchButton.setChecked(False)
        self.switchButton.setOnText("跨版本")
        self.switchButton.setOffText("跨版本")
        self.switchButton.setToolTip("如果要将模组更新到与现有版本不同的版本与加载器，请勾选！")
        self.switchButton.installEventFilter(ToolTipFilter(self.switchButton, 1000))
        self.switchButton.checkedChanged.connect(self.switchButtonChanged)
        self.switchButtonChanged()

        self.grayCard2 = GrayCard("更新")

        self.grayCard2.addWidget(self.updateButton)
        self.grayCard2.addWidget(self.label2_1, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_1)
        self.grayCard2.addWidget(self.label2_2, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_2)
        self.grayCard2.addWidget(self.label2_3, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_3)
        self.grayCard2.addWidget(self.switchButton, alignment=Qt.AlignCenter)

        self.vBoxLayout.insertWidget(1, self.grayCard2)

        self.cardGroup = CardGroup("模组", self)
        self.vBoxLayout.addWidget(self.cardGroup)

    def downloadButtonClicked(self):
        self.parent().page["搜索"].lastPage = "模组"
        self.parent().page["搜索"].comboBox2.setCurrentText(self.data["游戏版本"])
        self.parent().page["搜索"].comboBox3.setCurrentText("模组")
        self.parent().showPage("搜索")

    def switchButtonChanged(self):
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())
        self.comboBox2_3.setEnabled(self.switchButton.isChecked())
        if not self.switchButton.isChecked():
            if self.data:
                self.comboBox2_2.setCurrentText(self.data["游戏版本"])
                loader = [i[0] for i in self.data["加载器"] if i[0] in mc.MOD_LOADER_LIST]
                self.comboBox2_3.setCurrentText(loader[0] if loader else "Forge")

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

        self.comboBox2_2.setCurrentText(self.data["游戏版本"])
        loader = [i[0] for i in self.data["加载器"] if i[0] in mc.MOD_LOADER_LIST]
        self.comboBox2_3.setCurrentText(loader[0] if loader else "Forge")

    def updateButtonClicked(self):
        self.updateButton.setEnabled(False)
        self.comboBox2_1.setEnabled(False)
        self.comboBox2_2.setEnabled(False)
        self.comboBox2_3.setEnabled(False)

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"正在通过{self.comboBox2_1.currentText()}检查资源在{self.comboBox2_2.currentText()}{self.comboBox2_3.currentText()}的更新", Qt.Orientation.Vertical, False, -1, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()

        self.thread3 = AddonThread("获得模组最新版本", [f.pathJoin(self.data["路径"], mc.FILE_PATH["模组"]), self.comboBox2_2.currentText(), self.comboBox2_3.currentText(), self.comboBox2_1.currentText()])
        self.thread3.signalDict.connect(self.threadEvent3_1)
        self.thread3.signalBool.connect(self.threadEvent3_2)
        self.thread3.signalInt.connect(self.threadEvent3_3)
        self.thread3.start()

    def threadEvent3_1(self, msg):
        list1 = []
        name_list = []
        for k, v in msg.items():
            if v[1]:
                if v[0]["id"] != v[1]["id"]:
                    if not self.switchButton.checked:
                        if v[0]["更新日期"] > v[1]["更新日期"]:
                            continue
                    if k in name_list:
                        continue
                    name_list.append(k)
                    list1.append(v)
        list1 = sorted(list1, key=lambda x: x[0]["名称"])
        self.infoBar.isClosable = True
        self.infoBar.closeButton.click()
        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"有{len(list1)}个资源在{self.comboBox2_2.currentText()}{self.comboBox2_3.currentText()}有新版本", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.show()
        if len(list1) > 0:
            self.modUpdateMessageBox = ModUpdateMessageBox("资源更新", list1, f.pathJoin(self.data["路径"], mc.FILE_PATH["模组"]), self)
            self.modUpdateMessageBox.exec()

        self.updateButton.setEnabled(True)
        self.comboBox2_1.setEnabled(True)
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())
        self.comboBox2_3.setEnabled(self.switchButton.isChecked())

    def threadEvent3_2(self, msg):
        if not msg:
            self.infoBar.isClosable = True
            self.infoBar.closeButton.click()
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "错误", f"检查更新失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.updateButton.setEnabled(True)
        self.comboBox2_1.setEnabled(True)
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())
        self.comboBox2_3.setEnabled(self.switchButton.isChecked())

    def threadEvent3_3(self, msg):
        try:
            self.progressBar.setValue(msg)
        except:
            pass


class ResourcePackManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源包")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["资源包"])))
        self.openButton.setToolTip("打开资源包目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))

        self.downloadButton = PushButton("下载", self, FIF.DOWNLOAD)
        self.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.downloadButton.setToolTip("下载资源包")
        self.downloadButton.installEventFilter(ToolTipFilter(self.downloadButton, 1000))

        self.grayCard1.insertWidget(0, self.openButton)
        self.grayCard1.insertWidget(0, self.downloadButton)

        self.cardGroup = CardGroup("资源包", self)
        self.vBoxLayout.addWidget(self.cardGroup)

        self.updateButton = PushButton("立刻更新", self, FIF.UPDATE)
        self.updateButton.clicked.connect(self.updateButtonClicked)
        self.updateButton.setToolTip("更新资源")
        self.updateButton.installEventFilter(ToolTipFilter(self.updateButton, 1000))

        self.label2_1 = StrongBodyLabel("来源", self)

        self.comboBox2_1 = AcrylicComboBox(self)
        self.comboBox2_1.setPlaceholderText("来源")
        self.comboBox2_1.addItems(["CurseForge", "Modrinth"])
        self.comboBox2_1.setCurrentIndex(0)
        self.comboBox2_1.setToolTip("选择更新来源")
        self.comboBox2_1.installEventFilter(ToolTipFilter(self.comboBox2_1, 1000))

        self.label2_2 = StrongBodyLabel("版本", self)

        self.comboBox2_2 = AcrylicComboBox(self)
        self.comboBox2_2.setPlaceholderText("版本")
        self.comboBox2_2.addItems(mc.RELEASE_VERSIONS)
        self.comboBox2_2.setToolTip("选择目标版本")
        self.comboBox2_2.installEventFilter(ToolTipFilter(self.comboBox2_2, 1000))
        self.comboBox2_2.setMaxVisibleItems(15)

        self.switchButton = SwitchButton("跨版本", self, IndicatorPosition.RIGHT)
        self.switchButton.setChecked(False)
        self.switchButton.setOnText("跨版本")
        self.switchButton.setOffText("跨版本")
        self.switchButton.setToolTip("如果要将模组更新到与现有版本不同的版本与加载器，请勾选！")
        self.switchButton.installEventFilter(ToolTipFilter(self.switchButton, 1000))
        self.switchButton.checkedChanged.connect(self.switchButtonChanged)
        self.switchButtonChanged()

        self.grayCard2 = GrayCard("更新")

        self.grayCard2.addWidget(self.updateButton)
        self.grayCard2.addWidget(self.label2_1, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_1)
        self.grayCard2.addWidget(self.label2_2, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_2)
        self.grayCard2.addWidget(self.switchButton, alignment=Qt.AlignCenter)

        self.vBoxLayout.insertWidget(1, self.grayCard2)

    def downloadButtonClicked(self):
        self.parent().page["搜索"].lastPage = "资源包"
        self.parent().page["搜索"].comboBox2.setCurrentText(self.data["游戏版本"])
        self.parent().page["搜索"].comboBox3.setCurrentText("资源包")
        self.parent().showPage("搜索")

    def switchButtonChanged(self):
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())
        if not self.switchButton.isChecked():
            if self.data:
                self.comboBox2_2.setCurrentText(self.data["游戏版本"])

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

        self.comboBox2_2.setCurrentText(self.data["游戏版本"])

    def updateButtonClicked(self):
        self.updateButton.setEnabled(False)
        self.comboBox2_1.setEnabled(False)
        self.comboBox2_2.setEnabled(False)

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"正在通过{self.comboBox2_1.currentText()}检查资源在{self.comboBox2_2.currentText()}的更新", Qt.Orientation.Vertical, False, -1, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()

        self.thread3 = AddonThread("获得模组最新版本", [f.pathJoin(self.data["路径"], mc.FILE_PATH["资源包"]), self.comboBox2_2.currentText(), ["Minecraft"], self.comboBox2_1.currentText()])
        self.thread3.signalDict.connect(self.threadEvent3_1)
        self.thread3.signalBool.connect(self.threadEvent3_2)
        self.thread3.signalInt.connect(self.threadEvent3_3)
        self.thread3.start()

    def threadEvent3_1(self, msg):
        list1 = []
        name_list = []
        for k, v in msg.items():
            if v[1]:
                if v[0]["id"] != v[1]["id"]:
                    if not self.switchButton.checked:
                        if v[0]["更新日期"] > v[1]["更新日期"]:
                            continue
                    if k in name_list:
                        continue
                    name_list.append(k)
                    list1.append(v)
        list1 = sorted(list1, key=lambda x: x[0]["名称"])
        self.infoBar.isClosable = True
        self.infoBar.closeButton.click()
        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"有{len(list1)}个资源在{self.comboBox2_2.currentText()}有新版本", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.show()
        if len(list1) > 0:
            self.modUpdateMessageBox = ModUpdateMessageBox("资源更新", list1, f.pathJoin(self.data["路径"], mc.FILE_PATH["资源包"]), self)
            self.modUpdateMessageBox.exec()

        self.updateButton.setEnabled(True)
        self.comboBox2_1.setEnabled(True)
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())

    def threadEvent3_2(self, msg):
        if not msg:
            self.infoBar.isClosable = True
            self.infoBar.closeButton.click()
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "错误", f"检查更新失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.updateButton.setEnabled(True)
        self.comboBox2_1.setEnabled(True)
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())

    def threadEvent3_3(self, msg):
        try:
            self.progressBar.setValue(msg)
        except:
            pass


class ShaderPackManageTab(ResourceManageTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("光影包")

        self.openButton = PushButton("打开", self, FIF.FOLDER)
        self.openButton.clicked.connect(lambda: f.showFile(f.pathJoin(self.data["路径"], mc.FILE_PATH["光影包"])))
        self.openButton.setToolTip("打开光影包目录")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))

        self.downloadButton = PushButton("下载", self, FIF.DOWNLOAD)
        self.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.downloadButton.setToolTip("下载光影")
        self.downloadButton.installEventFilter(ToolTipFilter(self.downloadButton, 1000))

        self.grayCard1.insertWidget(0, self.openButton)
        self.grayCard1.insertWidget(0, self.downloadButton)

        self.cardGroup = CardGroup("光影包", self)
        self.vBoxLayout.addWidget(self.cardGroup)

        self.updateButton = PushButton("立刻更新", self, FIF.UPDATE)
        self.updateButton.clicked.connect(self.updateButtonClicked)
        self.updateButton.setToolTip("更新资源")
        self.updateButton.installEventFilter(ToolTipFilter(self.updateButton, 1000))

        self.label2_1 = StrongBodyLabel("来源", self)

        self.comboBox2_1 = AcrylicComboBox(self)
        self.comboBox2_1.setPlaceholderText("来源")
        self.comboBox2_1.addItems(["CurseForge", "Modrinth"])
        self.comboBox2_1.setCurrentIndex(0)
        self.comboBox2_1.setToolTip("选择更新来源")
        self.comboBox2_1.installEventFilter(ToolTipFilter(self.comboBox2_1, 1000))

        self.label2_2 = StrongBodyLabel("版本", self)

        self.comboBox2_2 = AcrylicComboBox(self)
        self.comboBox2_2.setPlaceholderText("版本")
        self.comboBox2_2.addItems(mc.RELEASE_VERSIONS)
        self.comboBox2_2.setToolTip("选择目标版本")
        self.comboBox2_2.installEventFilter(ToolTipFilter(self.comboBox2_2, 1000))
        self.comboBox2_2.setMaxVisibleItems(15)

        self.switchButton = SwitchButton("跨版本", self, IndicatorPosition.RIGHT)
        self.switchButton.setChecked(False)
        self.switchButton.setOnText("跨版本")
        self.switchButton.setOffText("跨版本")
        self.switchButton.setToolTip("如果要将模组更新到与现有版本不同的版本与加载器，请勾选！")
        self.switchButton.installEventFilter(ToolTipFilter(self.switchButton, 1000))
        self.switchButton.checkedChanged.connect(self.switchButtonChanged)
        self.switchButtonChanged()

        self.grayCard2 = GrayCard("更新")

        self.grayCard2.addWidget(self.updateButton)
        self.grayCard2.addWidget(self.label2_1, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_1)
        self.grayCard2.addWidget(self.label2_2, alignment=Qt.AlignCenter)
        self.grayCard2.addWidget(self.comboBox2_2)
        self.grayCard2.addWidget(self.switchButton, alignment=Qt.AlignCenter)

        self.vBoxLayout.insertWidget(1, self.grayCard2)

    def downloadButtonClicked(self):
        self.parent().page["搜索"].lastPage = "光影包"
        self.parent().page["搜索"].comboBox2.setCurrentText(self.data["游戏版本"])
        self.parent().page["搜索"].comboBox3.setCurrentText("光影包")
        self.parent().showPage("搜索")

    def switchButtonChanged(self):
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())
        if not self.switchButton.isChecked():
            if self.data:
                self.comboBox2_2.setCurrentText(self.data["游戏版本"])

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

        self.comboBox2_2.setCurrentText(self.data["游戏版本"])

    def updateButtonClicked(self):
        self.updateButton.setEnabled(False)
        self.comboBox2_1.setEnabled(False)
        self.comboBox2_2.setEnabled(False)

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"正在通过{self.comboBox2_1.currentText()}检查资源在{self.comboBox2_2.currentText()}的更新", Qt.Orientation.Vertical, False, -1, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()

        self.thread3 = AddonThread("获得模组最新版本", [f.pathJoin(self.data["路径"], mc.FILE_PATH["光影包"]), self.comboBox2_2.currentText(), ["Iris", "Optifine", "Canvas", "Vanilla"], self.comboBox2_1.currentText()])
        self.thread3.signalDict.connect(self.threadEvent3_1)
        self.thread3.signalBool.connect(self.threadEvent3_2)
        self.thread3.signalInt.connect(self.threadEvent3_3)
        self.thread3.start()

    def threadEvent3_1(self, msg):
        list1 = []
        name_list = []
        for k, v in msg.items():
            if v[1]:
                if v[0]["id"] != v[1]["id"]:
                    if not self.switchButton.checked:
                        if v[0]["更新日期"] > v[1]["更新日期"]:
                            continue
                    if k in name_list:
                        continue
                    name_list.append(k)
                    list1.append(v)
        list1 = sorted(list1, key=lambda x: x[0]["名称"])
        self.infoBar.isClosable = True
        self.infoBar.closeButton.click()
        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"有{len(list1)}个资源在{self.comboBox2_2.currentText()}有新版本", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.show()
        if len(list1) > 0:
            self.modUpdateMessageBox = ModUpdateMessageBox("资源更新", list1, f.pathJoin(self.data["路径"], mc.FILE_PATH["光影包"]), self)
            self.modUpdateMessageBox.exec()

        self.updateButton.setEnabled(True)
        self.comboBox2_1.setEnabled(True)
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())

    def threadEvent3_2(self, msg):
        if not msg:
            self.infoBar.isClosable = True
            self.infoBar.closeButton.click()
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "错误", f"检查更新失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.updateButton.setEnabled(True)
        self.comboBox2_1.setEnabled(True)
        self.comboBox2_2.setEnabled(self.switchButton.isChecked())

    def threadEvent3_3(self, msg):
        try:
            self.progressBar.setValue(msg)
        except:
            pass


class SmallModInfoCard(SmallInfoCard, SignalBase):
    """
    资源信息小卡片
    """

    def __init__(self, data: dict, source: str, type: str, parent: QWidget = None):
        """
        @param data: 资源数据
        @param source: 资源来源
        @param type: 资源类型
        """
        super().__init__(parent)

        self.data = data
        self.source = source
        self.type = type

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
        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data["名称"])}.png", self.data["图标"])
        self.setTitle(f"{self.data["名称"]}")
        self.setInfo(self.data["介绍"], 0)
        self.setInfo(f"下载量：{f.numberAddUnit(self.data["下载量"])}", 1)
        self.setInfo(f"游戏版本：{self.data["游戏版本"][0] + "-" + self.data["游戏版本"][-1] if len(self.data["游戏版本"]) > 1 else self.data["游戏版本"][0] if len(self.data["游戏版本"]) > 0 else "无"}", 2)
        self.setInfo(f"更新日期：{self.data["更新日期"]}", 3)

    def mousePressEvent(self, event):
        if isinstance(self.data, dict):
            self.parent().parent().parent().parent().parent().page["信息"].type = self.type
            self.parent().parent().parent().parent().parent().page["信息"].version = self.parent().parent().parent().parent().comboBox2.currentText()
            self.parent().parent().parent().parent().parent().page["信息"].loadPage(self.data)
            self.parent().parent().parent().parent().parent().showPage("信息")


class SearchTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("搜索")
        self.isInit = False
        self.lastPage = "管理"

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
        self.comboBox2.addItems(["全部"] + mc.RELEASE_VERSIONS)
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
        self.parent().page[self.lastPage].loadPage()
        self.parent().showPage(self.lastPage)

    def showEvent(self, QShowEvent):
        if not self.isInit:
            self.isInit = True
            self.lineEdit.searchButton.click()
            self.comboBox2.currentIndexChanged.disconnect(self.searchButtonClicked)
            self.comboBox2.items.clear()
            self.comboBox2.addItems(["全部"] + mc.RELEASE_VERSIONS)
            self.comboBox2.currentIndexChanged.connect(self.searchButtonClicked)

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

        self.thread1 = AddonThread("搜索资源", [self.lineEdit.text(), self.comboBox1.currentText(), self.comboBox2.currentText(), self.comboBox3.currentText()])
        self.thread1.signalList.connect(self.threadEvent1_1)
        self.thread1.signalBool.connect(self.threadEvent1_2)
        self.thread1.start()

    def threadEvent1_1(self, msg):
        self.loadingCard.hide()
        for i in msg:
            self.infoCard = SmallModInfoCard(i, self.comboBox1.currentText(), self.comboBox3.currentText(), self)
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

    def threadEvent1_2(self, msg):
        if not msg:
            self.loadingCard.setText("搜索失败！")
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox1.setEnabled(True)
            self.comboBox2.setEnabled(True)
            self.comboBox3.setEnabled(True)


class SmallFileInfoCard(SmallInfoCard, SignalBase):
    """
    文件信息小卡片
    """

    def __init__(self, data: dict, type: str, parent: QWidget = None):
        """
        @param data: 资源数据
        @param type: 资源类型
        """
        super().__init__(parent)
        self.data = data
        self.type = type

        self.image.deleteLater()

        self.setTitle(f"{data["名称"]}{" · " if data["版本类型"] else ""}{data["版本类型"]}")
        self.setInfo("、".join(data["加载器"]) + (" | " if len(data["加载器"]) > 0 else "") + ("、".join(data["游戏版本"]) if len(data["游戏版本"]) <= 10 else f"支持{data["游戏版本"][0]}-{data["游戏版本"][-1]}共{len(data["游戏版本"])}个版本"), 0)
        self.setInfo(f"文件大小：{f.fileSizeAddUnit(data["文件大小"])}", 1)
        self.setInfo(f"下载量：{f.numberAddUnit(data["下载量"])}", 2)
        self.setInfo(f"更新日期：{data["更新日期"]}", 3)

        self.mainButton.setText("下载")
        self.mainButton.setIcon(FIF.DOWNLOAD)

        if not self.data["下载链接"]:
            self.mainButton.setEnabled(False)

    def mainButtonClicked(self):
        if self.type in mc.FILE_PATH.keys():
            open = f.pathJoin(mc.FILE_DOWNLOAD_PATH, mc.FILE_PATH[self.type])
        else:
            open = setting.read("downloadPath")
        path = QFileDialog.getExistingDirectory(self, "选择下载目录", open)
        if not path:
            return
        path = f.pathJoin(path, self.data["文件名称"])
        UpdateModWidget(self.data["下载链接"], path, parent=self.parent().parent().parent().parent())


class ResultTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("信息")
        self.dataList = []
        self.data = None
        self.lastPage = "搜索"
        self.version = "全部"
        self.loader = "全部"
        self.type = "模组"

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.backButton.setToolTip(f"返回{self.lastPage}页面")
        self.backButton.installEventFilter(ToolTipFilter(self.backButton, 1000))
        self.backButton.move(8, 8)
        self.backButton.setFixedSize(32, 32)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.bigInfoCard = BigInfoCard(self)

        self.label1 = StrongBodyLabel("版本", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("版本")
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择资源版本")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.currentIndexChanged.connect(self.getFileInfo)
        self.comboBox1.setMaxVisibleItems(15)
        self.comboBox1.setEnabled(False)

        self.label2 = StrongBodyLabel("加载器", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("加载器")
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择加载器版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox2.currentIndexChanged.connect(self.getFileInfo)
        self.comboBox2.setEnabled(False)

        self.grayCard = GrayCard("筛选")
        self.grayCard.addWidget(self.label1, alignment=Qt.AlignCenter)
        self.grayCard.addWidget(self.comboBox1)
        self.grayCard.addWidget(self.label2, alignment=Qt.AlignCenter)
        self.grayCard.addWidget(self.comboBox2)

        self.cardGroup = CardGroup("", self)

        self.vBoxLayout.addWidget(self.bigInfoCard)
        self.vBoxLayout.addWidget(self.grayCard)
        self.vBoxLayout.addWidget(self.cardGroup)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

        self.thread1 = AddonThread("获得资源信息")
        self.thread1.signalDict.connect(self.threadEvent1_1)
        self.thread1.signalBool.connect(self.threadEvent1_2)

        self.thread2 = AddonThread("获得资源文件")
        self.thread2.signalDict.connect(self.threadEvent2_1)
        self.thread2.signalBool.connect(self.threadEvent2_2)

    def backButtonClicked(self):
        self.dataList.pop()
        if len(self.dataList) == 0:
            self.parent().showPage(self.lastPage)
        else:
            self.loadPage(self.dataList.pop())

    def setType(self, lastPage: str, type: str, version: str, loader: str):
        self.lastPage = lastPage
        self.version = version
        self.loader = loader
        self.type = type

    def loadPage(self, data):
        self.thread1.terminate()
        self.thread2.terminate()

        self.comboBox1.currentIndexChanged.disconnect(self.getFileInfo)
        self.comboBox2.currentIndexChanged.disconnect(self.getFileInfo)
        self.comboBox1.setCurrentText("全部")
        self.comboBox2.setCurrentText("全部")
        self.comboBox1.currentIndexChanged.connect(self.getFileInfo)
        self.comboBox2.currentIndexChanged.connect(self.getFileInfo)

        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)

        self.data = data
        self.dataList.append(self.data)

        self.loadingCard.setText("加载中")
        self.loadingCard.show()

        self.cardGroup.hide()

        self.bigInfoCard.deleteLater()
        self.bigInfoCard = BigInfoCard(self)
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.deleteLater()
        self.bigInfoCard.setTitle(data["名称"])
        self.bigInfoCard.setInfo(data["介绍"])
        self.bigInfoCard.setImg(f"{data["来源"]}/{f.removeIllegalPath(data["名称"])}.png", data["图标"])
        try:
            self.bigInfoCard.addData("作者", data["作者"])
        except:
            pass
        self.bigInfoCard.addData("下载量", f.numberAddUnit(data["下载量"]))
        self.bigInfoCard.addData("发布日期", data["发布日期"])
        self.bigInfoCard.addData("更新日期", data["更新日期"])

        self.vBoxLayout.insertWidget(0, self.bigInfoCard)

        self.thread1.data = [data["id"], data["来源"]]
        self.thread1.start()

    def threadEvent1_1(self, msg):
        self.comboBox1.currentIndexChanged.disconnect(self.getFileInfo)
        self.comboBox2.currentIndexChanged.disconnect(self.getFileInfo)
        self.comboBox1.items.clear()
        self.comboBox2.items.clear()
        self.comboBox1.addItems(["全部"] + msg["游戏版本"][::-1])
        if self.version in ["全部"] + msg["游戏版本"]:
            self.comboBox1.setCurrentText(self.version)
        self.comboBox2.addItems(["全部"] + msg["加载器"])
        if self.loader in ["全部"] + msg["加载器"]:
            self.comboBox2.setCurrentText(self.loader)
        self.comboBox1.currentIndexChanged.connect(self.getFileInfo)
        self.comboBox2.currentIndexChanged.connect(self.getFileInfo)

        self.bigInfoCard.setTitle(msg["名称"])
        self.bigInfoCard.setInfo(msg["介绍"])
        self.bigInfoCard.setImg(f"{msg["来源"]}/{f.removeIllegalPath(msg["名称"])}.png", msg["图标"])
        self.bigInfoCard.addUrl(msg["来源"], msg["网站链接"], FIF.LINK)
        if msg["源代码链接"]:
            self.bigInfoCard.addUrl("源代码", msg["源代码链接"], FIF.GITHUB)
        self.bigInfoCard.addUrl("MC百科", f"https://search.mcmod.cn/s?key={msg["名称"]}", FIF.SEARCH)

        for i in msg["加载器"]:
            self.bigInfoCard.addTag(i)

        self.getFileInfo()

    def threadEvent1_2(self, msg):
        if not msg:
            self.loadingCard.setText("加载失败")

    def getFileInfo(self):
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)

        self.cardGroup.hide()
        self.loadingCard.setText("加载中")
        self.loadingCard.show()

        self.thread2.data = [self.data["id"], self.comboBox1.currentText(), self.comboBox2.currentText(), self.data["来源"]]
        self.thread2.start()

    def threadEvent2_1(self, msg):
        self.cardGroup.deleteLater()
        self.cardGroup = CardGroup("文件", self)
        if len(msg.keys()) == 0:
            self.cardGroup.setTitle("无筛选结果")
        self.vBoxLayout.insertWidget(3, self.cardGroup)

        dependencies = []
        for k in msg.keys():
            for i in msg[k]:
                dependencies += i["前置"]
        dependencies = list(set(dependencies))
        if len(dependencies) > 0:
            self.cardGroup.addWidget(StrongBodyLabel(f"前置（{len(dependencies)}个）", self))
        if len(dependencies) <= 10:
            for i in dependencies:
                self.infoCard = SmallModInfoCard(i, self.data["来源"], self.type, self)
                self.infoCard.signalDict.connect(self.signalDict.emit)
                self.cardGroup.addWidget(self.infoCard)
        else:
            self.cardGroup.addWidget(StrongBodyLabel(f"前置数量过多，无法展示，请前往资源网页查看！", self))
        i = 0
        for k in f.sortVersion(msg.keys(), True):
            if k == self.comboBox1.currentText() or self.comboBox1.currentText() == "全部":
                self.cardGroup.addWidget(StrongBodyLabel(k, self))
                for v in msg[k]:
                    self.cardGroup.addWidget(SmallFileInfoCard(v, self.type))
                    if i > 50:
                        break
                    i += 1
        self.cardGroup.show()
        self.loadingCard.hide()
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)

    def threadEvent2_2(self, msg):
        if not msg:
            self.loadingCard.setText("加载失败")
            self.loadingCard.show()


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
            self.searchTab = SearchTab(self)
            self.resultTab = ResultTab(self)

            self.addPage(self.versionsManageTab)
            self.addPage(self.addonSettingTab)
            self.addPage(self.versionManageTab)
            self.addPage(self.saveManageTab)
            self.addPage(self.modManageTab)
            self.addPage(self.resourcePackManageTab)
            self.addPage(self.shaderPackManageTab)
            self.addPage(self.searchTab)
            self.addPage(self.resultTab)

            self.showPage("管理")
