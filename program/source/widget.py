from .custom import *



class AddonEditMessageBox(MessageBoxBase):
    """
    可编辑插件的弹出框
    """

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(title, self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(4)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["ID", "名称", "本地版本号", "在线版本号"])
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.tableView, 0, Qt.AlignTop)

        self.yesButton.setText("安装选中")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.removeButton = PrimaryPushButton("删除选中", self.buttonGroup)
        self.removeButton.clicked.connect(self.removeButtonClicked)
        self.buttonLayout.insertWidget(1, self.removeButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.yesButton.setEnabled(False)
        self.removeButton.setEnabled(False)

        self.widget.setMinimumWidth(600)

        self.installed = f.getInstalledAddonInfo()
        self.tableView.setRowCount(len(self.installed.values()))
        for i in range(len(self.installed.values())):
            names = sorted(self.installed.keys())

            self.tableView.setItem(i, 0, QTableWidgetItem(self.installed[names[i]]["id"]))
            self.tableView.setItem(i, 1, QTableWidgetItem(self.installed[names[i]]["name"]))
            self.tableView.setItem(i, 2, QTableWidgetItem(self.installed[names[i]]["version"]))
            self.tableView.setItem(i, 3, QTableWidgetItem("加载中..."))

        self.thread1 = CustomThread("云端插件信息")
        self.thread1.signalDict.connect(self.threadEvent1_1)
        self.thread1.signalBool.connect(self.threadEvent1_2)
        self.thread1.signalStr.connect(self.threadEvent1_3)
        self.thread1.start()

    def yesButtonClicked(self):
        self.parent().mainPage.addonSettingCard.button1.setEnabled(False)
        self.parent().mainPage.addonSettingCard.button2.setEnabled(False)
        self.parent().mainPage.addonSettingCard.progressBarLoading.show()

        list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[::4]]
        self.thread2 = CustomThread("下载插件", list)
        self.thread2.signalDict.connect(self.threadEvent2_1)
        self.thread2.signalBool.connect(self.threadEvent2_2)
        self.thread2.start()

    def removeButtonClicked(self):
        self.parent().mainPage.addonSettingCard.button1.setEnabled(False)
        self.parent().mainPage.addonSettingCard.button2.setEnabled(False)
        self.parent().mainPage.addonSettingCard.progressBarLoading.show()

        id_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[::4]]
        name_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[1::4]]
        installed_version_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[2::4]]
        for i in range(len(id_list)):
            if installed_version_list[i] != "未安装":
                self.parent().removeAddon({"id": id_list[i], "name": name_list[i]})

        self.accept()
        self.accepted.emit()
        self.parent().mainPage.addonSettingCard.button1.setEnabled(True)
        self.parent().mainPage.addonSettingCard.button2.setEnabled(True)
        self.parent().mainPage.addonSettingCard.progressBarLoading.hide()

    def threadEvent1_1(self, msg):
        if msg["id"] in self.installed.keys():
            i = self.tableView.findItems(msg["id"], Qt.MatchFlag.MatchExactly)[0].row()
            self.tableView.setItem(i, 3, QTableWidgetItem(msg["version"]))
        else:
            self.tableView.hide()
            self.tableView.setRowCount(self.tableView.rowCount() + 1)
            i = self.tableView.rowCount() - 1
            self.tableView.setItem(i, 0, QTableWidgetItem(msg["id"]))
            self.tableView.setItem(i, 1, QTableWidgetItem(msg["name"]))
            self.tableView.setItem(i, 2, QTableWidgetItem("未安装"))
            self.tableView.setItem(i, 3, QTableWidgetItem(msg["version"]))
            self.tableView.show()

    def threadEvent1_2(self, msg):
        if msg:
            for i in range(self.tableView.rowCount()):
                if self.tableView.item(i, 3).text() == "加载中...":
                    self.tableView.setItem(i, 3, QTableWidgetItem("云端无数据"))
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "无网络连接！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
            self.infoBar.show()
            for i in range(self.tableView.rowCount()):
                self.tableView.setItem(i, 3, QTableWidgetItem("无网络连接"))
            self.yesButton.setEnabled(False)
            self.removeButton.setEnabled(True)
            self.titleLabel.setText("管理插件（无网络连接）")
            return
        self.titleLabel.setText("管理插件")
        self.yesButton.setEnabled(True)
        self.removeButton.setEnabled(True)

    def threadEvent1_3(self, msg):
        i = self.tableView.findItems(msg["id"], Qt.MatchFlag.MatchExactly)[0].row()
        self.tableView.setItem(i, 2, QTableWidgetItem("连接失败"))

    def threadEvent2_1(self, msg):
        self.parent().addAddon(msg)

    def threadEvent2_2(self, msg):
        if not msg:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", f"无网络连接，插件下载失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
            self.infoBar.show()
        self.parent().mainPage.addonSettingCard.button1.setEnabled(True)
        self.parent().mainPage.addonSettingCard.button2.setEnabled(True)
        self.parent().mainPage.addonSettingCard.progressBarLoading.hide()

class AddonSettingCard(SettingCard):
    """
    插件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ADD, "插件", f"管理{program.NAME}的插件", parent)

        self.progressBarLoading = IndeterminateProgressBar(self)
        self.progressBarLoading.setMaximumWidth(200)
        self.progressBarLoading.hide()

        self.button1 = PushButton("手动导入", self, FIF.ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("手动导入程序插件")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("管理", self, FIF.EDIT)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("管理程序插件")
        self.button2.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.progressBarLoading, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setAcceptDrops(True)

    def button1Clicked(self):
        get = QFileDialog.getOpenFileUrl(self, "选择插件文件", QUrl(""), "zb小程序插件 (*.zbaddon);;压缩包 (*.zip)")[0]
        get = f.pathJoin(get.path()[1:])
        if get and get not in ["."]:
            self.importAddon(get)

    def button2Clicked(self):
        self.addonEditMessageBox = AddonEditMessageBox("加载中...", self.window())
        self.addonEditMessageBox.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if f.isFile(event.mimeData().urls()[0].toLocalFile()):
                    if f.splitPath(event.mimeData().urls()[0].toLocalFile(), 2) in [".zbaddon", ".zip"]:
                        event.acceptProposedAction()
                        self.contentLabel.setText("拖拽到此卡片即可快速导入插件！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"管理{program.NAME}的插件")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            self.importAddon(file)

    def importAddon(self, path: str):
        if not f.existPath(path):
            return
        id = f.importAddon(path)
        self.window().addAddon(id)


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
        self.radioButton1.setToolTip("设置浅色模式")
        self.radioButton1.installEventFilter(ToolTipFilter(self.radioButton1, 1000))

        self.radioButton2 = RadioButton("深色", self.view)
        self.radioButton2.setToolTip("设置深色模式")
        self.radioButton2.installEventFilter(ToolTipFilter(self.radioButton2, 1000))

        self.radioButton3 = RadioButton("跟随系统设置", self.view)
        self.radioButton3.setToolTip("设置跟随系统模式")
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
            setTheme(Theme.LIGHT, lazy=True)
        elif button is self.radioButton2:
            setting.save("theme", "Theme.DARK")
            setTheme(Theme.DARK, lazy=True)
        else:
            setting.save("theme", "Theme.AUTO")
            setTheme(Theme.AUTO, lazy=True)

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
        self.radioLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        self.button1 = RadioButton("默认", self.radioWidget)
        self.button1.setToolTip("设置默认颜色")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = RadioButton("自定义", self.radioWidget)
        self.button2.setToolTip("设置自定义颜色")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.button3 = QPushButton("选择颜色", self.customColorWidget)
        self.button3.setToolTip("选择自定义颜色")
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.radioLayout.addWidget(self.button1)
        self.radioLayout.addWidget(self.button2)

        self.buttonGroup = QButtonGroup(self)

        self.buttonGroup.addButton(self.button1)
        self.buttonGroup.addButton(self.button2)

        self.customColorLayout.setContentsMargins(48, 18, 44, 18)
        self.customColorLayout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)

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
        setThemeColor(self.color.name(), lazy=True)
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
            setThemeColor("#0078D4", lazy=True)
        else:
            self.button3.setDisabled(False)
            setting.save("themeColor", self.color.name())
            setThemeColor(self.color.name(), lazy=True)

    def showColorDialog(self):
        colorDialog = ColorDialog(setting.read("themeColor"), "选择颜色", self.window())
        colorDialog.colorChanged.connect(self.__colorChanged)
        colorDialog.exec()

    def __colorChanged(self, color):
        setThemeColor(color, lazy=True)
        self.color = QColor(color)
        setting.save("themeColor", self.color.name())
        self.colorChanged.emit(color)


class MicaEffectSettingCard(SettingCard):
    """
    云母效果设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.TRANSPARENT, "云母效果", "", parent)
        self.button1 = SwitchButton(self, IndicatorPosition.RIGHT)
        self.button1.setChecked(setting.read("micaEffect"))
        self.button1.checkedChanged.connect(self.button1Clicked)
        self.button1.setToolTip("开启 Windows 11 的窗口模糊效果")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        setting.save("micaEffect", self.button1.checked)
        self.window().setMicaEffectEnabled(self.button1.checked)


class StartupSettingCard(SettingCard):
    """
    开机自启动设置卡片
    """

    def __init__(self, parent=None):

        super().__init__(FIF.POWER_BUTTON, "开机自启动", "设置程序的开机自启动功能", parent)
        self.checkBox1 = CheckBox("开机自启动", self)
        self.checkBox1.setChecked(setting.read("autoStartup"))
        self.checkBox1.clicked.connect(self.button1Clicked)
        self.checkBox1.setToolTip("设置程序开机自启动")
        self.checkBox1.installEventFilter(ToolTipFilter(self.checkBox1, 1000))

        self.checkBox2 = CheckBox("最小化启动", self)
        self.checkBox2.setChecked(setting.read("autoHide"))
        self.checkBox2.clicked.connect(self.button2Clicked)
        self.checkBox2.setToolTip("设置程序在开机自启动时自动最小化窗口")
        self.checkBox2.installEventFilter(ToolTipFilter(self.checkBox2, 1000))

        if setting.read("autoStartup"):
            self.checkBox2.setEnabled(True)
        else:
            self.checkBox2.setEnabled(False)

        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        if self.checkBox1.isChecked():
            setting.save("autoStartup", True)
            self.checkBox2.setEnabled(True)
            f.addToStartup(program.NAME, program.MAIN_FILE_PATH, True)
        else:
            setting.save("autoStartup", False)
            self.checkBox2.setEnabled(False)
            f.addToStartup(program.NAME, program.MAIN_FILE_PATH, False)

    def button2Clicked(self):
        setting.save("autoHide", self.checkBox2.isChecked())


class TraySettingCard(SettingCard):
    """
    托盘设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ZOOM, "展示托盘图标", "", parent)
        self.button1 = SwitchButton(self, IndicatorPosition.RIGHT)
        self.button1.setChecked(setting.read("showTray"))
        self.button1.checkedChanged.connect(self.button1Clicked)
        self.button1.setToolTip("在系统托盘展示软件图标")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        setting.save("showTray", self.button1.checked)
        self.window().tray.setVisible(self.button1.checked)


class HideSettingCard(SettingCard):
    """
    隐藏后台设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.EMBED, "自动驻留后台", "", parent)
        self.button1 = SwitchButton(self, IndicatorPosition.RIGHT)
        self.button1.setChecked(setting.read("hideWhenClose"))
        self.button1.checkedChanged.connect(self.button1Clicked)
        self.button1.setToolTip("关闭窗口时程序自动隐藏")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        setting.save("hideWhenClose", self.button1.checked)



class DownloadSettingCard(SettingCard):
    """
    下载文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.DOWNLOAD, "下载文件", f"当前路径：{setting.read("downloadPath")}", parent)
        self.button1 = PushButton("下载目录", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("设置下载文件夹目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setAcceptDrops(True)

    def saveSetting(self, path: str):
        if f.existPath(path):
            setting.save("downloadPath", path)
        self.contentLabel.setText(f"当前路径：{setting.read("downloadPath")}")

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择下载目录", setting.read("downloadPath"))
        self.saveSetting(get)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if f.isDir(event.mimeData().urls()[0].toLocalFile()):
                    event.acceptProposedAction()
                    self.contentLabel.setText("拖拽到此卡片即可快速导入目录！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"当前路径：{setting.read("downloadPath")}")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            self.saveSetting(file)


class UpdateSettingCard(SettingCard):
    """
    更新设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.UPDATE, "更新", "更新程序至新版本", parent)

        self.button1 = PrimaryPushButton("检查更新", self, FIF.DOWNLOAD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("检查程序新版本更新")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        self.button1.setEnabled(False)

        self.thread1 = CustomThread("检查更新")
        self.thread1.signalStr.connect(self.threadEvent1_1)
        self.thread1.signalBool.connect(self.threadEvent1_2)
        self.thread1.start()

    def threadEvent1_1(self, msg):
        self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", f"检测到新版本{msg}！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.window().aboutPage)

        self.button2 = PushButton("立刻更新", self, FIF.DOWNLOAD)
        self.button2.clicked.connect(self.button2Clicked)

        self.infoBar.addWidget(self.button2)
        self.infoBar.show()

        self.button1.setEnabled(True)

    def threadEvent1_2(self, msg):
        if msg:
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"{program.VERSION}已为最新版本！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().aboutPage)
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "网络连接失败，无法检查程序更新！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().aboutPage)
        self.infoBar.show()

        self.button1.setEnabled(True)

    def button2Clicked(self):
        self.infoBar.close()
        f.delete(program.cache("zbProgramUpdate.exe"))
        self.download = DownloadWidget(program.UPDATE_INSTALLER_URL, program.cache("zbProgramUpdate.exe"), self.window().aboutPage)
        self.download.signalBool.connect(self.updateProgram)

    def updateProgram(self, msg):
        if msg:
            os.popen(program.cache("zbProgramUpdate.exe"))


class HelpSettingCard(SettingCard):
    """
    帮助设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.HELP, "帮助", "查看程序相关信息", parent)
        self.button1 = HyperlinkButton(program.INSTALL_PATH, "程序安装路径", self, FIF.FOLDER)
        self.button1.clicked.connect(lambda: f.showFile(program.INSTALL_PATH))
        self.button1.setToolTip("打开程序安装路径")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = HyperlinkButton(program.INSTALL_PATH, "程序数据路径", self, FIF.FOLDER)
        self.button2.clicked.connect(lambda: f.showFile(program.DATA_PATH))
        self.button2.setToolTip("打开程序数据路径")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.button3 = HyperlinkButton("", "清理程序缓存", self, FIF.BROOM)
        self.button3.clicked.connect(self.button3Clicked)
        self.button3.setToolTip("清理程序运行过程中生成的缓存文件")
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button3Clicked(self):
        self.button3.setEnabled(False)

        self.thread3 = CustomThread("清理程序缓存")
        self.thread3.signalBool.connect(self.threadEvent3)
        self.thread3.start()

    def threadEvent3(self, msg):
        self.button3.setEnabled(True)

        if msg:
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "清理程序缓存成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().aboutPage)
            self.infoBar.show()
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "清理程序缓存失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().aboutPage)
            self.infoBar.show()


class ControlSettingCard(SettingCard):
    """
    控制设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALBUM, "控制", "", parent)
        self.button1 = PushButton("重置设置", self, FIF.SYNC)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("重启程序设置")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("关闭", self, FIF.CLOSE)
        self.button2.clicked.connect(program.close)
        self.button2.setToolTip("关闭程序")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.button3 = PushButton("重启", self, FIF.SYNC)
        self.button3.clicked.connect(program.restart)
        self.button3.setToolTip("重启程序")
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.button4 = PrimaryPushButton("卸载", self, FIF.DELETE)
        self.button4.clicked.connect(lambda: os.popen("unins000.exe"))
        self.button4.setToolTip("卸载程序")
        self.button4.installEventFilter(ToolTipFilter(self.button4, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button3, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button4, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        self.button4 = PushButton("确认", self, FIF.SEND)
        self.button4.clicked.connect(setting.reset)
        self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "是否确认重置设置？该操作不可撤销！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.window().aboutPage)
        self.infoBar.addWidget(self.button4)
        self.infoBar.show()


class AboutSettingCard(SettingCard):
    """
    关于设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.INFO, "关于", f"© 2022-2024 Ianzb. GPLv3 License.\n当前版本 {program.VERSION}", parent)
        self.button1 = HyperlinkButton(program.URL, "程序官网", self, FIF.LINK)
        self.button1.setToolTip("打开程序官网")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = HyperlinkButton(program.GITHUB_URL, "GitHub", self, FIF.GITHUB)
        self.button2.setToolTip("打开程序GitHub页面")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


logging.debug("widget.py初始化成功")
