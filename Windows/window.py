from widgets import *


class MainPage(ScrollArea):
    """
    主页
    """
    name = "主页"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.toolBar = ToolBar(self.name, "常用功能", self)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.view = QWidget(self)
        self.setWidget(self.view)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)
        self.setWidgetResizable(True)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)

        self.pushButton1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.pushButton1_1.clicked.connect(self.button1_1)
        self.pushButton1_2 = ToolButton(FIF.FOLDER, self)
        self.pushButton1_2.clicked.connect(self.button1_2)
        self.pushButton1_3 = PushButton("设置整理目录", self, FIF.FOLDER_ADD)
        self.pushButton1_3.clicked.connect(self.button1_3)
        self.pushButton1_4 = PushButton("设置微信目录", self, FIF.FOLDER_ADD)
        self.pushButton1_4.clicked.connect(self.button1_4)

        self.pushButton2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.pushButton2_1.clicked.connect(self.button2_1)

        self.pushButton3_1 = PushButton("查看Minecraft最新版本", self, FIF.CHECKBOX)
        self.pushButton3_1.clicked.connect(self.button3_1)

        self.card1 = GrayCard("一键整理+清理", [self.pushButton1_1, self.pushButton1_2, self.pushButton1_3, self.pushButton1_4], self.view)
        self.card2 = GrayCard("快捷功能", [self.pushButton2_1], self.view)
        self.card3 = GrayCard("游戏功能", [self.pushButton3_1], self.view)
        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card3, 0, Qt.AlignTop)

    def button1_1(self):
        if setting.read("sortPath") == "":
            self.infoBar = InfoBar(
                icon=InfoBarIcon.WARNING,
                title="提示",
                content="当前未设置整理文件目录，无法整理！",
                orient=Qt.Horizontal,
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
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            self.infoBar.show()
        self.pushButton1_1.setEnabled(False)
        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        self.thread = NewThread("一键整理+清理")
        self.thread.signalBool.connect(self.thread1_1)
        self.thread.start()

    def thread1_1(self, msg):
        self.stateTooltip.setState(True)
        self.pushButton1_1.setEnabled(True)
        if msg:
            self.stateTooltip.setContent("整理成功")
        else:
            self.stateTooltip.setContent("整理失败")

    def button1_2(self):
        if setting.read("sortPath") != "":
            os.startfile(setting.read("sortPath"))

    def button1_3(self):
        get = QFileDialog.getExistingDirectory(self, "选择整理目录", setting.read("sortPath"))
        if os.path.exists(get):
            setting.save("sortPath", str(get))

    def button1_4(self):
        get = QFileDialog.getExistingDirectory(self, "选择微信WeChat Files文件夹目录", setting.read("wechatPath"))
        if os.path.exists(get):
            setting.save("wechatPath", str(get))

    def button2_1(self):
        self.pushButton2_1.setEnabled(False)
        self.thread = NewThread("重启文件资源管理器")
        self.thread.signalStr.connect(self.thread2_1)
        self.thread.start()

    def thread2_1(self, msg):
        self.pushButton2_1.setEnabled(True)

    def button3_1(self):
        self.pushButton3_1.setEnabled(False)
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
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=10000,
            parent=self
        )
        self.infoBar.show()
        self.pushButton3_1.setEnabled(True)


class ToolPage(ScrollArea):
    """
    工具页面
    """
    name = "工具"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.toolBar = ToolBar(self.name, "工具箱", self)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.view = QWidget(self)
        self.setWidget(self.view)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)
        self.setWidgetResizable(True)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)


class GamePage(ScrollArea):
    """
    游戏页面
    """
    name = "游戏"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.toolBar = ToolBar(self.name, "Minecraft相关功能", self)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.view = QWidget(self)
        self.setWidget(self.view)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)
        self.setWidgetResizable(True)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)


class SettingPage(ScrollArea):
    """
    设置页面
    """
    name = "设置"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.toolBar = ToolBar(self.name, "个性化修改程序", self)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.view = QWidget(self)
        self.setWidget(self.view)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.toolBar.height(), 0, 0)
        self.setWidgetResizable(True)

        self.vBoxLayout = VBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)

        self.settingCardGroup1 = SettingCardGroup("个性化", self)

        self.settingCardGroup1.addSettingCard(ThemeSettingCard())
        self.settingCardGroup1.addSettingCard(ColorSettingCard())
        self.settingCardGroup1.addSettingCard(StartupSettingCard())
        self.settingCardGroup1.addSettingCard(ShortcutSettingCard())

        self.vBoxLayout.addWidget(self.settingCardGroup1)

        self.settingCardGroup2 = SettingCardGroup("关于", self)

        self.settingCardGroup2.addSettingCard(HelpSettingCard())
        self.updateSettingCard = UpdateSettingCard()
        self.settingCardGroup2.addSettingCard(self.updateSettingCard)
        self.settingCardGroup2.addSettingCard(AboutSettingCard())

        self.vBoxLayout.addWidget(self.settingCardGroup2)


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
        self.addSubInterface(self.mainPage, FIF.HOME, self.mainPage.name, NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.toolPage, FIF.DEVELOPER_TOOLS, self.toolPage.name, NavigationItemPosition.SCROLL)
        self.addSubInterface(self.gamePage, FIF.GAME, self.gamePage.name, NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            "avatar",
            NavigationAvatarWidget(program.AUTHOR_NAME, program.source("zb.png")),
            self.avatorEvent,
            NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(self.settingPage, FIF.SETTING, self.settingPage.name, NavigationItemPosition.BOTTOM)

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
