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

        if self.mode == "加载目录游戏信息":
            try:
                data = getPathGameInfo(setting.read("minecraftJavaPath"))
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
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
        self.backButton.move(8, 0)

        self.vBoxLayout.addWidget(self.cardGroup1)

    def backButtonClicked(self):
        self.parent().page["管理"].loadPage()
        self.parent().showPage("管理")


class AddonManageTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("管理")

        self.cardGroup1 = CardGroup("管理", self)

        self.smallInfoCard = SmallInfoCard(self)
        self.smallInfoCard.setImg("grass_block.png", "https://patchwiki.biligame.com/images/mc/d/d0/jsva4b20p50dyilh54o7jnzmt5eytt4.png")
        self.smallInfoCard.mainButton.setText("打开")
        self.smallInfoCard.mainButton.setIcon(FIF.FOLDER)
        self.smallInfoCard.mainButton.clicked.connect(lambda: f.showFile(setting.read("minecraftJavaPath")))

        self.grayCard = GrayCard("设置", self)

        self.settingButton = PushButton("设置", self, FIF.SETTING)
        self.settingButton.clicked.connect(self.settingButtonClicked)
        self.settingButton.setToolTip("打开插件设置")
        self.settingButton.installEventFilter(ToolTipFilter(self.settingButton, 1000))

        self.grayCard.addWidget(self.settingButton)

        self.cardGroup1.addWidget(self.smallInfoCard)
        self.cardGroup1.addWidget(self.grayCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignmentFlag.AlignTop)

        self.loadPage()

    def settingButtonClicked(self):
        self.parent().showPage("设置")

    def loadPage(self):
        self.smallInfoCard.setTitle(f.splitPath(setting.read("minecraftJavaPath")))

        self.thread1 = AddonThread("加载目录游戏信息")
        self.thread1.signalDict.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.run()

    def thread1_1(self, msg):
        self.smallInfoCard.setTitle(msg["id"])
        data = msg["游戏版本"]
        for i in msg["加载器"]:
            data += f" | {i[0]} {i[1]}"
        self.smallInfoCard.setInfo(data, 0)

    def thread1_2(self, msg):
        if not msg:
            self.smallInfoCard.setInfo(f"目录{setting.read('minecraftJavaPath')}的Minecraft版本信息读取失败！", 0)


class AddonPage(BasicTabPage):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.GAME)
        self.setObjectName("MC资源管理器")

        self.page = ChangeableTab(self)

        self.addonManageTab = AddonManageTab()
        self.addonSettingTab = AddonSettingTab()

        self.page.addPage(self.addonManageTab)
        self.page.addPage(self.addonSettingTab)
        self.page.showPage("管理")

        self.addPage(self.page)
