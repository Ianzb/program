from functions import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import *


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


class HelpSettingCard(SettingCard):
    """
    帮助设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.HELP, "帮助", "查看程序相关信息", parent)
        self.linkButton1 = HyperlinkButton(program.PROGRAM_URL, "程序官网", self, FIF.LINK)
        self.linkButton2 = HyperlinkButton(program.PROGRAM_PATH, "程序安装路径", self, FIF.FOLDER)
        self.linkButton2.clicked.connect(lambda: os.startfile(program.PROGRAM_PATH))
        self.hBoxLayout.addWidget(self.linkButton1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.linkButton2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
