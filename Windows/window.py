import logging

from widgets import *


class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, window):
        super(Tray, self).__init__()
        self.window = window

        self.setIcon(QIcon(program.source("logo.png")))
        self.setToolTip(program.PROGRAM_TITLE)
        self.installEventFilter(ToolTipFilter(self, 1000))
        self.activated.connect(self.iconClicked)
        self.show()

        self.showMessage(program.PROGRAM_NAME, f"{program.PROGRAM_NAME}启动成功！", QIcon(program.source("logo.png")), 1)

        self.action1 = Action(FIF.HOME, "打开", triggered=self.action1Clicked)
        self.action2 = Action(FIF.ALIGNMENT, "整理", triggered=self.action2Clicked)
        self.action3 = Action(FIF.LINK, "官网", triggered=self.action3Clicked)
        self.action4 = Action(FIF.CLOSE, "退出", triggered=self.action4Clicked)

        self.menu = RoundMenu()

        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

        self.window.mainPage.signalBool.connect(self.thread2)

    def iconClicked(self, reason):
        if reason == 3:
            self.trayClickedEvent()
        elif reason == 1:
            self.contextMenuEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == Qt.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), ani=True, aniType=MenuAnimationType.PULL_UP)

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
        setting.save("sortBlacklist", list(set([i.strip() for i in self.textEdit.toPlainText().split("\n") if i])))

        self.accept()
        self.accepted.emit()


class AppInfoCard(SmallInfoCard):
    """
    应用商店信息卡片
    """

    def __init__(self, data: dict, source: str, parent: QWidget = None):
        super().__init__(parent)
        self.data = data
        self.source = source

        self.mainButton.setText("下载")
        self.mainButton.setIcon(FIF.DOWNLOAD)
        self.mainButton.setToolTip("下载软件")
        self.mainButton.installEventFilter(ToolTipFilter(self.mainButton, 1000))

        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data["名称"])}", self.data["图标"])
        self.setTitle(f"{self.data["名称"]}")

        self.setInfo(self.data["介绍"], 0)
        self.setInfo(self.data["文件大小"], 1)
        self.setInfo(f"当前版本：{self.data["当前版本"]}", 2)
        self.setInfo(f"更新日期：{self.data["更新日期"]}", 3)

    def mainButtonClicked(self):
        self.mainButton.setEnabled(False)

        self.thread = NewThread("下载文件", (self.data["文件名称"], self.data["下载链接"]))
        self.thread.signalStr.connect(self.thread1)
        self.thread.signalInt.connect(self.thread2)
        self.thread.signalBool.connect(self.thread3)
        self.thread.start()

        self.stateTooltip = StateToolTip(f"正在下载软件：{self.data["名称"]}", "正在连接到服务器...", self.parent().parent().parent().parent())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.closeButton.clicked.connect(self.thread.cancel)
        self.stateTooltip.show()

    def thread1(self, msg):
        self.filePath = msg

    def thread2(self, msg):
        self.stateTooltip.setContent(f"下载中，当前进度{msg}%")
        if msg == 100:
            f.moveFile(self.filePath, self.filePath.replace(".zb.appstore.downloading", ""))
            self.stateTooltip.setContent("下载成功")
            self.stateTooltip.setState(True)

            self.mainButton.setEnabled(True)

    def thread3(self, msg):
        if msg:
            f.delete(self.filePath)
        self.mainButton.setEnabled(True)


class AppStoreTab(BasicTab):
    """
    应用商店页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout.setSpacing(8)

        self.lineEdit = SearchLineEdit(self)
        self.lineEdit.setPlaceholderText("应用名称")
        self.lineEdit.setToolTip("搜索应用，数据来源：\n 360软件中心\n 腾讯软件中心")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.lineEdit.searchButton.setEnabled(False)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)

        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("下载应用来源")
        self.comboBox.addItems(["360", "腾讯"])
        self.comboBox.setCurrentIndex(0)
        self.comboBox.setToolTip("选择下载应用来源")
        self.comboBox.installEventFilter(ToolTipFilter(self.comboBox, 1000))

        self.card = GrayCard("搜索")
        self.card.addWidget(self.lineEdit)
        self.card.addWidget(self.comboBox)

        self.progressRingLoading = IndeterminateProgressRing(self)
        self.progressRingLoading.hide()

        self.progressRingError = ProgressRing(self)
        self.progressRingError.setValue(100)
        self.progressRingError.setFormat("")
        self.progressRingError.hide()

        self.loadingCard = DisplayCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card)
        self.vBoxLayout.addWidget(self.loadingCard, 5, Qt.AlignCenter | Qt.AlignHCenter)

    def lineEditChanged(self, text):
        self.lineEdit.searchButton.setEnabled(bool(text))

    def searchButtonClicked(self):
        if self.lineEdit.text():
            for i in range(self.vBoxLayout.count())[2:]:
                self.vBoxLayout.itemAt(i).widget().hide()
                if not self.vBoxLayout.itemAt(i).widget().image.loading:
                    self.vBoxLayout.itemAt(i).widget().deleteLater()

            self.lineEdit.setEnabled(False)
            self.comboBox.setEnabled(False)

            self.loadingCard.setText("搜索中...")
            self.loadingCard.setDisplay(self.progressRingLoading)
            self.progressRingLoading.show()
            self.progressRingError.hide()
            self.loadingCard.show()

            self.thread = NewThread("搜索应用", [self.lineEdit.text(), self.comboBox.currentText()])
            self.thread.signalList.connect(self.thread1)
            self.thread.signalBool.connect(self.thread2)
            self.thread.start()

    def thread1(self, msg):
        self.loadingCard.hide()
        self.progressRingLoading.hide()
        self.progressRingError.hide()

        for i in msg:
            self.infoCard = AppInfoCard(i, self.comboBox.currentText())
            self.vBoxLayout.addWidget(self.infoCard)
        self.lineEdit.setEnabled(True)
        self.comboBox.setEnabled(True)

    def thread2(self, msg):
        if not msg:
            self.loadingCard.setText("网络连接失败！")
            self.loadingCard.setDisplay(self.progressRingError)
            self.progressRingLoading.hide()
            self.progressRingError.show()
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox.setEnabled(True)


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

        self.button1.clicked.connect(lambda: f.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.DESKTOP_PATH, "zb小程序.lnk"), program.source("logo.ico")))
        self.button2.clicked.connect(lambda: f.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.USER_PATH, "AppData\Roaming\Microsoft\Windows\Start Menu\Programs", "zb小程序.lnk"), program.source("logo.ico")))

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

        self.button1.clicked.connect(lambda: os.startfile(program.PROGRAM_PATH))
        self.button2.clicked.connect(lambda: os.startfile(program.PROGRAM_DATA_PATH))
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
        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.label.hide()
        self.progressBar.hide()

    def button1Clicked(self):
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
        self.button1.setEnabled(True)
        self.button2.setEnabled(True)

    def button3(self):
        if "beta" in program.PROGRAM_VERSION:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前版本为内测版无法更新！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            return
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)

        self.label.setText("正在连接服务器")

        self.label.show()
        self.progressBar.show()

        self.thread = NewThread("立刻更新")
        self.thread.signalDict.connect(self.thread3)
        self.thread.start()

    def thread3(self, msg):
        if msg["完成"]:
            if msg["完成"] == "失败":
                self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"{program.PROGRAM_VERSION}已为最新版本！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            else:
                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "更新成功！", Qt.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())

                self.button4 = PushButton("重新启动", self, FIF.SYNC)
                self.button4.clicked.connect(self.button4Clicked)

                self.infoBar.addWidget(self.button4)
            self.infoBar.show()

            self.label.hide()
            self.progressBar.hide()

            self.label.setText("")
            self.progressBar.setValue(0)

            self.button1.setEnabled(True)
            self.button2.setEnabled(True)
        else:
            value = int(msg["序号"] / msg["数量"] * 100)
            self.label.setText(f"{str(value)}% 正在更新 {msg["名称"]}")
            self.progressBar.setValue(value)

    def button4Clicked(self):
        f.cmd(program.PROGRAM_MAIN_FILE_PATH)
        sys.exit()


class AboutSettingCard(SettingCard):
    """
    关于设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.INFO, "关于", f"© 2022-2023 Ianzb. GPLv3 License.\n当前版本 {program.PROGRAM_VERSION}", parent)
        self.button1 = HyperlinkButton(program.PROGRAM_URL, "程序官网", self, FIF.LINK)
        self.button2 = HyperlinkButton(program.GITHUB_URL, "GitHub", self, FIF.GITHUB)

        self.button1.setToolTip("打开程序官网")
        self.button2.setToolTip("打开程序GitHub页面")

        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


logging.debug("windows.py初始化成功")
