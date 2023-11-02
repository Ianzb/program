from widgets import *


class MainPage(ScrollArea):
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

        self.button1_1.setToolTip("开始整理+清理文件，范围包括：\n·整理桌面文件\n·整理微信文件\n·清空回收站\n·清理系统缓存")
        self.button1_2.setToolTip("")
        self.button1_1.installEventFilter(ToolTipFilter(self.button1_1, 1000, ToolTipPosition.TOP))

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
            self.infoBar = InfoBar(
                icon=InfoBarIcon.WARNING,
                title="提示",
                content="当前未设置整理文件目录，无法整理！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            self.infoBar.show()
            return
        if setting.read("wechatPath") == "":
            self.infoBar = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title="提示",
                content="当前未设置微信文件目录，无法整理微信文件！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            self.infoBar.show()
        self.button1_1.setEnabled(False)
        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        self.thread = NewThread("一键整理+清理")
        self.thread.signalBool.connect(self.thread1_1)
        self.thread.start()

    def thread1_1(self, msg):
        self.stateTooltip.setState(True)
        self.button1_1.setEnabled(True)
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

    def thread3_1(self, msg):
        self.infoBar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content=msg,
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=10000,
            parent=self
        )
        self.infoBar.show()
        self.button3_1.setEnabled(True)


class ToolPage(ScrollArea):
    """
    工具页面
    """
    title = "工具"
    subtitle = "实用工具"

    def __init__(self, parent=None):
        super().__init__(parent=parent)


class GamePage(ScrollArea):
    """
    游戏页面
    """
    title = "游戏"
    subtitle = "游戏功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)


class SettingPage(ScrollArea):
    """
    设置页面
    """
    title = "设置"
    subtitle = "设置程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.settingCardGroup1 = SettingCardGroup("个性化", self)

        self.themeSettingCard = ThemeSettingCard()
        self.settingCardGroup1.addSettingCard(self.themeSettingCard)
        self.colorSettingCard = ColorSettingCard()
        self.settingCardGroup1.addSettingCard(self.colorSettingCard)
        self.startupSettingCard = StartupSettingCard()
        self.settingCardGroup1.addSettingCard(self.startupSettingCard)
        self.shortcutSettingCard = ShortcutSettingCard()
        self.settingCardGroup1.addSettingCard(self.shortcutSettingCard)

        self.vBoxLayout.addWidget(self.settingCardGroup1)

        self.settingCardGroup2 = SettingCardGroup("功能", self)
        self.sortSettingCard = SortSettingCard()
        self.settingCardGroup2.addSettingCard(self.sortSettingCard)
        self.vBoxLayout.addWidget(self.settingCardGroup2)

        self.settingCardGroup3 = SettingCardGroup("关于", self)

        self.helpSettingCard = HelpSettingCard()
        self.settingCardGroup3.addSettingCard(self.helpSettingCard)
        self.updateSettingCard = UpdateSettingCard()
        self.settingCardGroup3.addSettingCard(self.updateSettingCard)
        self.aboutSettingCard = AboutSettingCard()
        self.settingCardGroup3.addSettingCard(self.aboutSettingCard)

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

        # 自动更新
        if setting.read("autoUpdate") and program.isStartup:
            self.settingPage.updateSettingCard.button3()

    def __initWindow(self):
        """
        窗口初始化
        """
        self.thread = NewThread("展示窗口")
        self.thread.signalStr.connect(self.ifShow)
        self.thread.start()
        # 外观调整
        setTheme(eval(setting.read("theme")))
        setThemeColor("#0078D4")
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(500, 400)
        self.setWindowIcon(QIcon(program.source("logo.png")))
        self.setWindowTitle(program.PROGRAM_TITLE)
        self.navigationInterface.setReturnButtonVisible(False)
        # 窗口居中
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 托盘组件
        self.tray = Tray(self)

    def __initWidget(self):
        """
        组件初始化
        """
        # 页面组件
        self.mainPage = MainPage(self)
        self.toolPage = ToolPage(self)
        self.gamePage = GamePage(self)
        self.settingPage = SettingPage(self)
        # 导航栏组件
        self.addSubInterface(self.mainPage, FIF.HOME, self.mainPage.title, NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.toolPage, FIF.DEVELOPER_TOOLS, self.toolPage.title, NavigationItemPosition.SCROLL)
        self.addSubInterface(self.gamePage, FIF.GAME, self.gamePage.title, NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            "avatar",
            NavigationAvatarWidget(program.AUTHOR_NAME, program.source("zb.png")),
            self.avatorEvent,
            NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(self.settingPage, FIF.SETTING, self.settingPage.title, NavigationItemPosition.BOTTOM)

    def avatorEvent(self):
        """
        头像页面事件
        """
        w = MessageBox(
            f"欢迎使用{program.PROGRAM_NAME}！",
            f"作者：{program.AUTHOR_NAME}",
            self
        )
        w.yesButton.setText(f"{program.AUTHOR_NAME}的个人网站")
        w.cancelButton.setText("关闭")
        if w.exec():
            webbrowser.open(program.AUTHOR_URL)

    def ifShow(self, msg):
        """
        重复运行展示窗口
        """
        if msg == "展示窗口":
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
