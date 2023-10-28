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

        self.card = HeaderCardWidget()
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignTop)

        self.btn = PrimaryPushButton("zb", self.card.view, FIF.ALIGNMENT)

        self.card2 = GrayCard("123", self.btn, self.view)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)


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
        if setting.read("autoUpdate"):
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
