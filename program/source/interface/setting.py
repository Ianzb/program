from ..widget import *
from .widget import *


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

        self.set()
        setting.signalConnect(self.setEvent)

        self._adjustViewSize()

    def set(self):
        self.buttonGroup.buttonClicked.disconnect(self.buttonGroupClicked)
        if setting.read("theme") == "Theme.LIGHT":
            self.radioButton1.setChecked(True)
            setTheme(Theme.LIGHT, lazy=True)
            self.label.setText("浅色")
        elif setting.read("theme") == "Theme.DARK":
            self.radioButton2.setChecked(True)
            setTheme(Theme.DARK, lazy=True)
            self.label.setText("深色")
        else:
            self.radioButton3.setChecked(True)
            setTheme(Theme.AUTO, lazy=True)
            self.label.setText("跟随系统设置")
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

    def setEvent(self, msg):
        if msg == "theme":
            self.set()

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
        self.button3.clicked.connect(self.showColorDialog)

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

        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

        self.set()
        setting.signalConnect(self.setEvent)

        self.label1.setText(self.buttonGroup.checkedButton().text())
        self.label1.adjustSize()

    def set(self):
        self.buttonGroup.buttonClicked.disconnect(self.buttonGroupClicked)
        if setting.read("themeColor") == "#0078D4":
            self.button1.setChecked(True)
            self.button3.setEnabled(False)
        else:
            self.button2.setChecked(True)
            self.button3.setEnabled(True)
        self.label1.setText(self.buttonGroup.checkedButton().text())
        self.label1.adjustSize()
        self.color = QColor(setting.read("themeColor"))
        setThemeColor(self.color, lazy=True)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)

    def setEvent(self, msg):
        if msg == "themeColor":
            self.set()

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
            setThemeColor(self.color, lazy=True)

    def showColorDialog(self):
        colorDialog = ColorDialog(setting.read("themeColor"), "选择颜色", self.window())
        colorDialog.colorChanged.connect(self.__colorChanged)
        colorDialog.exec()

    def __colorChanged(self, color):
        setThemeColor(color, lazy=True)
        self.color = QColor(color)
        setting.save("themeColor", self.color.path())
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

        self.set()
        setting.signalConnect(self.setEvent)

    def set(self):
        self.button1.checkedChanged.disconnect(self.button1Clicked)
        self.button1.setChecked(setting.read("micaEffect"))
        self.window().setMicaEffectEnabled(setting.read("micaEffect"))
        self.button1.checkedChanged.connect(self.button1Clicked)

    def setEvent(self, msg):
        if msg == "micaEffect":
            self.set()

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
        self.checkBox1.setChecked(checkStartup())
        self.checkBox1.clicked.connect(self.button1Clicked)
        self.checkBox1.setToolTip("设置程序开机自启动")
        self.checkBox1.installEventFilter(ToolTipFilter(self.checkBox1, 1000))

        self.checkBox2 = CheckBox("最小化启动", self)
        self.checkBox2.setChecked(setting.read("autoHide"))
        self.checkBox2.clicked.connect(self.button2Clicked)
        self.checkBox2.setToolTip("设置程序在开机自启动时自动最小化窗口")
        self.checkBox2.installEventFilter(ToolTipFilter(self.checkBox2, 1000))
        self.checkBox2.setEnabled(checkStartup())

        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.set()
        setting.signalConnect(self.setEvent)

    def set(self):
        self.checkBox2.clicked.disconnect(self.button2Clicked)
        self.checkBox2.setChecked(setting.read("autoHide"))
        self.checkBox2.clicked.connect(self.button2Clicked)

    def setEvent(self, msg):
        if msg == "autoHide":
            self.set()

    def button1Clicked(self):
        if self.checkBox1.isChecked():
            self.checkBox2.setEnabled(True)
            addToStartup(True)
        else:
            self.checkBox2.setEnabled(False)
            addToStartup(False)

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

        self.set()
        setting.signalConnect(self.setEvent)

    def set(self):
        self.button1.checkedChanged.disconnect(self.button1Clicked)
        self.button1.setChecked(setting.read("showTray"))
        self.window().tray.setVisible(setting.read("showTray"))
        self.button1.checkedChanged.connect(self.button1Clicked)

    def setEvent(self, msg):
        if msg == "showTray":
            self.set()

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

        self.set()
        setting.signalConnect(self.setEvent)

    def set(self):
        self.button1.checkedChanged.disconnect(self.button1Clicked)
        self.button1.setChecked(setting.read("hideWhenClose"))
        self.button1.checkedChanged.connect(self.button1Clicked)

    def setEvent(self, msg):
        if msg == "hideWhenClose":
            self.set()

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

    def setEvent(self, msg):
        if msg == "downloadPath":
            self.contentLabel.setText(f"当前路径：{setting.read("downloadPath")}")

    def saveSetting(self, path: str):
        if existPath(path):
            setting.save("downloadPath", path)
        self.contentLabel.setText(f"当前路径：{setting.read("downloadPath")}")

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择下载目录", setting.read("downloadPath"))
        self.saveSetting(get)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if isDir(event.mimeData().urls()[0].toLocalFile()):
                    event.acceptProposedAction()
                    self.contentLabel.setText("拖拽到此卡片即可快速导入目录！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"当前路径：{setting.read("downloadPath")}")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            self.saveSetting(file)


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setViewportMargins(0, 70, 0, 0)
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

        if not (WINDOWS_VERSION[0] >= 10 and WINDOWS_VERSION[2] >= 22000):
            self.micaEffectSettingCard.hide()
