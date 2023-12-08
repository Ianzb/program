from .custom import *


class BlackListEditMessageBox(MessageBoxBase):
    """
    可编辑黑名单的弹出框
    """

    def __init__(self, title: str, tip: str, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(title, self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText(tip)
        self.textEdit.setText("\n".join(setting.read("sortBlacklist")))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortBlacklist", sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText()).split("\n") if i]))))

        self.accept()
        self.accepted.emit()


class ThemeSettingCard(ExpandSettingCard):
    """
    主题设置卡片
    """
    themeChanged = pyqtSignal(OptionsConfigItem)

    def __init__(self, parent=None):
        super().__init__(FIF.BRUSH, "程序主题", "修改程序明暗主题", parent)
        self.label = QLabel(self)

        self.addWidget(self.label)

        self.radioButton1 = RadioButton("浅色", self.view)
        self.radioButton2 = RadioButton("深色", self.view)
        self.radioButton3 = RadioButton("跟随系统设置", self.view)

        self.radioButton1.setToolTip("设置浅色模式")
        self.radioButton2.setToolTip("设置深色模式")
        self.radioButton3.setToolTip("设置跟随系统模式")

        self.radioButton1.installEventFilter(ToolTipFilter(self.radioButton1, 1000))
        self.radioButton2.installEventFilter(ToolTipFilter(self.radioButton2, 1000))
        self.radioButton3.installEventFilter(ToolTipFilter(self.radioButton3, 1000))

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

        self.buttonGroup.addButton(self.radioButton1)
        self.buttonGroup.addButton(self.radioButton2)
        self.buttonGroup.addButton(self.radioButton3)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        self.viewLayout.addWidget(self.radioButton1)
        self.viewLayout.addWidget(self.radioButton2)
        self.viewLayout.addWidget(self.radioButton3)

        if setting.read("theme") == "Theme.LIGHT":
            self.radioButton1.setChecked(True)
            self.label.setText("浅色")
        elif setting.read("theme") == "Theme.DARK":
            self.radioButton2.setChecked(True)
            self.label.setText("深色")
        else:
            self.radioButton3.setChecked(True)
            self.label.setText("跟随系统设置")

        self._adjustViewSize()

    def buttonGroupClicked(self, button: RadioButton):
        if button.text() == self.label.text():
            return
        if button is self.radioButton1:
            setting.save("theme", "Theme.LIGHT")
            setTheme(Theme.LIGHT)
        elif button is self.radioButton2:
            setting.save("theme", "Theme.DARK")
            setTheme(Theme.DARK)
        else:
            setting.save("theme", "Theme.AUTO")
            setTheme(Theme.AUTO)

        self.label.setText(button.text())
        self.label.adjustSize()


class ColorSettingCard(ExpandGroupSettingCard):
    """
    主题色设置卡片
    """
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(FIF.PALETTE, "主题色", "修改程序的主题色", parent=parent)
        self.label1 = QLabel(self)

        self.addWidget(self.label1)

        self.radioWidget = QWidget(self.view)

        self.customColorWidget = QWidget(self.view)
        self.customColorLayout = QHBoxLayout(self.customColorWidget)

        self.label2 = QLabel("自定义颜色", self.customColorWidget)

        self.radioLayout = QVBoxLayout(self.radioWidget)

        self.radioLayout.setSpacing(19)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 18, 0, 18)
        self.radioLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.button1 = RadioButton("默认", self.radioWidget)
        self.button2 = RadioButton("自定义", self.radioWidget)
        self.button3 = QPushButton("选择颜色", self.customColorWidget)

        self.button1.setToolTip("设置默认颜色")
        self.button2.setToolTip("设置自定义颜色")
        self.button3.setToolTip("选择自定义颜色")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.radioLayout.addWidget(self.button1)
        self.radioLayout.addWidget(self.button2)

        self.buttonGroup = QButtonGroup(self)

        self.buttonGroup.addButton(self.button1)
        self.buttonGroup.addButton(self.button2)

        self.customColorLayout.setContentsMargins(48, 18, 44, 18)
        self.customColorLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.customColorLayout.addWidget(self.label2, 0, Qt.AlignLeft)
        self.customColorLayout.addWidget(self.button3, 0, Qt.AlignRight)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.addGroupWidget(self.radioWidget)
        self.addGroupWidget(self.customColorWidget)

        self._adjustViewSize()

        if setting.read("themeColor") == "#0078D4":
            self.button1.setChecked(True)
            self.button3.setEnabled(False)
        else:
            self.button2.setChecked(True)
            self.button3.setEnabled(True)
        self.color = QColor(setting.read("themeColor"))
        setThemeColor(self.color.name())
        self.label1.setText(self.buttonGroup.checkedButton().text())
        self.label1.adjustSize()

        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)
        self.button3.clicked.connect(self.showColorDialog)

    def buttonGroupClicked(self, button: RadioButton):
        if button.text() == self.label1.text():
            return

        self.label1.setText(button.text())
        self.label1.adjustSize()

        if button is self.button1:
            self.button3.setDisabled(True)
            setting.save("themeColor", "#0078D4")
            setThemeColor("#0078D4")
        else:
            self.button3.setDisabled(False)
            setting.save("themeColor", self.color.name())
            setThemeColor(self.color.name())

    def showColorDialog(self):
        colorDialog = ColorDialog(setting.read("themeColor"), "选择颜色", self.window())
        colorDialog.colorChanged.connect(self.__colorChanged)
        colorDialog.exec()

    def __colorChanged(self, color):
        setThemeColor(color)
        self.color = QColor(color)
        setting.save("themeColor", self.color.name())
        self.colorChanged.emit(color)


class StartupSettingCard(SettingCard):
    """
    开机自启动设置卡片
    """
    clicked = pyqtSignal()

    def __init__(self, parent=None):

        super().__init__(FIF.POWER_BUTTON, "开机自启动", "设置程序的开机自启动功能", parent)
        self.checkBox1 = CheckBox("开机自启动", self)
        self.checkBox2 = CheckBox("最小化启动", self)
        self.checkBox3 = CheckBox("开机自动更新", self)

        self.checkBox1.clicked.connect(self.button1Clicked)
        self.checkBox2.clicked.connect(self.button2Clicked)
        self.checkBox3.clicked.connect(self.button3Clicked)

        self.checkBox1.setToolTip("设置程序开机自启动")
        self.checkBox2.setToolTip("设置程序在开机自启动时自动最小化窗口")
        self.checkBox3.setToolTip("设置程序在开机自启动时自动更新新版本")

        self.checkBox1.installEventFilter(ToolTipFilter(self.checkBox1, 1000))
        self.checkBox2.installEventFilter(ToolTipFilter(self.checkBox2, 1000))
        self.checkBox3.installEventFilter(ToolTipFilter(self.checkBox3, 1000))

        self.checkBox1.setChecked(setting.read("autoStartup"))
        if setting.read("autoStartup"):
            self.checkBox2.setEnabled(True)
            self.checkBox3.setEnabled(True)
        else:
            self.checkBox2.setEnabled(False)
            self.checkBox3.setEnabled(False)
        self.checkBox2.setChecked(setting.read("autoHide"))
        self.checkBox3.setChecked(setting.read("autoUpdate"))

        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        if self.checkBox1.isChecked():
            setting.save("autoStartup", True)
            self.checkBox2.setEnabled(True)
            self.checkBox3.setEnabled(True)
            f.addToStartup(program.PROGRAM_NAME, program.PROGRAM_MAIN_FILE_PATH, True)
        else:
            setting.save("autoStartup", False)
            self.checkBox2.setEnabled(False)
            self.checkBox3.setEnabled(False)
            f.addToStartup(program.PROGRAM_NAME, program.PROGRAM_MAIN_FILE_PATH, False)

    def button2Clicked(self):
        setting.save("autoHide", self.checkBox2.isChecked())

    def button3Clicked(self):
        setting.save("autoUpdate", self.checkBox3.isChecked())


class ShortcutSettingCard(SettingCard):
    """
    快捷方式设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ADD_TO, "添加快捷方式", "向计算机中添加程序的快捷方式", parent)
        self.button1 = HyperlinkButton("", "桌面", self)
        self.button2 = HyperlinkButton("", "开始菜单", self)

        self.button1.clicked.connect(lambda: f.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.DESKTOP_PATH, "zb小程序.lnk"), program.source("program.ico")))
        self.button2.clicked.connect(lambda: f.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.USER_PATH, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs", "zb小程序.lnk"), program.source("program.ico")))

        self.button1.setToolTip("将程序添加到桌面快捷方式")
        self.button2.setToolTip("将程序添加到开始菜单列表")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class SortSettingCard(SettingCard):
    """
    整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "整理文件", "设置整理文件夹的目录", parent)
        self.button1 = PushButton("整理目录", self, FIF.FOLDER_ADD)
        self.button2 = PushButton("微信目录", self, FIF.FOLDER_ADD)

        self.button1.clicked.connect(self.button1Clicked)
        self.button2.clicked.connect(self.button2Clicked)

        self.button1.setToolTip("设置整理文件夹目录")
        self.button2.setToolTip("设置微信WeChat Files文件夹目录")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择整理目录", setting.read("sortPath"))
        if f.existPath(get):
            setting.save("sortPath", str(get))

    def button2Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择微信WeChat Files文件夹目录", setting.read("wechatPath"))
        if f.existPath(get):
            setting.save("wechatPath", str(get))


class SortBlacklistSettingCard(SettingCard):
    """
    下载文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.FOLDER, "整理文件黑名单", "设置整理文件时跳过的文件", parent)
        self.button1 = PushButton("编辑黑名单", self, FIF.EDIT)

        self.button1.clicked.connect(self.button1Clicked)

        self.button1.setToolTip("编辑整理文件黑名单")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        self.lineEditMessageBox = BlackListEditMessageBox("编辑黑名单", "输入文件名称\n一行一个", self.parent().parent().parent().parent().parent().parent().parent())
        self.lineEditMessageBox.show()


class DownloadSettingCard(SettingCard):
    """
    下载文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.DOWNLOAD, "下载文件", "设置下载文件的目录", parent)
        self.button1 = PushButton("下载目录", self, FIF.FOLDER_ADD)

        self.button1.clicked.connect(self.button1Clicked)

        self.button1.setToolTip("设置下载文件夹目录")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择下载目录", setting.read("downloadPath"))
        if f.existPath(get):
            setting.save("downloadPath", str(get))


class HelpSettingCard(SettingCard):
    """
    帮助设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.HELP, "帮助", "查看程序相关信息", parent)
        self.button1 = HyperlinkButton(program.PROGRAM_PATH, "程序安装路径", self, FIF.FOLDER)
        self.button2 = HyperlinkButton(program.PROGRAM_PATH, "程序数据路径", self, FIF.FOLDER)
        self.button3 = HyperlinkButton("", "清理程序缓存", self, FIF.BROOM)

        self.button1.clicked.connect(lambda: f.startFile(program.PROGRAM_PATH))
        self.button2.clicked.connect(lambda: f.startFile(program.PROGRAM_DATA_PATH))
        self.button3.clicked.connect(self.button3Clicked)

        self.button1.setToolTip("打开程序安装路径")
        self.button2.setToolTip("打开程序数据路径")
        self.button3.setToolTip("清理程序运行过程中生成的缓存文件")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button3Clicked(self):
        self.button3.setEnabled(False)

        self.thread = NewThread("清理程序缓存")
        self.thread.signalBool.connect(self.thread3)
        self.thread.start()

    def thread3(self, msg):
        self.button3.setEnabled(True)

        if msg:
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "清理程序缓存成功！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "清理程序缓存失败！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()


class UpdateSettingCard(SettingCard):
    """
    更新设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.UPDATE, "更新", "更新程序至新版本", parent)
        self.button1 = PushButton("更新运行库", self, FIF.LIBRARY)
        self.button2 = PrimaryPushButton("检查更新", self, FIF.DOWNLOAD)

        self.button1.clicked.connect(self.button1Clicked)
        self.button2.clicked.connect(self.button2Clicked)

        self.button1.setToolTip("更新程序运行库")
        self.button2.setToolTip("检查程序新版本更新")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("更新通道")
        self.comboBox.addItems(["正式版", "测试版"])
        self.comboBox.currentIndexChanged.connect(self.comboBoxIndexChanged)
        self.comboBox.setToolTip("选择更新通道")
        self.comboBox.installEventFilter(ToolTipFilter(self.comboBox, 1000))
        if setting.read("updateChannel") == "正式版":
            self.comboBox.setCurrentIndex(0)
        elif setting.read("updateChannel") == "测试版":
            self.comboBox.setCurrentIndex(1)
        else:
            self.comboBox.setCurrentIndex(0)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont())
        self.label.setText("")

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(250)

        self.vBoxLayout2 = QVBoxLayout()
        self.vBoxLayout2.setSpacing(0)
        self.vBoxLayout2.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout2.setAlignment(Qt.AlignVCenter)

        self.vBoxLayout2.addWidget(self.label)
        self.vBoxLayout2.addSpacing(2)
        self.vBoxLayout2.addWidget(self.progressBar)

        self.hBoxLayout.addLayout(self.vBoxLayout2)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.label.hide()
        self.progressBar.hide()

    def comboBoxIndexChanged(self):
        setting.save("updateChannel", self.comboBox.currentText())

    def button1Clicked(self):
        self.comboBox.setEnabled(False)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)

        self.label.show()
        self.progressBar.show()

        self.thread = NewThread("更新运行库")
        self.thread.signalDict.connect(self.thread1)
        self.thread.start()

    def thread1(self, msg):
        if msg["完成"]:
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "运行库安装成功！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()

            self.label.hide()
            self.progressBar.hide()

            self.label.setText("")
            self.progressBar.setValue(0)

            self.comboBox.setEnabled(True)
            self.button1.setEnabled(True)
            self.button2.setEnabled(True)
        else:
            value = int(msg["序号"] / len(program.REQUIRE_LIB) * 100)
            self.label.setText(f"{str(value)}% 正在更新 {msg["名称"]}")
            self.progressBar.setValue(value)

    def button2Clicked(self):
        if "beta" in program.PROGRAM_VERSION:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前版本为内测版无法更新！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            return
        self.comboBox.setEnabled(False)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)

        self.thread = NewThread("检查更新")
        self.thread.signalDict.connect(self.thread2)
        self.thread.start()

    def thread2(self, msg):
        if msg["更新"]:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", f"检测到新版本{msg["版本"]}！", Qt.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())

            self.button3 = PushButton("立刻更新", self, FIF.DOWNLOAD)
            self.button3.clicked.connect(self.button3Clicked)

            self.infoBar.addWidget(self.button3)
            self.infoBar.show()
        else:
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"{program.PROGRAM_VERSION}已为最新版本！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
        self.comboBox.setEnabled(True)
        self.button1.setEnabled(True)
        self.button2.setEnabled(True)

    def button3Clicked(self):
        self.comboBox.setEnabled(False)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)
        try:
            self.button3.setEnabled(False)
        except:
            pass
        self.label.setText("正在连接服务器")

        self.label.show()
        self.progressBar.show()

        self.thread = NewThread("立刻更新")
        self.thread.signalDict.connect(self.thread3)
        self.thread.start()

    def thread3(self, msg):
        if msg["更新"]:
            if msg["完成"]:
                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "更新成功！", Qt.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())

                self.button4 = PushButton("重新启动", self, FIF.SYNC)
                self.button4.clicked.connect(self.button4Clicked)

                self.infoBar.addWidget(self.button4)
                self.infoBar.show()

                self.label.hide()
                self.progressBar.hide()

                self.label.setText("")
                self.progressBar.setValue(0)

                self.comboBox.setEnabled(True)
                self.button1.setEnabled(True)
                self.button2.setEnabled(True)
            else:
                value = int(msg["序号"] / msg["数量"] * 100)
                self.label.setText(f"{str(value)}% 正在更新 {msg["名称"]}")
                self.progressBar.setValue(value)

        else:
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"{program.PROGRAM_VERSION}已为最新版本！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()

            self.label.hide()
            self.progressBar.hide()

            self.label.setText("")
            self.progressBar.setValue(0)

            self.comboBox.setEnabled(True)
            self.button1.setEnabled(True)
            self.button2.setEnabled(True)

    def button4Clicked(self):
        f.cmd(program.PROGRAM_MAIN_FILE_PATH)
        sys.exit()


class AboutSettingCard(SettingCard):
    """
    关于设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.INFO, "关于", f"© 2022-2023 Ianzb. GPLv3 License.\n当前版本 {program.PROGRAM_VERSION} {setting.read("updateChannel")}", parent)
        self.button1 = HyperlinkButton(program.PROGRAM_URL, "程序官网", self, FIF.LINK)
        self.button2 = HyperlinkButton(program.GITHUB_URL, "GitHub", self, FIF.GITHUB)

        self.button1.setToolTip("打开程序官网")
        self.button2.setToolTip("打开程序GitHub页面")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, window):
        super(Tray, self).__init__()
        self.window = window

        self.setIcon(QIcon(program.PROGRAM_ICON))
        self.setToolTip(program.PROGRAM_TITLE)
        self.installEventFilter(ToolTipFilter(self, 1000))
        self.activated.connect(self.iconClicked)
        self.show()

        self.showMessage(program.PROGRAM_NAME, f"{program.PROGRAM_NAME}启动成功！", QIcon(program.PROGRAM_ICON), 1)

        self.action1 = Action(FIF.HOME, "打开", triggered=self.action1Clicked)
        self.action2 = Action(FIF.ALIGNMENT, "整理", triggered=self.action2Clicked)
        self.action3 = Action(FIF.LINK, "官网", triggered=self.action3Clicked)
        self.action4 = Action(FIF.CLOSE, "退出", triggered=self.action4Clicked)

        self.menu = SystemTrayMenu()

        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

        self.window.mainPage.signalBool.connect(self.thread2)

    def iconClicked(self, reason):
        if reason == 3:
            self.trayClickedEvent()
        elif reason == 1:
            self.menu.show()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == Qt.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def action1Clicked(self):
        self.window.show()

    def action2Clicked(self):
        self.action2.setEnabled(False)
        self.window.mainPage.button1_1Clicked()

    def thread2(self, msg):
        self.action2.setEnabled(msg)

    def action3Clicked(self):
        webbrowser.open(program.PROGRAM_URL)

    def action4Clicked(self):
        self.deleteLater()
        qApp.quit()


logging.debug("windows.py初始化成功")
