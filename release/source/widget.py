from .custom import *


class BlackListEditMessageBox(MessageBoxBase):
    """
    可编辑黑名单的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("整理文件黑名单", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件名称\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortBlacklist")))
        self.textEdit.setToolTip("输入文件名称\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

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


class SortFolderEditMessageBox(MessageBoxBase):
    """
    可编辑整理目录的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("自定义整理目录", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件夹完整路径\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortFolder")))
        self.textEdit.setToolTip("输入文件夹完整路径\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.addButton = PushButton("选择目录", self.buttonGroup)
        self.addButton.clicked.connect(self.addButtonClicked)
        self.buttonLayout.insertWidget(1, self.addButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortFolder", sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))))

        self.accept()
        self.accepted.emit()

    def addButtonClicked(self):
        get = QFileDialog.getExistingDirectory(self, "添加整理目录", "C:/")
        if f.existPath(get):
            if get not in sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))):
                self.textEdit.setText((self.textEdit.toPlainText().strip() + "\n" + get).strip())


class SortFormatEditMessageBox(MessageBoxBase):
    """
    可编辑整理文件类型的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("自定义整理文件类型", self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(2)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["类型", "后缀名"])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.tableView.setToolTip("后缀名逗号（中英文均可）分割，加不加.均可")
        self.tableView.installEventFilter(ToolTipFilter(self.tableView, 1000))

        self.tableView.setRowCount(len(setting.read("sortFormat").keys()))
        for i in range(len(setting.read("sortFormat").keys())):
            self.tableView.setItem(i, 0, QTableWidgetItem(list(setting.read("sortFormat").keys())[i]))
            self.tableView.setItem(i, 1, QTableWidgetItem(",".join(sorted(list(setting.read("sortFormat").values())[i])).replace(".", "")))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.tableView)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.addButton = PushButton("添加行", self.buttonGroup)
        self.addButton.clicked.connect(self.addButtonClicked)

        self.removeButton = PushButton("删除选中行", self.buttonGroup)
        self.removeButton.clicked.connect(self.removeButtonClicked)

        self.resetButton = PushButton("重置", self.buttonGroup)
        self.resetButton.clicked.connect(self.resetButtonClicked)

        self.buttonLayout.insertWidget(1, self.addButton, 1, Qt.AlignVCenter)
        self.buttonLayout.insertWidget(2, self.removeButton, 1, Qt.AlignVCenter)
        self.buttonLayout.insertWidget(3, self.resetButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumSize(600, 400)

    def yesButtonClicked(self):
        data = {}
        for i in range(self.tableView.rowCount()):
            try:
                k = self.tableView.item(i, 0).text()
                v = self.tableView.item(i, 1).text()
            except:
                continue
            v = v.lower().replace("，", ",").replace(" ", "").strip().split(",")
            for i in range(len(v)):
                if v[i][0] != ".":
                    v[i] = "." + v[i]
            v = sorted(list(set(v)))
            if k.strip():
                if k not in data.keys():
                    data[k] = v
                else:
                    data[k] += v
                    data[k] = sorted(list(set(data[k])))
        setting.save("sortFormat", data)
        self.accept()
        self.accepted.emit()

    def addButtonClicked(self):
        self.tableView.hide()
        self.tableView.setRowCount(self.tableView.rowCount() + 1)
        self.tableView.show()

    def removeButtonClicked(self):
        selected = self.tableView.selectedIndexes()[::2]
        for i in range(len(selected)):
            selected[i] = selected[i].row()
        selected.sort(reverse=True)
        for i in selected:
            self.tableView.removeRow(i)

    def resetButtonClicked(self):
        setting.reset("sortFormat")
        self.accept()
        self.accepted.emit()


class AddonEditMessageBox(MessageBoxBase):
    """
    可编辑插件的弹出框
    """

    def __init__(self, title: str, parent=None, error: list = []):
        super().__init__(parent)
        self.errorAddonList = error
        self.titleLabel = SubtitleLabel(title, self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(4)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["ID", "名称", "本地版本号", "在线版本号"])
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.tableView, 0, Qt.AlignTop)

        self.yesButton.setText("安装选中")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.removeButton = PrimaryPushButton("删除选中", self.buttonGroup)
        self.removeButton.clicked.connect(self.removeButtonClicked)
        self.buttonLayout.insertWidget(1, self.removeButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(500)

        self.installed = f.getInstalledAddonInfo()
        self.tableView.setRowCount(len(self.installed.values()))
        for i in range(len(self.installed.values())):
            names = sorted(self.installed.keys())

            self.tableView.setItem(i, 0, QTableWidgetItem(self.installed[names[i]]["id"]))
            self.tableView.setItem(i, 1, QTableWidgetItem(self.installed[names[i]]["name"]))
            self.tableView.setItem(i, 2, QTableWidgetItem(self.installed[names[i]]["version"]))
            self.tableView.setItem(i, 3, QTableWidgetItem("加载中..."))

        self.thread1 = NewThread("云端插件信息")
        self.thread1.signalDict.connect(self.threadEvent1_1)
        self.thread1.signalBool.connect(self.threadEvent1_2)
        self.thread1.signalStr.connect(self.threadEvent1_3)
        self.thread1.start()

    def yesButtonClicked(self):
        self.parent().aboutPage.addonSettingCard.button1.setEnabled(False)
        self.parent().aboutPage.addonSettingCard.progressBarLoading.show()

        list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[::4]]
        self.thread2 = NewThread("下载插件", list)
        self.thread2.signalDict.connect(self.threadEvent2_1)
        self.thread2.signalBool.connect(self.threadEvent2_2)
        self.thread2.start()

    def removeButtonClicked(self):
        self.parent().aboutPage.addonSettingCard.button1.setEnabled(False)
        self.parent().aboutPage.addonSettingCard.progressBarLoading.show()

        id_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[::4]]
        name_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[1::4]]
        installed_version_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[2::4]]
        for i in range(len(id_list)):
            if installed_version_list[i] != "未安装":
                self.parent().removeAddon({"id": id_list[i], "name": name_list[i]})

        self.accept()
        self.accepted.emit()
        self.parent().aboutPage.addonSettingCard.button1.setEnabled(True)
        self.parent().aboutPage.addonSettingCard.progressBarLoading.hide()

    def threadEvent1_1(self, msg):
        if msg["id"] in self.installed.keys():
            i = self.tableView.findItems(msg["id"], Qt.MatchExactly)[0].row()
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
                if self.tableView.item(i, 0).text() in self.errorAddonList:
                    self.tableView.setItem(i, 2, QTableWidgetItem("安装失败"))
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", f"无网络连接！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().aboutPage)
            self.infoBar.show()
            for i in range(self.tableView.rowCount()):
                self.tableView.setItem(i, 3, QTableWidgetItem("无网络连接"))
            self.yesButton.setEnabled(False)
            self.removeButton.setEnabled(False)
        self.titleLabel.setText("管理插件")

    def threadEvent1_3(self, msg):
        i = self.tableView.findItems(msg["id"], Qt.MatchExactly)[0].row()
        self.tableView.setItem(i, 2, QTableWidgetItem("连接失败"))

    def threadEvent2_1(self, msg):
        self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{msg["name"]}安装成功！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().aboutPage)
        self.infoBar.show()
        self.parent().addAddon(msg)
        if msg["id"] in self.parent().aboutPage.addonSettingCard.errorAddonList:
            self.parent().aboutPage.addonSettingCard.errorAddonList.remove(msg["id"])

    def threadEvent2_2(self, msg):
        if msg:
            self.parent().aboutPage.addonSettingCard.button1.setEnabled(True)
            self.parent().aboutPage.addonSettingCard.progressBarLoading.hide()


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


class MicaEffectSettingCard(SettingCard):
    """
    云母效果设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.TRANSPARENT, "云母效果", "", parent)
        self.button1 = SwitchButton(self, IndicatorPosition.RIGHT)
        self.button1.setChecked(setting.read("micaEffect"))
        self.button1.checkedChanged.connect(self.button1Clicked)
        self.button1.setToolTip("开启Windows11的窗口模糊效果")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        setting.save("micaEffect", self.button1.checked)
        self.parent().parent().parent().parent().parent().parent().parent().setMicaEffectEnabled(self.button1.checked)


class StartupSettingCard(SettingCard):
    """
    开机自启动设置卡片
    """
    clicked = pyqtSignal()

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

        self.checkBox3 = CheckBox("开机自动更新", self)
        self.checkBox3.setChecked(setting.read("autoUpdate"))
        self.checkBox3.clicked.connect(self.button3Clicked)
        self.checkBox3.setToolTip("设置程序在开机自启动时自动更新新版本")
        self.checkBox3.installEventFilter(ToolTipFilter(self.checkBox3, 1000))

        if setting.read("autoStartup"):
            self.checkBox2.setEnabled(True)
            self.checkBox3.setEnabled(True)
        else:
            self.checkBox2.setEnabled(False)
            self.checkBox3.setEnabled(False)

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
        self.parent().parent().parent().parent().parent().parent().parent().tray.setVisible(self.button1.checked)


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


class SortPathSettingCard(SettingCard):
    """
    整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "整理文件", "设置整理文件夹的目录", parent)
        self.button1 = PushButton("整理目录", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("设置整理文件夹目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("微信目录", self, FIF.FOLDER_ADD)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("设置微信WeChat Files文件夹目录")
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


class SortSettingCard(SettingCard):
    """
    自定义整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.EDIT, "自定义整理文件", "", parent)
        self.button1 = PushButton("整理文件黑名单", self)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("编辑整理文件黑名单（填写文件名）")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("自定义整理目录", self)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("自定义整理文件夹（填写文件夹完整路径）")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.button3 = PushButton("自定义整理文件类型", self)
        self.button3.clicked.connect(self.button3Clicked)
        self.button3.setToolTip("自定义整理文件类型")
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        self.blackListMessageBox = BlackListEditMessageBox(self.parent().parent().parent().parent().parent().parent().parent())
        self.blackListMessageBox.show()

    def button2Clicked(self):
        self.blackListMessageBox = SortFolderEditMessageBox(self.parent().parent().parent().parent().parent().parent().parent())
        self.blackListMessageBox.show()

    def button3Clicked(self):
        self.sortFormatMessageBox = SortFormatEditMessageBox(self.parent().parent().parent().parent().parent().parent().parent())
        self.sortFormatMessageBox.show()


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


class AddonSettingCard(SettingCard):
    """
    插件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ADD, "插件", f"管理{program.PROGRAM_NAME}的插件", parent)
        self.errorAddonList = []

        self.progressBarLoading = IndeterminateProgressBar(self)
        self.progressBarLoading.setMaximumWidth(200)
        self.progressBarLoading.hide()

        self.button1 = PushButton("管理插件", self, FIF.EDIT)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("管理程序插件")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.progressBarLoading, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.parent().parent().signalStr.connect(self.errorAddonEvent)

    def button1Clicked(self):
        self.addonEditMessageBox = AddonEditMessageBox("加载中...", self.parent().parent().parent().parent().parent().parent().parent(), self.errorAddonList)
        self.addonEditMessageBox.show()

    def errorAddonEvent(self, msg):
        self.errorAddonList.append(msg)


class UpdateSettingCard(SettingCard):
    """
    更新设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.UPDATE, "更新", "更新程序至新版本", parent)
        self.button1 = PushButton("更新运行库", self, FIF.LIBRARY)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("更新程序运行库")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PrimaryPushButton("检查更新", self, FIF.DOWNLOAD)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("检查程序新版本更新")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("更新通道")
        self.comboBox.addItems(["正式版", "抢先版", "测试版"])
        self.comboBox.currentIndexChanged.connect(self.comboBoxIndexChanged)
        self.comboBox.setToolTip("选择更新通道：\n 正式版：于123云盘发布，下载快，最稳定，更新慢\n 抢先版：于Github/release发布，下载慢，较稳定，更新慢，通常与正式版相同\n 测试版：于Github/beta发布，下载慢，不稳定，更新快，若非测试不推荐该版本")
        self.comboBox.installEventFilter(ToolTipFilter(self.comboBox, 1000))
        if setting.read("updateChannel") == "正式版":
            self.comboBox.setCurrentIndex(0)
        elif setting.read("updateChannel") == "抢先版":
            self.comboBox.setCurrentIndex(1)
        elif setting.read("updateChannel") == "测试版":
            self.comboBox.setCurrentIndex(2)
        else:
            self.comboBox.setCurrentIndex(0)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont())
        self.label.setText("")

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
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
        if not f.pipTest():
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "Python未添加环境变量，pip无法使用，无法安装运行库！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            return

        self.comboBox.setEnabled(False)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)

        self.label.show()
        self.progressBar.show()

        self.thread1 = NewThread("更新运行库")
        self.thread1.signalDict.connect(self.threadEvent1)
        self.thread1.start()

    def threadEvent1(self, msg):
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

        self.thread2 = NewThread("检查更新")
        self.thread2.signalDict.connect(self.threadEvent2)
        self.thread2.start()

    def threadEvent2(self, msg):
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

        self.thread3 = NewThread("立刻更新")
        self.thread3.signalDict.connect(self.threadEvent3)
        self.thread3.start()

    def threadEvent3(self, msg):
        if msg["更新"]:
            if msg["完成"]:
                self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "更新成功！", Qt.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())

                self.button4 = PushButton("重新启动", self, FIF.SYNC)
                self.button4.clicked.connect(self.parent().parent().parent().parent().parent().parent().parent().aboutPage.controlSettingCard.button2Clicked)

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


class HelpSettingCard(SettingCard):
    """
    帮助设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.HELP, "帮助", "查看程序相关信息", parent)
        self.button1 = HyperlinkButton(program.PROGRAM_PATH, "程序安装路径", self, FIF.FOLDER)
        self.button1.clicked.connect(lambda: f.startFile(program.PROGRAM_PATH))
        self.button1.setToolTip("打开程序安装路径")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = HyperlinkButton(program.PROGRAM_PATH, "程序数据路径", self, FIF.FOLDER)
        self.button2.clicked.connect(lambda: f.startFile(program.PROGRAM_DATA_PATH))
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

        self.thread3 = NewThread("清理程序缓存")
        self.thread3.signalBool.connect(self.threadEvent3)
        self.thread3.start()

    def threadEvent3(self, msg):
        self.button3.setEnabled(True)

        if msg:
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", "清理程序缓存成功！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
        else:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "清理程序缓存失败！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()


class ControlSettingCard(SettingCard):
    """
    控制设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALBUM, "控制", "", parent)
        self.button1 = PushButton("关闭", self, FIF.CLOSE)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("关闭程序")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("重新启动", self, FIF.SYNC)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("重新启动程序")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        pass
        sys.exit()

    def button2Clicked(self):
        f.cmd(program.PROGRAM_MAIN_FILE_PATH)
        sys.exit()


class ShortcutSettingCard(SettingCard):
    """
    快捷方式设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ADD_TO, "添加快捷方式", "", parent)
        self.button1 = HyperlinkButton("", "桌面", self)
        self.button1.clicked.connect(lambda: f.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.DESKTOP_PATH, "zb小程序.lnk"), program.source("program.ico")))
        self.button1.setToolTip("将程序添加到桌面快捷方式")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = HyperlinkButton("", "开始菜单", self)
        self.button2.clicked.connect(lambda: f.createShortcut(program.PROGRAM_MAIN_FILE_PATH, f.pathJoin(program.USER_PATH, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs", "zb小程序.lnk"), program.source("program.ico")))
        self.button2.setToolTip("将程序添加到开始菜单列表")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class AboutSettingCard(SettingCard):
    """
    关于设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.INFO, "关于", f"© 2022-2024 Ianzb. GPLv3 License.\n当前版本 {program.PROGRAM_VERSION} {setting.read("updateChannel")}", parent)
        self.button1 = HyperlinkButton(program.PROGRAM_URL, "程序官网", self, FIF.LINK)
        self.button1.setToolTip("打开程序官网")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = HyperlinkButton(program.GITHUB_URL, "GitHub", self, FIF.GITHUB)
        self.button2.setToolTip("打开程序GitHub页面")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


logging.debug("widget.py初始化成功")
