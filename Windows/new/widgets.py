from functions import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import *


class NewThread(QThread):
    """
    多线程模块
    """
    signal = pyqtSignal(str)
    signal2 = pyqtSignal(list)

    def __init__(self, mode, data=None):
        super().__init__()
        self.mode = mode
        self.data = data

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
            for i in range(len(lib_update_list)):
                self.signal.emit(str(i))
                pipUpdate(lib_update_list[i])
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
        if mode == 10:
            l1 = ["全部"] + getGameVersions(mode="lite")
            l2 = ["全部"] + getGameVersions()
            self.signal2.emit([l1, l2])
        if mode == 11:
            info = search(self.data[0], self.data[1], 20, 1)
            info = searchModInf(info)
            if not info:
                self.signal2.emit(info)
                return
            info = getModData(info)
            self.signal2.emit(info)
        if mode == 12:
            try:
                if exists(join(user_path, "zb", "cache", self.data["名称"] + ".png")):
                    self.signal.emit("成功")
                response = requests.get(self.data["图标"], headers=header, timeout=600).content
                mkDir(join(user_path, "zb", "cache"))
                with open(join(user_path, "zb", "cache", self.data["名称"] + ".png"), "wb") as file:
                    file.write(response)
                self.signal.emit("成功")
            except:
                self.signal.emit("失败")


class ScrollArea(ScrollArea):
    """
    优化样式的滚动区域
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("QScrollArea {background-color: rgba(0,0,0,0); border: none; border-top-left-radius: 10px;}")


class ToolBar(QWidget):
    """
    页面顶端工具栏
    """

    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(90)

        self.titleLabel = TitleLabel(title, self)
        self.subtitleLabel = CaptionLabel(subtitle, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 22, 36, 12)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")


class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, UI):
        super(Tray, self).__init__()
        self.window = UI
        self.menu = RoundMenu()
        self.menu.addAction(Action(FIF.HOME, "打开", triggered=lambda: self.window.show()))
        self.menu.addAction(Action(FIF.ALIGNMENT, "整理", triggered=lambda: self.window.mainInterface.btn1_1()))
        self.menu.addAction(Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program.PROGRAM_URL)))
        self.menu.addAction(Action(FIF.CLOSE, "退出", triggered=lambda: self.triggered()))
        self.setIcon(QIcon(program.source("logo.png")))
        self.setToolTip(program.PROGRAM_TITLE)
        self.activated.connect(self.clickedIcon)
        self.show()

    def clickedIcon(self, reason):
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

    def triggered(self):
        self.deleteLater()
        qApp.quit()

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), ani=True, aniType=MenuAnimationType.PULL_UP)


class GrayCard(QWidget):
    """
    灰色背景组件卡片
    """

    def __init__(self, title: str, widget, parent=None):
        super().__init__(parent=parent)
        self.widget = widget
        if type(self.widget) != list:
            self.widget = [self.widget]

        self.titleLabel = StrongBodyLabel(title, self)
        self.card = QFrame(self)
        self.card.setObjectName("卡片")

        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = QVBoxLayout(self.card)
        self.topLayout = QHBoxLayout()

        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.cardLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.topLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setContentsMargins(12, 12, 12, 12)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignTop)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.cardLayout.setSpacing(0)
        self.cardLayout.setAlignment(Qt.AlignTop)
        self.cardLayout.addLayout(self.topLayout, 0)

        for i in self.widget:
            i.setParent(self.card)
            self.topLayout.addWidget(i)
            i.show()

        self.topLayout.addStretch(1)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
            self.card.setStyleSheet("QWidget {background-color: rgba(25,25,25,0.5); border:1px solid rgba(20,20,20,0.15); border-radius: 10px}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")
            self.card.setStyleSheet("QWidget {background-color: rgba(175,175,175,0.1); border:1px solid rgba(150,150,150,0.15); border-radius: 10px}")


class ThemeSettingCard(ExpandSettingCard):
    """
    主题设置卡片
    """
    themeChanged = pyqtSignal(OptionsConfigItem)

    def __init__(self, parent=None):
        super().__init__(FIF.BRUSH, "程序主题", "修改程序明暗主题", parent)
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        self.radioButton1 = RadioButton("浅色", self.view)
        self.buttonGroup.addButton(self.radioButton1)
        self.viewLayout.addWidget(self.radioButton1)
        self.radioButton2 = RadioButton("深色", self.view)
        self.buttonGroup.addButton(self.radioButton2)
        self.viewLayout.addWidget(self.radioButton2)
        self.radioButton3 = RadioButton("跟随系统设置", self.view)
        self.buttonGroup.addButton(self.radioButton3)
        self.viewLayout.addWidget(self.radioButton3)

        if setting.read("theme") == "Theme.LIGHT":
            self.radioButton1.setChecked(True)
            self.choiceLabel.setText("浅色")
        elif setting.read("theme") == "Theme.DARK":
            self.radioButton2.setChecked(True)
            self.choiceLabel.setText("深色")
        else:
            self.radioButton3.setChecked(True)
            self.choiceLabel.setText("跟随系统设置")
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

        self._adjustViewSize()

    def __onButtonClicked(self, button: RadioButton):
        if button.text() == self.choiceLabel.text():
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

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()


class ColorSettingCard(ExpandGroupSettingCard):
    """
    主题色设置卡片
    """
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(FIF.PALETTE, "主题色", "修改程序的主题色", parent=parent)
        self.choiceLabel = QLabel(self)
        self.radioWidget = QWidget(self.view)
        self.radioLayout = QVBoxLayout(self.radioWidget)
        self.radioButton1 = RadioButton("默认", self.radioWidget)
        self.radioButton2 = RadioButton("自定义", self.radioWidget)
        self.buttonGroup = QButtonGroup(self)

        self.customColorWidget = QWidget(self.view)
        self.customColorLayout = QHBoxLayout(self.customColorWidget)
        self.customLabel = QLabel("自定义颜色", self.customColorWidget)
        self.chooseColorButton = QPushButton("选择颜色", self.customColorWidget)

        self.addWidget(self.choiceLabel)

        self.radioLayout.setSpacing(19)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 18, 0, 18)
        self.buttonGroup.addButton(self.radioButton1)
        self.buttonGroup.addButton(self.radioButton2)
        self.radioLayout.addWidget(self.radioButton1)
        self.radioLayout.addWidget(self.radioButton2)
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

        if setting.read("themeColor") == "#0078D4":
            self.radioButton1.setChecked(True)
            self.chooseColorButton.setEnabled(False)
        else:
            self.radioButton2.setChecked(True)
            self.chooseColorButton.setEnabled(True)
        self.color = QColor(setting.read("themeColor"))
        setThemeColor(self.color.name())
        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())
        self.choiceLabel.adjustSize()

        self.chooseColorButton.setObjectName("chooseColorButton")

        self.buttonGroup.buttonClicked.connect(self.__onRadioButtonClicked)
        self.chooseColorButton.clicked.connect(self.__showColorDialog)

    def __onRadioButtonClicked(self, button: RadioButton):
        if button.text() == self.choiceLabel.text():
            return
        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        if button is self.radioButton1:
            self.chooseColorButton.setDisabled(True)
            setting.save("themeColor", "#0078D4")
            setThemeColor("#0078D4")
        else:
            self.chooseColorButton.setDisabled(False)
            setting.save("themeColor", self.color.name())
            setThemeColor(self.color.name())

    def __showColorDialog(self):
        w = ColorDialog(setting.read("themeColor"), "选择颜色", self.window())
        w.colorChanged.connect(self.__colorChanged)
        w.exec()

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
        self.checkBox1.clicked.connect(self.button1)
        self.checkBox2 = CheckBox("最小化启动", self)
        self.checkBox2.clicked.connect(self.button2)
        self.checkBox3 = CheckBox("开机自动更新", self)
        self.checkBox3.clicked.connect(self.button3)
        if setting.read("autoStartup") == "1":
            self.checkBox1.setChecked(True)
            self.checkBox2.setEnabled(True)
            self.checkBox3.setEnabled(True)
        else:
            self.checkBox1.setChecked(False)
            self.checkBox2.setEnabled(False)
            self.checkBox3.setEnabled(False)
        if setting.read("autoMinimize") == "1":
            self.checkBox2.setChecked(True)
        else:
            self.checkBox2.setChecked(False)
        if setting.read("autoUpdate") == "1":
            self.checkBox3.setChecked(True)
        else:
            self.checkBox3.setChecked(False)
        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.checkBox2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.checkBox3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1(self):
        if self.checkBox1.isChecked():
            setting.save("autoStartup", "1")
            self.checkBox2.setEnabled(True)
            self.checkBox3.setEnabled(True)
            f.addToStartup(program.PROGRAM_NAME, program.PROGRAM_MAIN_FILE_PATH, True)
        else:
            setting.save("autoStartup", "0")
            self.checkBox2.setEnabled(False)
            self.checkBox3.setEnabled(False)
            f.addToStartup(program.PROGRAM_NAME, program.PROGRAM_MAIN_FILE_PATH, False)

    def button2(self):
        if self.checkBox2.isChecked():
            setting.save("autoMinimize", "1")
        else:
            setting.save("autoMinimize", "0")

    def button3(self):
        if self.checkBox3.isChecked():
            setting.save("autoUpdate", "1")
        else:
            setting.save("autoUpdate", "0")


class HelpSettingCard(SettingCard):
    """
    帮助设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.HELP, "帮助", "查看程序相关信息", parent)
        self.linkButton1 = HyperlinkButton(program.PROGRAM_PATH, "程序安装路径", self, FIF.FOLDER)
        self.linkButton2 = HyperlinkButton(program.SETTING_FILE_PATH, "程序设置文件", self, FIF.SAVE_AS)
        self.linkButton1.clicked.connect(lambda: os.startfile(program.PROGRAM_PATH))
        self.linkButton2.clicked.connect(lambda: os.startfile(program.SETTING_FILE_PATH))
        self.hBoxLayout.addWidget(self.linkButton1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class AboutSettingCard(SettingCard):
    """
    关于设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.INFO, "关于", f"By Ianzb 2022-2023. MIT License.\n当前版本 {program.PROGRAM_VERSION}", parent)
        self.linkButton1 = HyperlinkButton(program.PROGRAM_URL, "程序官网", self, FIF.LINK)
        self.linkButton2 = HyperlinkButton(program.GITHUB_URL, "GitHub", self, FIF.GITHUB)
        self.hBoxLayout.addWidget(self.linkButton1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
