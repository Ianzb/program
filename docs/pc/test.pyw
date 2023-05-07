version = "0.0.1"
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import *

from zb import *
check()
disable("test.txt")

class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class tab1(QFrame,QWidget):
    def __init__(self,text:str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
        settings = read_setting()
        self.pushButton1 = PushButton("一键整理+清理", self)
        self.pushButton1.clicked.connect(self.autoSortAndClean)
        self.toolButton = ToolButton(FIF.FOLDER, self)
        self.toolButton.clicked.connect(lambda: os.startfile(settings[3]))
        self.pushButton1.setGeometry(QtCore.QRect(0, 0, 150, 35))
        self.toolButton.setGeometry(QtCore.QRect(150, 0, 50, 35))

    def autoSortAndClean(self):
        settings = read_setting()

        if settings[0] == "作者个人版" and "Ian" not in platform.node():
            showerror("错误", "zb小程序 作者个人版 暂未适配你的电脑，暂时无法使用")
            return
        if settings[0] == "Seewo" and "seewo" not in platform.node().lower():
            showerror("错误", "zb小程序 希沃定制版 暂未适配你的电脑，暂时无法使用")
            return
        clear_rubbish()
        clear_cache()
        clear_desk(settings[3])
        clear_wechat(settings[4], settings[3])
        if settings[0] == "作者个人版":
            clear_apps(settings[3])
        if settings[0] == "希沃定制版":
            clear_seewo()
        clear_useless_files(settings[3])
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="提示",
            content="整理完毕",
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self
        )
        w.show()
class tab2(QFrame,QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
        settings = read_setting()
        self.pushButton1 = PushButton("点名器", self)
        self.pushButton1.clicked.connect(self.b1)
        self.pushButton2 = PushButton("函数工具", self)
        self.pushButton2.clicked.connect(self.b2)
        self.pushButton1.setGeometry(QtCore.QRect(0, 0, 200, 35))
        self.pushButton2.setGeometry(QtCore.QRect(0, 35, 200, 35))

    def b1(self):
        os.popen("choose.pyw")
        exit()

    def b2(self):
        os.popen("function.pyw")
        exit()

class AvatarWidget(NavigationWidget):

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage("logo.ico").scaled(
            24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        # draw background
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        # draw avatar
        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)
        painter.translate(-8, -6)

        if not self.isCompacted:
            painter.setPen(Qt.white if isDarkTheme() else Qt.black)
            font = QFont('Segoe UI')
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, "Ianzb")


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)
        # create sub interface
        self.tab1 = tab1("功能")
        self.tab2 = tab2("模块")
        self.settingtab = Widget("版本"+version+"\n设置即将到来", self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.tab1, FIF.HOME, "功能", NavigationItemPosition.TOP)
        self.addSubInterface(self.tab2, FIF.BOOK_SHELF, "模块", NavigationItemPosition.TOP)
        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=AvatarWidget(),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM
        )
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)

        self.addSubInterface(self.settingtab, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def initWindow(self):
        self.resize(250, 200)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle("zb小程序")
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.windowEffect.setMicaEffect(self.winId())
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text
        )

    def setQss(self):
        color = "dark" if isDarkTheme() else "light"

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        message = Dialog("zb小程序", "是否打开作者网站？", self)
        if message.exec():
            webbrowser.open("https://ianzb.github.io/")
        else:
            message = None


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    w = Window()
    w.show()
    close()
    app.exec_()
