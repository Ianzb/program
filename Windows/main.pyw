from window import *


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
