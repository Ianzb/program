from window import *


class MainPage(BasicPage):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.button1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.button1_2 = ToolButton(FIF.FOLDER, self)
        self.button2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.button3_1 = PushButton("查看Minecraft最新版本", self, FIF.CHECKBOX)

        self.button1_1.clicked.connect(self.buttonClicked1_1)
        self.button1_2.clicked.connect(self.buttonClicked1_2)
        self.button2_1.clicked.connect(self.buttonClicked2_1)
        self.button3_1.clicked.connect(self.buttonClicked3_1)

        self.button1_1.setToolTip("开始整理+清理文件，范围包括：\n  整理桌面文件\n  整理微信文件\n  清空回收站\n  清理系统缓存")
        self.button1_2.setToolTip("打开整理文件所在目录")
        self.button2_1.setToolTip("重启文件资源管理器")
        self.button3_1.setToolTip("查看Minecraft最新版本，数据来源：\n  我的世界中文维基百科（https://zh.minecraft.wiki/）")

        self.button1_1.installEventFilter(ToolTipFilter(self.button1_1, 1000))
        self.button1_2.installEventFilter(ToolTipFilter(self.button1_2, 1000))
        self.button2_1.installEventFilter(ToolTipFilter(self.button2_1, 1000))
        self.button3_1.installEventFilter(ToolTipFilter(self.button3_1, 1000))

        self.card1 = GrayCard("一键整理+清理", self.view)
        self.card2 = GrayCard("快捷功能", self.view)
        self.card3 = GrayCard("游戏功能", self.view)

        self.card1.addWidget(self.button1_1)
        self.card1.addWidget(self.button1_2)
        self.card2.addWidget(self.button2_1)
        self.card3.addWidget(self.button3_1)

        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card3, 0, Qt.AlignTop)

    def buttonClicked1_1(self):
        if setting.read("sortPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前未设置整理文件目录，无法整理！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()
            return
        if setting.read("wechatPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "当前未设置微信文件目录，无法整理微信文件！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.button1_1.setEnabled(False)

        self.signalBool.emit(False)

        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()

        self.thread = NewThread("一键整理+清理")
        self.thread.signalBool.connect(self.thread1_1)
        self.thread.start()

    def thread1_1(self, msg):
        self.stateTooltip.setState(True)
        self.button1_1.setEnabled(True)
        self.signalBool.emit(True)
        if msg:
            self.stateTooltip.setContent("整理成功")
        else:
            self.stateTooltip.setContent("整理失败")

    def buttonClicked1_2(self):
        if setting.read("sortPath") != "":
            os.startfile(setting.read("sortPath"))

    def buttonClicked2_1(self):
        self.button2_1.setEnabled(False)

        self.thread = NewThread("重启文件资源管理器")
        self.thread.signalStr.connect(self.thread2_1)
        self.thread.start()

    def thread2_1(self, msg):
        self.button2_1.setEnabled(True)

    def buttonClicked3_1(self):
        self.button3_1.setEnabled(False)

        self.thread = NewThread("Minecraft最新版本")
        self.thread.signalStr.connect(self.thread3_1)
        self.thread.start()
        self.flyout1 = Flyout(FlyoutViewBase())
        self.flyout1.create(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content="正在连接至服务器！",
            target=self.button3_1,
            parent=self,
            isClosable=False,
        )

    def thread3_1(self, msg):
        self.button3_1.setEnabled(True)

        self.flyout2 = Flyout(FlyoutViewBase())
        self.flyout2.create(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content=msg,
            target=self.button3_1,
            parent=self,
            isClosable=True
        )


class ToolPage(BasicTabPage):
    """
    工具页面
    """
    title = "工具"
    subtitle = "实用工具"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.page1 = AppStoreTab()
        self.addPage(self.page1, "应用商店", FIF.SHOPPING_CART)


class GamePage(BasicTabPage):
    """
    游戏页面
    """
    title = "游戏"
    subtitle = "游戏功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.card2 = SmallInfoCard()
        self.card2.setImg("mc.png", "https://static.wikia.nocookie.net/minecraft_zh_gamepedia/images/9/90/Minecraft_Wiki_header.svg/revision/latest/scale-to-width-down/300?cb=20211229051507")
        self.card2.setTitle("标题")
        self.card2.setInfo("左上", 0)
        self.card2.setInfo("左下", 1)
        self.card2.setInfo("右上", 2)
        self.card2.setInfo("右下", 3)

        self.card3 = DisplayCard(self)
        self.card3.setFixedSize(500, 600)
        self.image = Image("linger.png", "https://picdl.sunbangyan.cn/2023/11/14/774ab3fad42612dd6e7a1aa68aef5b09.jpg")
        self.image.setFixedSize(50, 60)
        self.card3.setDisplay(self.image)
        self.card3.setText("123")

        self.page1 = BasicTab()

        self.card1 = BigInfoCard()
        self.card1.setImg("mc.png", "https://static.wikia.nocookie.net/minecraft_zh_gamepedia/images/9/90/Minecraft_Wiki_header.svg/revision/latest/scale-to-width-down/300?cb=20211229051507")
        self.card1.setInfo("介绍Info")
        self.card1.setTitle("标题Title")
        self.card1.addUrl("链接Url", program.UPDATE_URL)
        self.card1.addData("数据Data", "值")
        self.card1.addTag("标签Tag")

        self.page1.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.page1.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.page1.vBoxLayout.addWidget(self.card3, 0, Qt.AlignTop)
        self.addPage(self.page1, "Test", FIF.GAME)


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "设置程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.settingCardGroup1 = SettingCardGroup("个性化", self)
        self.settingCardGroup2 = SettingCardGroup("功能", self)
        self.settingCardGroup3 = SettingCardGroup("关于", self)

        self.themeSettingCard = ThemeSettingCard()
        self.colorSettingCard = ColorSettingCard()
        self.startupSettingCard = StartupSettingCard()
        self.shortcutSettingCard = ShortcutSettingCard()

        self.sortSettingCard = SortSettingCard()

        self.helpSettingCard = HelpSettingCard()
        self.updateSettingCard = UpdateSettingCard()
        self.aboutSettingCard = AboutSettingCard()

        self.settingCardGroup1.addSettingCard(self.themeSettingCard)
        self.settingCardGroup1.addSettingCard(self.colorSettingCard)
        self.settingCardGroup1.addSettingCard(self.startupSettingCard)
        self.settingCardGroup1.addSettingCard(self.shortcutSettingCard)

        self.settingCardGroup2.addSettingCard(self.sortSettingCard)

        self.settingCardGroup3.addSettingCard(self.helpSettingCard)
        self.settingCardGroup3.addSettingCard(self.updateSettingCard)
        self.settingCardGroup3.addSettingCard(self.aboutSettingCard)

        self.vBoxLayout.addWidget(self.settingCardGroup1)
        self.vBoxLayout.addWidget(self.settingCardGroup2)
        self.vBoxLayout.addWidget(self.settingCardGroup3)


class Window(FluentWindow):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("主窗口")

        self.__initWindow()
        self.__initWidget()

        self.__initActivity()

    def __initWindow(self):
        """
        窗口初始化
        """
        # 外观调整
        setTheme(eval(setting.read("theme")))
        setThemeColor("#0078D4")
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.source("logo.png")))
        self.setWindowTitle(program.PROGRAM_TITLE)
        self.navigationInterface.setReturnButtonVisible(False)
        # 窗口居中
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def __initWidget(self):
        """
        组件初始化
        """
        self.mainPage = MainPage(self)
        self.toolPage = ToolPage(self)
        self.gamePage = GamePage(self)
        self.settingPage = SettingPage(self)

        self.addSubInterface(self.mainPage, FIF.HOME, self.mainPage.title, NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.toolPage, FIF.DEVELOPER_TOOLS, self.toolPage.title, NavigationItemPosition.SCROLL)
        self.addSubInterface(self.gamePage, FIF.GAME, self.gamePage.title, NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget("avatar", NavigationAvatarWidget(program.AUTHOR_NAME, program.source("zb.png")), self.avatorEvent, NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settingPage, FIF.SETTING, self.settingPage.title, NavigationItemPosition.BOTTOM)

    def __initActivity(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.repeatOpen)
        self.timer.start(100)

        # 托盘组件
        self.tray = Tray(self)

        if setting.read("autoUpdate") and program.isStartup:
            self.settingPage.updateSettingCard.button3()

    def avatorEvent(self):
        """
        头像点击事件
        """
        w = MessageBox(f"欢迎使用{program.PROGRAM_NAME}！", f"作者：{program.AUTHOR_NAME}", self)
        w.yesButton.setText(f"{program.AUTHOR_NAME}的个人网站")
        w.cancelButton.setText("关闭")
        if w.exec():
            webbrowser.open(program.AUTHOR_URL)

    def repeatOpen(self):
        """
        重复运行展示窗口
        """
        if setting.read("showWindow") == "1":
            setting.save("showWindow", "0")
            self.show()

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key_Escape:
            self.hide()

    def closeEvent(self, QCloseEvent):
        """
        自定义关闭事件
        """
        QCloseEvent.ignore()
        self.hide()


QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
translator = FluentTranslator()
app.installTranslator(translator)
w = Window()
w.show()
if program.isStartup and setting.read("autoHide"):
    w.hide()
app.exec()
