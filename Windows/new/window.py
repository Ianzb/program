from widgets import *


class mainPage(ScrollArea):
    """
    主页
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("主页")
        self.TitleLabel = TitleLabel(program.PROGRAM_NAME, self)


class toolPage(ScrollArea):
    """
    Minecraft页面
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("工具")


class minecraftPage(ScrollArea):
    """
    Minecraft页面
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Minecraft")


class settingPage(ScrollArea):
    """
    设置页面
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("设置")


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
        # 窗口居中
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.navigationInterface.setReturnButtonVisible(False)

    def __initWidget(self):
        """
        组件初始化
        """
        self.addSubInterface(mainPage(self), FIF.HOME, "主页", NavigationItemPosition.TOP)
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(toolPage(self), FIF.DEVELOPER_TOOLS, "工具", NavigationItemPosition.SCROLL)
        self.addSubInterface(minecraftPage(self), FIF.GAME, "Minecraft", NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=NavigationAvatarWidget("Ianzb", program.source("zb.png")),
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(settingPage(self), FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)
