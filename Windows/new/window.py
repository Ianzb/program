from widgets import *


class mainPage(ScrollArea):
    """
    主页
    """
    name = "主页"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.TitleLabel = ToolBar(self.name,"常用功能", self)


class toolPage(ScrollArea):
    """
    工具页面
    """
    name = "工具"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.TitleLabel = ToolBar(self.name,"工具箱", self)


class gamePage(ScrollArea):
    """
    游戏页面
    """
    name = "游戏"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.TitleLabel = ToolBar(self.name,"Minecraft相关功能", self)


class settingPage(ScrollArea):
    """
    设置页面
    """
    name = "设置"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.name)
        self.TitleLabel = ToolBar(self.name,"", self)


class Window(FluentWindow):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("主窗口")
        self.__initWindow()
        self.__initWidget()

    def __initWindow(self):
        """
        窗口初始化
        """
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

    def __initWidget(self):
        """
        组件初始化
        """
        # 页面组件
        self.mainPage = mainPage(self)
        self.toolPage = toolPage(self)
        self.gamePage = gamePage(self)
        self.settingPage = settingPage(self)
        # 导航栏组件
        self.addSubInterface(self.mainPage, FIF.HOME, self.mainPage.name, NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.toolPage, FIF.DEVELOPER_TOOLS, self.toolPage.name, NavigationItemPosition.SCROLL)
        self.addSubInterface(self.gamePage, FIF.GAME, self.gamePage.name, NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=NavigationAvatarWidget("Ianzb", program.source("zb.png")),
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(self.settingPage, FIF.SETTING, self.settingPage.name, NavigationItemPosition.BOTTOM)
