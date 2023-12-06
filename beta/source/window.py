from .widget import *


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

        self.button1_1.clicked.connect(self.button1_1Clicked)
        self.button1_2.clicked.connect(lambda: f.startFile(setting.read("sortPath")))
        self.button2_1.clicked.connect(self.button2_1Clicked)
        self.button3_1.clicked.connect(self.button3_1Clicked)

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

    def button1_1Clicked(self):
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

    def button2_1Clicked(self):
        self.button2_1.setEnabled(False)

        self.thread = NewThread("重启文件资源管理器")
        self.thread.signalStr.connect(self.thread2_1)
        self.thread.start()

    def thread2_1(self, msg):
        self.button2_1.setEnabled(True)

    def button3_1Clicked(self):
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
        from .addon.appstore import AppStoreTab
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


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "设置程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.cardGroup1 = CardGroup("个性化", self)
        self.cardGroup2 = CardGroup("功能", self)
        self.cardGroup3 = CardGroup("关于", self)

        self.themeSettingCard = ThemeSettingCard()
        self.colorSettingCard = ColorSettingCard()
        self.startupSettingCard = StartupSettingCard()
        self.shortcutSettingCard = ShortcutSettingCard()

        self.sortSettingCard = SortSettingCard()
        self.sortBlacklistSettingCard = SortBlacklistSettingCard()
        self.downloadSettingCard = DownloadSettingCard()

        self.helpSettingCard = HelpSettingCard()
        self.updateSettingCard = UpdateSettingCard()
        self.aboutSettingCard = AboutSettingCard()

        self.cardGroup1.addWidget(self.themeSettingCard)
        self.cardGroup1.addWidget(self.colorSettingCard)
        self.cardGroup1.addWidget(self.startupSettingCard)
        self.cardGroup1.addWidget(self.shortcutSettingCard)

        self.cardGroup2.addWidget(self.sortSettingCard)
        self.cardGroup2.addWidget(self.sortBlacklistSettingCard)
        self.cardGroup2.addWidget(self.downloadSettingCard)

        self.cardGroup3.addWidget(self.helpSettingCard)
        self.cardGroup3.addWidget(self.updateSettingCard)
        self.cardGroup3.addWidget(self.aboutSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1)
        self.vBoxLayout.addWidget(self.cardGroup2)
        self.vBoxLayout.addWidget(self.cardGroup3)


class ChatPage(BasicPage):
    title = "PyChat"
    subtitle = "Python实现的在线聊天"

    def __init__(self, parent=None):
        super().__init__(parent)


class Window(FluentWindow):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()

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
        self.setWindowIcon(QIcon(program.PROGRAM_ICON))
        self.setWindowTitle(f"{program.PROGRAM_TITLE} {setting.read("updateChannel")}")
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
        self.chatPage = ChatPage(self)

        self.addSubInterface(self.mainPage, FIF.HOME, self.mainPage.title, NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.toolPage, FIF.DEVELOPER_TOOLS, self.toolPage.title, NavigationItemPosition.SCROLL)
        self.addSubInterface(self.gamePage, FIF.GAME, self.gamePage.title, NavigationItemPosition.SCROLL)
        self.addSubInterface(self.chatPage, FIF.CHAT, self.chatPage.title, NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget("avatar", NavigationAvatarWidget(program.AUTHOR_NAME, program.source("zb.png")), None, NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settingPage, FIF.SETTING, self.settingPage.title, NavigationItemPosition.BOTTOM)

    def __initActivity(self):
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.repeatOpen)
        self.timer.start(100)

        # 托盘组件
        self.tray = Tray(self)

        if setting.read("autoUpdate") and program.isStartup:
            self.settingPage.updateSettingCard.button3Clicked()
        if program.PYTHON_VERSION.split(".")[1] != "12":
            QMessageBox(QMessageBox.Warning, "警告", f"当前Python版本为{program.PYTHON_VERSION}，{program.PROGRAM_NAME}推荐使用Python3.12版本！").exec()

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
