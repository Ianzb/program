from .widget import *


class MainPage(BasicPage):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.button1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.button1_1.clicked.connect(self.button1_1Clicked)
        self.button1_1.setToolTip("开始整理+清理文件，范围包括：\n  整理桌面文件\n  整理微信文件\n  清空回收站\n  清理系统缓存")
        self.button1_1.installEventFilter(ToolTipFilter(self.button1_1, 1000))

        self.button1_2 = ToolButton(FIF.FOLDER, self)
        self.button1_2.clicked.connect(lambda: f.showFile(setting.read("sortPath")))
        self.button1_2.setToolTip("打开整理文件所在目录")
        self.button1_2.installEventFilter(ToolTipFilter(self.button1_2, 1000))

        self.button2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.button2_1.clicked.connect(self.button2_1Clicked)
        self.button2_1.setToolTip("重启文件资源管理器")
        self.button2_1.installEventFilter(ToolTipFilter(self.button2_1, 1000))

        self.button3_1 = PushButton("查看Minecraft最新版本", self, FIF.CHECKBOX)
        self.button3_1.clicked.connect(self.button3_1Clicked)
        self.button3_1.setToolTip("查看Minecraft最新版本，数据来源：\n  我的世界中文维基百科（https://zh.minecraft.wiki/）")
        self.button3_1.installEventFilter(ToolTipFilter(self.button3_1, 1000))

        self.card1 = GrayCard("一键整理+清理", self.view)
        self.card1.addWidget(self.button1_1)
        self.card1.addWidget(self.button1_2)

        self.card2 = GrayCard("快捷功能", self.view)
        self.card2.addWidget(self.button2_1)

        self.card3 = GrayCard("游戏功能", self.view)
        self.card3.addWidget(self.button3_1)

        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.card3, 0, Qt.AlignmentFlag.AlignTop)

    def button1_1Clicked(self):
        if setting.read("sortPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前未设置整理文件目录，无法整理！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()
            return
        if setting.read("wechatPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "当前未设置微信文件目录，无法整理微信文件！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.button1_1.setEnabled(False)

        self.signalBool.emit(False)

        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()

        self.thread1_1 = NewThread("一键整理+清理")
        self.thread1_1.signalBool.connect(self.threadEvent1_1)
        self.thread1_1.start()

    def threadEvent1_1(self, msg):
        self.stateTooltip.setState(True)
        self.button1_1.setEnabled(True)
        self.signalBool.emit(True)
        if msg:
            self.stateTooltip.setContent("整理成功")
        else:
            self.stateTooltip.setContent("整理失败")

    def button2_1Clicked(self):
        self.button2_1.setEnabled(False)

        self.thread2_1 = NewThread("重启文件资源管理器")
        self.thread2_1.signalStr.connect(self.threadEvent2_1)
        self.thread2_1.start()

    def threadEvent2_1(self, msg):
        self.button2_1.setEnabled(True)

    def button3_1Clicked(self):
        self.button3_1.setEnabled(False)

        self.thread3_1 = NewThread("Minecraft最新版本")
        self.thread3_1.signalStr.connect(self.threadEvent3_1)
        self.thread3_1.start()
        self.flyout1 = AcrylicFlyout(FlyoutViewBase())
        self.flyout1.create(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content="正在连接至服务器！",
            target=self.button3_1,
            parent=self,
            isClosable=False,
        )

    def threadEvent3_1(self, msg):
        self.button3_1.setEnabled(True)

        self.flyout2 = AcrylicFlyout(FlyoutViewBase())
        self.flyout2.create(
            icon=InfoBarIcon.INFORMATION,
            title="Minecraft最新版本",
            content=msg,
            target=self.button3_1,
            parent=self,
            isClosable=True
        )


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "设置程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.SETTING)

        self.cardGroup1 = CardGroup("插件", self)
        self.cardGroup2 = CardGroup("外观", self)
        self.cardGroup3 = CardGroup("行为", self)
        self.cardGroup4 = CardGroup("功能", self)

        self.addonSettingCard = AddonSettingCard(self)

        self.themeSettingCard = ThemeSettingCard(self)
        self.colorSettingCard = ColorSettingCard(self)
        self.micaEffectSettingCard = MicaEffectSettingCard(self)

        self.startupSettingCard = StartupSettingCard(self)
        self.traySettingCard = TraySettingCard(self)
        self.hideSettingCard = HideSettingCard(self)

        self.sortSettingCard = SortPathSettingCard(self)
        self.sortFolderSettingCard = SortSettingCard(self)
        self.downloadSettingCard = DownloadSettingCard(self)

        self.cardGroup1.addWidget(self.addonSettingCard)

        self.cardGroup2.addWidget(self.themeSettingCard)
        self.cardGroup2.addWidget(self.colorSettingCard)
        self.cardGroup2.addWidget(self.micaEffectSettingCard)

        self.cardGroup3.addWidget(self.startupSettingCard)
        self.cardGroup3.addWidget(self.traySettingCard)
        self.cardGroup3.addWidget(self.hideSettingCard)

        self.cardGroup4.addWidget(self.sortSettingCard)
        self.cardGroup4.addWidget(self.sortFolderSettingCard)
        self.cardGroup4.addWidget(self.downloadSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup3, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup4, 0, Qt.AlignmentFlag.AlignTop)


class AboutPage(BasicPage):
    """
    关于页面
    """
    title = "关于"
    subtitle = "关于程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.INFO)

        self.cardGroup1 = CardGroup("关于", self)

        self.updateSettingCard = UpdateSettingCard(self)
        self.helpSettingCard = HelpSettingCard(self)
        self.controlSettingCard = ControlSettingCard(self)
        self.shortcutSettingCard = ShortcutSettingCard(self)
        self.aboutSettingCard = AboutSettingCard(self)

        self.cardGroup1.addWidget(self.updateSettingCard)
        self.cardGroup1.addWidget(self.helpSettingCard)
        self.cardGroup1.addWidget(self.controlSettingCard)
        self.cardGroup1.addWidget(self.shortcutSettingCard)
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

        self.vBoxLayout.addWidget(self.bigInfoCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignmentFlag.AlignTop)


class Window(FluentWindow):
    """
    主窗口
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self):
        super().__init__()

        self.__initWindow()
        self.__initWidget()
        self.__initActivity()
        self.updateFrameless()
        self.setMicaEffectEnabled(True)

    def __initWindow(self):
        """
        窗口初始化
        """

        # 外观调整
        setTheme(eval(setting.read("theme")))
        setThemeColor("#0078D4")
        self.navigationInterface.setAcrylicEnabled(True)
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.PROGRAM_ICON))
        self.setWindowTitle(f"{program.PROGRAM_TITLE} {setting.read('updateChannel')}")
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

        from .web_ui import AddonPage
        self.addPage(AddonPage(self), "scroll")
        from .mc_ui import AddonPage
        self.addPage(AddonPage(self), "scroll")


    def __initActivity(self):
        # 报错检测
        sys.excepthook = self.getException
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.detectRepeatRun)
        self.timer.start(100)

        # 托盘组件
        self.tray = Tray(self)
        self.tray.setVisible(setting.read("showTray"))

        self.setMicaEffectEnabled(setting.read("micaEffect"))
        if setting.read("autoUpdate") and program.isStartup:
            self.aboutPage.updateSettingCard.setEnabled(False)
            self.thread1 = NewThread("更新运行库")
            self.thread1.start()
            self.thread2 = NewThread("立刻更新")
            self.thread2.signalDict.connect(self.autoUpdateFinish)
            self.thread2.signalBool.connect(self.autoUpdateFinish)
            self.thread2.start()

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
        self.addSubInterface(page, page.icon, page.title, eval(f"NavigationItemPosition.{pos.upper()}"))

    def addSeparator(self, pos: str):
        """
        添加导航栏分割线简易版
        @param pos: 位置top/scroll/bottom
        """
        self.navigationInterface.addSeparator(eval(f"NavigationItemPosition.{pos.upper()}"))

    def addAddon(self, msg):
        """
        添加插件
        @param data: 数据
        """
        if "id" in msg.keys():
            self.__addAddon(msg)
        else:
            for v in msg.values():
                self.__addAddon(v)

    def removeAddon(self, msg):
        """
        移除插件
        @param data: 数据
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
        sys.path = [program.ADDON_PATH] + sys.path
        import importlib
        try:
            lib = importlib.import_module(data["id"])
            self.page = lib.AddonPage(self)
            if not self.page.title:
                self.page.title = data["name"]
            self.addPage(self.page, "scroll")
        except Exception as ex:
            logging.warning(f"插件{data['name']}安装失败{ex}")

    def __removeAddon(self, data):
        """
        移除插件
        @param data: 数据
        """
        f.cmd(f"del /F /Q {f.pathJoin(program.ADDON_PATH, data['id'])}", True)
        f.delete(f.pathJoin(program.ADDON_PATH, data["id"]))
        logging.info(f"插件{data['name']}删除成功")

        self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data['name']}删除成功！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.settingPage)

        self.button1 = PushButton("重启", self, FIF.SYNC)
        self.button1.clicked.connect(program.restart)

        self.infoBar.addWidget(self.button1)
        self.infoBar.show()

    def autoUpdateFinish(self, msg):
        """
        开机自动更新完成解锁组件
        """
        if isinstance(msg, bool):
            self.aboutPage.updateSettingCard.setEnabled(True)
        if isinstance(msg, dict):
            if msg["完成"]:
                self.aboutPage.updateSettingCard.setEnabled(True)

    def detectRepeatRun(self):
        """
        重复运行展示窗口
        """
        if f.existPath(f.pathJoin(program.PROGRAM_DATA_PATH, "zb.unlock")):
            f.delete(f.pathJoin(program.PROGRAM_DATA_PATH, "zb.unlock"))
            self.show()


logging.debug("window.py初始化成功")
