from .widget import *


class MainPage(BasicTab):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.titleImage = Image("logo.png", "https://ianzb.github.io/project/img/program.png", self, False)
        self.titleImage.setFixedSize(410, 135)
        self.card1 = IntroductionCard(self)
        self.card1.setTitle(f"欢迎使用")
        self.card1.setText(f"一款基于Python的Windows多功能工具箱！")
        self.card1.setImg(program.ICON)

        self.card2 = IntroductionCard(self)
        self.card2.setTitle("插件功能")
        self.card2.setText(f"选择并安装你需要的插件，享受程序功能！")
        self.card2.setImg("Ianzb.png", "https://vip.123pan.cn/1813801926/%E8%B5%84%E6%BA%90/%E4%B8%AA%E4%BA%BA/%E5%A4%B4%E5%83%8F/png/%E5%A4%B4%E5%83%8F%E9%AB%98%E6%B8%85%E9%80%8F%E6%98%8E.png")

        self.card3 = IntroductionCard(self)
        self.card3.setTitle("问题反馈")
        self.card3.setText(f"在Github Issue中提交使用过程中遇到的问题！")
        self.card3.setImg("Github.png", "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png")

        self.flowLayout = FlowLayout()
        self.flowLayout.addWidget(self.card1)
        self.flowLayout.addWidget(self.card2)
        self.flowLayout.addWidget(self.card3)

        self.vBoxLayout.addWidget(self.titleImage, 0, Qt.AlignCenter)
        self.vBoxLayout.addLayout(self.flowLayout, Qt.AlignCenter)

        self.cardGroup1 = CardGroup(self)
        self.addonSettingCard = AddonSettingCard(self)
        self.cardGroup1.addWidget(self.addonSettingCard)
        self.vBoxLayout.addWidget(self.cardGroup1)


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "个性化设置程序功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.SETTING)

        self.cardGroup1 = CardGroup("外观", self)
        self.cardGroup2 = CardGroup("行为", self)
        self.cardGroup3 = CardGroup("功能", self)

        self.themeSettingCard = ThemeSettingCard(self)
        self.colorSettingCard = ColorSettingCard(self)
        self.micaEffectSettingCard = MicaEffectSettingCard(self)

        self.startupSettingCard = StartupSettingCard(self)
        self.traySettingCard = TraySettingCard(self)
        self.hideSettingCard = HideSettingCard(self)

        self.downloadSettingCard = DownloadSettingCard(self)

        self.cardGroup1.addWidget(self.themeSettingCard)
        self.cardGroup1.addWidget(self.colorSettingCard)
        self.cardGroup1.addWidget(self.micaEffectSettingCard)

        self.cardGroup2.addWidget(self.startupSettingCard)
        self.cardGroup2.addWidget(self.traySettingCard)
        self.cardGroup2.addWidget(self.hideSettingCard)

        self.cardGroup3.addWidget(self.downloadSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup3, 0, Qt.AlignTop)

        if not (program.WINDOWS_VERSION[0] >= 10 and program.WINDOWS_VERSION[2] >= 22000):
            self.micaEffectSettingCard.hide()


class AboutPage(BasicPage):
    """
    关于页面
    """
    title = "关于"
    subtitle = "程序运行状态及相关信息"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.INFO)

        self.cardGroup1 = CardGroup("关于", self)

        self.updateSettingCard = UpdateSettingCard(self)
        self.helpSettingCard = HelpSettingCard(self)
        self.controlSettingCard = ControlSettingCard(self)
        self.aboutSettingCard = AboutSettingCard(self)

        self.cardGroup1.addWidget(self.updateSettingCard)
        self.cardGroup1.addWidget(self.helpSettingCard)
        self.cardGroup1.addWidget(self.controlSettingCard)
        self.cardGroup1.addWidget(self.aboutSettingCard)

        self.bigInfoCard = BigInfoCard(self, data=False)
        self.bigInfoCard.setImg("Ianzb.png", "https://vip.123pan.cn/1813801926/%E8%B5%84%E6%BA%90/%E4%B8%AA%E4%BA%BA/%E5%A4%B4%E5%83%8F/png/%E5%A4%B4%E5%83%8F%E9%AB%98%E6%B8%85%E9%80%8F%E6%98%8E.png")
        self.bigInfoCard.image.setMinimumSize(150, 150)
        self.bigInfoCard.setTitle(program.AUTHOR_NAME)
        self.bigInfoCard.setInfo("Minecraft玩家，科幻迷，编程爱好者！")
        self.bigInfoCard.addUrl("Github", "https://github.com/Ianzb", FIF.GITHUB)
        self.bigInfoCard.addUrl("Bilibili", "https://space.bilibili.com/1043835434", FIF.LINK)
        self.bigInfoCard.addTag("Minecraft")
        self.bigInfoCard.addTag("编程")
        self.bigInfoCard.addTag("科幻")
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.setText("个人网站")
        self.bigInfoCard.mainButton.clicked.connect(lambda: webbrowser.open(program.AUTHOR_URL))
        self.bigInfoCard.mainButton.setIcon(FIF.LINK)

        self.vBoxLayout.addWidget(self.bigInfoCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)


class Window(FluentWindow, SignalBase):
    """
    主窗口
    """
    ADDON_IMPORT = {}  # 导入的插件的对象
    ADDON_MAINPAGE = {}  # 导入的插件的主页
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
        setTheme(eval(setting.read("theme")), lazy=True)
        setThemeColor("#0078D4", lazy=True)
        self.navigationInterface.setAcrylicEnabled(True)
        self.setMicaEffectEnabled(setting.read("micaEffect"))
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.ICON))
        self.setWindowTitle(program.TITLE)
        self.navigationInterface.setReturnButtonVisible(False)
        # 窗口居中
        desktop = QApplication.screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def __initWidget(self):
        """
        组件初始化
        """
        self.mainPage = MainPage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)

        self.addPage(self.mainPage, "top")
        self.addSeparator("top")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, "bottom")
        self.addPage(self.aboutPage, "bottom")

    def __initActivity(self):
        # 报错检测
        if program.isExe:
            sys.excepthook = self.getException
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(250)

        # 托盘组件
        self.tray = Tray(self)
        self.tray.setVisible(setting.read("showTray"))

        # 插件安装
        self.addAddon(f.getInstalledAddonInfo())

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key.Key_Escape:
            if setting.read("hideWhenClose"):
                self.hide()

    def closeEvent(self, QCloseEvent):
        """
        自定义关闭事件
        """
        QCloseEvent.ignore()
        if setting.read("hideWhenClose"):
            self.hide()
        else:
            program.close()

    def getException(self, type, value, traceback):
        """
        报错拦截
        @param type: 报错类型
        @param value: 报错对象
        @param traceback: 报错返回信息
        """
        info = "".join(format_exception(type, value, traceback))
        logging.fatal(f"程序发生异常\n{info}")
        self.messageBox = MessageBox("程序发生异常", info, self)
        self.messageBox.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.messageBox.yesButton.setText("重启")
        self.messageBox.yesButton.setIcon(FIF.SYNC)
        self.messageBox.yesButton.clicked.connect(program.restart)
        self.messageBox.cancelButton.setText("关闭")
        self.messageBox.exec()

    def addPage(self, page, pos: str):
        """
        添加导航栏页面简易版
        @param page: 页面对象
        @param pos: 位置top/scroll/bottom
        """
        return self.addSubInterface(page, page.icon(), page.objectName(), eval(f"NavigationItemPosition.{pos.upper()}"))

    def addSeparator(self, pos: str):
        """
        添加导航栏分割线简易版
        @param pos: 位置top/scroll/bottom
        """
        self.navigationInterface.addSeparator(eval(f"NavigationItemPosition.{pos.upper()}"))

    def addAddon(self, msg):
        """
        添加插件
        @param msg: 数据
        """
        if "id" in msg.keys():
            self.__addAddon(msg)
        else:
            for v in msg.values():
                self.__addAddon(v)

    def removeAddon(self, msg):
        """
        移除插件
        @param msg: 数据
        """
        if "id" in msg.keys():
            self.__removeAddon(msg)
        else:
            for v in msg.values():
                self.__removeAddon(v)

    def __addAddon(self, data):
        """
        添加插件
        @param data: 数据
        """
        try:
            if data["id"] in self.ADDON_IMPORT.keys():
                self.navigationInterface.removeWidget(data["name"])
                self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE[data["id"]])
                self.ADDON_MAINPAGE[data["id"]].deleteLater()
                del self.ADDON_IMPORT[data["id"]]
                del self.ADDON_MAINPAGE[data["id"]]

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}更新成功，重启程序生效！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.button1 = PushButton("重启", self, FIF.SYNC)
                self.button1.clicked.connect(program.restart)
                self.button1.setToolTip("重启程序")
                self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
                self.infoBar.addWidget(self.button1)
                self.infoBar.show()
            else:
                self.ADDON_IMPORT[data["id"]] = importlib.import_module(data["id"])
                self.ADDON_MAINPAGE[data["id"]] = self.ADDON_IMPORT[data["id"]].AddonPage(self)
                self.ADDON_MAINPAGE[data["id"]].setObjectName(data["name"])
                self.addPage(self.ADDON_MAINPAGE[data["id"]], "scroll")

                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}安装成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.mainPage)
                self.infoBar.show()
            logging.warning(f"插件{data["name"]}安装成功")
        except Exception as ex:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data["name"]}安装失败{ex}！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.mainPage)
            self.infoBar.show()

            logging.warning(f"插件{data["name"]}安装失败{ex}")

    def __removeAddon(self, data):
        """
        移除插件
        @param data: 数据
        """
        if data["id"] in self.ADDON_IMPORT.keys():
            self.navigationInterface.removeWidget(data["name"])
            self.stackedWidget.view.removeWidget(self.ADDON_MAINPAGE[data["id"]])
            self.ADDON_MAINPAGE[data["id"]].deleteLater()
            del self.ADDON_IMPORT[data["id"]]
            del self.ADDON_MAINPAGE[data["id"]]
        f.cmd(f"del /F /Q /S {f.pathJoin(program.ADDON_PATH, data["id"])}", True)
        f.delete(f.pathJoin(program.ADDON_PATH, data["id"]))
        logging.info(f"插件{data["name"]}删除成功")

        self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}删除成功！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.settingPage)
        self.infoBar.show()

    def timerEvent(self):
        """
        重复运行展示窗口
        """
        if f.existPath(f.pathJoin(program.DATA_PATH, "zb.unlock")):
            f.delete(f.pathJoin(program.DATA_PATH, "zb.unlock"))
            self.show()


logging.debug("window.py初始化成功")
