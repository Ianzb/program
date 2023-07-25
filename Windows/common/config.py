from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets.menu import *
from qframelesswindow import *
from zb import *


class updateSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):

        super().__init__(icon, title, content, parent)
        self.pushButton1 = PushButton("安装运行库", self, FIF.DOWNLOAD)
        self.pushButton1.clicked.connect(self.btn1)
        self.pushButton2 = PrimaryPushButton("检查更新", self, FIF.DOWNLOAD)
        self.pushButton2.clicked.connect(self.btn2)
        self.progressBar = ProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setHidden(True)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("等线", 10))
        self.label.setHidden(True)
        self.label.setText("123")
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.progressBar, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.pushButton1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.pushButton2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def btn1(self):
        self.label.setHidden(False)
        self.pushButton1.setEnabled(False)
        self.pushButton2.setEnabled(False)
        self.progressBar.setHidden(False)
        self.progressBar.setValue(0)
        self.thread = newThread(4)
        self.thread.signal.connect(self.btn1_2)
        self.thread.start()

    def btn1_2(self, msg):
        self.number = len(lib_list)
        if msg == "完成":
            self.progressBar.setValue(0)
            self.progressBar.setHidden(True)
            self.label.setHidden(True)
            self.infoBar1 = InfoBar(
                icon=InfoBarIcon.SUCCESS,
                title="提示",
                content="运行库安装成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            self.infoBar1.show()
            self.pushButton1.setEnabled(True)
            self.pushButton2.setEnabled(True)
            return
        if int(msg) == 0:
            self.count = 0
        self.count += 1
        self.label.setText("正在安装 " + lib_list[int(msg)] + " " + str(int(100 / self.number * self.count)) + "%")
        self.progressBar.setValue(int(100 / self.number * self.count))

    def btn2(self):
        if ":\编程\program" in abs_path:
            self.infoBar2 = InfoBar(
                icon=InfoBarIcon.WARNING,
                title="警告",
                content="开发者目录禁止更新！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP_LEFT,
                duration=2000,
                parent=self
            )
            self.infoBar2.show()
            return
        self.label.setHidden(False)
        self.label.setText("正在连接至服务器")
        self.pushButton1.setEnabled(False)
        self.pushButton2.setEnabled(False)
        self.progressBar.setHidden(False)
        self.progressBar.setValue(0)
        self.thread = newThread(3)
        self.thread.signal.connect(self.btn2_2)
        self.thread.start()

    def btn2_2(self, msg):
        if msg == "开始":
            self.label.setText("正在连接至服务器")
            self.count = 0
            self.number = 20
        if msg == "无需更新":
            self.infoBar4 = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title="提示",
                content="当前已为最新版本",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            self.infoBar4.show()
        if msg == "完成":
            self.progressBar.setValue(0)
            self.progressBar.setHidden(True)
            self.label.setHidden(True)
            self.infoBar3 = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title="提示",
                content="更新成功，重新运行后生效！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            self.infoBar3.show()
            self.pushButton1.setEnabled(True)
            self.pushButton2.setEnabled(True)
            return
        if "总共" in msg:
            self.number = int(msg[2:]) + 1
        self.count += 1
        if self.count != 1:
            self.label.setText("正在更新 " + msg + " " + str(int(100 / self.number * (self.count - 1))) + "%")
        self.progressBar.setValue(int(100 / self.number * (self.count - 1)))

    def flush(self):
        pass


class pushSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.button1 = QPushButton(text[0], self)
        self.button2 = QPushButton(text[1], self)
        self.button1.clicked.connect(lambda: createLink(name="zb小程序", path=join(abs_path, "main.pyw"), to=abs_desktop, icon=join(abs_path, "img/logo.ico")))
        self.button2.clicked.connect(addToStartMenu)
        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class linkCard(SettingCard):

    def __init__(self, url, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.linkButton1 = HyperlinkButton("", text[0], self)
        self.linkButton2 = HyperlinkButton(url[1], text[1], self)
        self.linkButton3 = HyperlinkButton(url[2], text[2], self)
        self.linkButton1.clicked.connect(lambda: webbrowser.open(url[0]))
        self.linkButton2.clicked.connect(lambda: cmd(url[1]))
        self.linkButton3.clicked.connect(lambda: os.startfile(url[2]))
        self.hBoxLayout.addWidget(self.linkButton1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class checkBoxSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):

        super().__init__(icon, title, content, parent)
        self.checkBox = CheckBox("开机自启动", self)
        self.checkBox.clicked.connect(self.btn1)
        if readSetting("start") == "1":
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
        self.hBoxLayout.addWidget(self.checkBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def btn1(self):
        if self.checkBox.isChecked():
            saveSetting("start", "1")
            autoRun(switch="open", zdynames=os.path.basename(join(abs_path, "main.pyw")), current_file="zb小程序")
        else:
            saveSetting("start", "0")
            autoRun(switch="close", zdynames=os.path.basename(join(abs_path, "main.pyw")), current_file="zb小程序")


class OptionsSettingCard(ExpandSettingCard):
    optionChanged = pyqtSignal(OptionsConfigItem)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, texts=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.texts = texts or []
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)
        self.btn1 = RadioButton(texts[0], self.view)
        self.buttonGroup.addButton(self.btn1)
        self.viewLayout.addWidget(self.btn1)
        self.btn2 = RadioButton(texts[1], self.view)
        self.buttonGroup.addButton(self.btn2)
        self.viewLayout.addWidget(self.btn2)
        self.btn3 = RadioButton(texts[2], self.view)
        self.buttonGroup.addButton(self.btn3)
        self.viewLayout.addWidget(self.btn3)
        if readSetting("custom") == "":
            saveSetting("custom", "auto")
        if readSetting("custom") == "light":
            self.btn1.setChecked(True)
            self.choiceLabel.setText("浅色")
        elif readSetting("custom") == "dark":
            self.btn2.setChecked(True)
            self.choiceLabel.setText("深色")
        else:
            self.btn3.setChecked(True)
            self.choiceLabel.setText("跟随系统设置")

        self._adjustViewSize()
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: RadioButton):
        if button.text() == self.choiceLabel.text():
            return
        if button is self.btn1:
            saveSetting("custom", "light")
            setTheme(Theme.LIGHT)
        elif button is self.btn2:
            saveSetting("custom", "dark")
            setTheme(Theme.DARK)
        else:
            saveSetting("custom", "auto")
            setTheme(Theme.AUTO)

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()


class CustomColorSettingCard(ExpandGroupSettingCard):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str,
                 content=None, parent=None, enableAlpha=False):
        super().__init__(icon, title, content, parent=parent)
        self.enableAlpha = enableAlpha
        self.choiceLabel = QLabel(self)
        self.radioWidget = QWidget(self.view)
        self.radioLayout = QVBoxLayout(self.radioWidget)
        self.defaultRadioButton = RadioButton("默认颜色", self.radioWidget)
        self.customRadioButton = RadioButton("自定义颜色", self.radioWidget)
        self.buttonGroup = QButtonGroup(self)

        self.customColorWidget = QWidget(self.view)
        self.customColorLayout = QHBoxLayout(self.customColorWidget)
        self.customLabel = QLabel("自定义颜色", self.customColorWidget)
        self.chooseColorButton = QPushButton("选择颜色", self.customColorWidget)

        self.__initWidget()

    def __initWidget(self):
        self.__initLayout()
        if readSetting("color") == "":
            saveSetting("color", "#0078D4")
        if readSetting("color") == "#0078D4":
            self.defaultRadioButton.setChecked(True)
            self.chooseColorButton.setEnabled(False)
        else:
            self.customRadioButton.setChecked(True)
            self.chooseColorButton.setEnabled(True)
        self.color = QColor(readSetting("color"))
        setThemeColor(self.color.name())
        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())
        self.choiceLabel.adjustSize()

        self.chooseColorButton.setObjectName("chooseColorButton")

        self.buttonGroup.buttonClicked.connect(self.__onRadioButtonClicked)
        self.chooseColorButton.clicked.connect(self.__showColorDialog)

    def __initLayout(self):
        self.addWidget(self.choiceLabel)

        self.radioLayout.setSpacing(19)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 18, 0, 18)
        self.buttonGroup.addButton(self.customRadioButton)
        self.buttonGroup.addButton(self.defaultRadioButton)
        self.radioLayout.addWidget(self.customRadioButton)
        self.radioLayout.addWidget(self.defaultRadioButton)
        self.radioLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.customColorLayout.setContentsMargins(48, 18, 44, 18)
        self.customColorLayout.addWidget(self.customLabel, 0, Qt.AlignLeft)
        self.customColorLayout.addWidget(self.chooseColorButton, 0, Qt.AlignRight)
        self.customColorLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.addGroupWidget(self.radioWidget)
        self.addGroupWidget(self.customColorWidget)

        self._adjustViewSize()

    def __onRadioButtonClicked(self, button: RadioButton):
        if button.text() == self.choiceLabel.text():
            return
        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        if button is self.defaultRadioButton:
            self.chooseColorButton.setDisabled(True)
            saveSetting("color", "#0078D4")
            setThemeColor("#0078D4")
        else:
            self.chooseColorButton.setDisabled(False)
            saveSetting("color", self.color.name())
            setThemeColor(self.color.name())

    def __showColorDialog(self):
        w = ColorDialog(readSetting("color"), "选择颜色", self.window(), self.enableAlpha)
        w.colorChanged.connect(self.__colorChanged)
        w.exec()

    def __colorChanged(self, color):
        setThemeColor(color)
        self.color = QColor(color)
        saveSetting("color", self.color.name())
        self.colorChanged.emit(color)
