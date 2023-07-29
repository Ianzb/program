from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets.menu import *
from qframelesswindow import *
from resource import *
from zb import *


class newThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    def run(self):
        mode = self.mode
        if mode == 1:
            MyThread(lambda: clearRubbish())
            MyThread(lambda: clearCache())
            clearDesk(readSetting("sort"))
            if readSetting("wechat") != "":
                clearWechat(readSetting("wechat"), readSetting("sort"))
            clearFile(readSetting("sort"))
            self.signal.emit("完成")
        if mode == 2:
            cmd("taskkill /f /im explorer.exe")
            self.signal.emit("完成")
            cmd("start C:/windows/explorer.exe")
        if mode == 3:
            self.signal.emit("开始")
            if getVersion() == version:
                self.signal.emit("无需更新")
                return
            res = requests.get(urlJoin(update_url, "index.html"))
            res.encoding = "UTF-8"
            soup = bs4.BeautifulSoup(res.text, "lxml")
            data = soup.find_all(name="div", class_="download", text=re.compile("."))
            for i in range(len(data)): data[i] = data[i].text.strip()
            self.signal.emit("总共" + str(len(data)))
            for i in range(len(data)):
                self.signal.emit(data[i])
                download(urlJoin(update_url, data[i]))
            self.signal.emit("完成")
        if mode == 4:
            for i in range(len(lib_list)):
                self.signal.emit(str(i))
                pipInstall(lib_list[i])
            self.signal.emit("完成")
        if mode == 5:
            str1 = getMc()
            self.signal.emit(str1)

        if mode == 8:
            while True:
                time.sleep(0.1)
                if readSetting("shownow") == "1":
                    saveSetting("shownow", "0")
                    self.signal.emit("展示")


class updateSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None, parent2=None):

        super().__init__(icon, title, content, parent)
        self.parent = parent2
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
        self.label.setText("")
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
                parent=self.parent
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
                parent=self.parent
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
            self.progressBar.setValue(0)
            self.progressBar.setHidden(True)
            self.label.setHidden(True)
            self.infoBar4 = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title="提示",
                content="当前已为最新版本",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self.parent
            )
            self.infoBar4.show()
            self.pushButton1.setEnabled(True)
            self.pushButton2.setEnabled(True)
            return
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
                parent=self.parent

            )

            self.pushButton3 = PushButton("重新运行", self, FIF.SYNC)
            self.pushButton3.clicked.connect(self.btn3_1)
            self.infoBar3.addWidget(self.pushButton3)
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

    def btn3_1(self):
        os.popen("main.pyw")
        sys.exit()


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
        self.linkButton2 = HyperlinkButton("", text[1], self)
        self.linkButton3 = HyperlinkButton("", text[2], self)
        self.linkButton1.clicked.connect(lambda: webbrowser.open(url[0]))
        self.linkButton2.clicked.connect(lambda: cmd(url[1], False))
        self.linkButton3.clicked.connect(lambda: os.startfile(url[2]))
        self.hBoxLayout.addWidget(self.linkButton1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class checkBoxSettingCard(SettingCard):
    clicked = pyqtSignal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):

        super().__init__(icon, title[0], content, parent)
        self.checkBox1 = CheckBox(title[0], self)
        self.checkBox1.clicked.connect(self.btn1)
        self.checkBox2 = CheckBox(title[1], self)
        self.checkBox2.clicked.connect(self.btn2)
        if readSetting("start") == "1":
            self.checkBox1.setChecked(True)
            self.checkBox2.setEnabled(True)
        else:
            self.checkBox1.setChecked(False)
            self.checkBox2.setEnabled(False)
        if readSetting("autoupdate") == "1":
            self.checkBox2.setChecked(True)
        else:
            self.checkBox2.setChecked(False)
        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.checkBox2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def btn1(self):
        if self.checkBox1.isChecked():
            saveSetting("start", "1")
            self.checkBox2.setEnabled(True)
            autoRun(switch="open", zdynames=os.path.basename(join(abs_path, "main.pyw")), current_file="zb小程序")
        else:
            saveSetting("start", "0")
            self.checkBox2.setEnabled(False)
            autoRun(switch="close", zdynames=os.path.basename(join(abs_path, "main.pyw")), current_file="zb小程序")

    def btn2(self):
        if self.checkBox2.isChecked():
            saveSetting("autoupdate", "1")
        else:
            saveSetting("autoupdate", "0")


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


class SignalBus(QObject):
    switchToSampleCard = pyqtSignal(str, int)
    supportSignal = pyqtSignal()


signalBus = SignalBus()


class StyleSheet(StyleSheetBase, Enum):
    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    HOME_INTERFACE = "home_interface"
    ICON_INTERFACE = "icon_interface"
    VIEW_INTERFACE = "view_interface"
    SETTING_INTERFACE = "setting_interface"
    GALLERY_INTERFACE = "gallery_interface"
    NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f":/gallery/qss/{theme.value.lower()}/{self.value}.qss"


from queue import Queue


class Trie:

    def __init__(self):
        self.key = ''
        self.value = None
        self.children = [None] * 26
        self.isEnd = False

    def insert(self, key: str, value):
        key = key.lower()

        node = self
        for c in key:
            i = ord(c) - 97
            if not 0 <= i < 26:
                return

            if not node.children[i]:
                node.children[i] = Trie()

            node = node.children[i]

        node.isEnd = True
        node.key = key
        node.value = value

    def get(self, key, default=None):
        node = self.searchPrefix(key)
        if not (node and node.isEnd):
            return default

        return node.value

    def searchPrefix(self, prefix):
        prefix = prefix.lower()
        node = self
        for c in prefix:
            i = ord(c) - 97
            if not (0 <= i < 26 and node.children[i]):
                return None

            node = node.children[i]

        return node

    def items(self, prefix):
        node = self.searchPrefix(prefix)
        if not node:
            return []

        q = Queue()
        result = []
        q.put(node)

        while not q.empty():
            node = q.get()
            if node.isEnd:
                result.append((node.key, node.value))

            for c in node.children:
                if c:
                    q.put(c)

        return result
