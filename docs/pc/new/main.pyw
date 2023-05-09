
version = "0.2.0"
from PyQt5 import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import *

from zb import *

mode = None
weight = 450
height = 250


class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(" ", "-"))


class newthread(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        global mode
        if mode == 1:
            autoClean()
            self.signal.emit("完成")
        if mode == 2 or mode == 3:
            with open("names.zb", "r", encoding="utf-8") as file:
                names = file.readlines()
            for i in range(len(names)):
                names[i] = names[i].strip()
        if mode == 2:
            wait = 0
            for i in range(40):
                wait += 0.002
                self.signal.emit(random.choice(names))
                time.sleep(wait)
            self.signal.emit("完成")


class tab1(QFrame, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("功能")
        self.pushButton1 = PushButton("一键整理+清理", self)
        self.pushButton1.clicked.connect(self.btn12)
        self.pushButton1.setGeometry(QtCore.QRect(0, 0, 150, 35))
        self.toolButton1 = ToolButton(FIF.FOLDER, self)
        self.toolButton1.clicked.connect(lambda: os.startfile(settings[3]))
        self.toolButton1.setGeometry(QtCore.QRect(150, 0, 50, 35))

    def btn11(self, title="zb小程序", content="提示内容"):
        self.stateTooltip.setContent(content)
        self.stateTooltip.setState(True)
        self.stateTooltip = None
        w.show()
        self.pushButton1.setEnabled(True)

    def btn12(self):
        global mode
        mode = 1
        self.pushButton1.setEnabled(False)
        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(143, 264)
        self.stateTooltip.show()
        self.thread = newthread()
        self.thread.signal.connect(lambda: self.btn11("提示", "整理完毕"))
        self.thread.start()


class tab2(QFrame, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName("模块")
        self.pushButton1 = PushButton("点名", self)
        self.pushButton1.clicked.connect(self.btn12)
        self.pushButton1.setGeometry(QtCore.QRect(0, 0, 400, 35))
        self.pushButton2 = PushButton("函数工具", self)
        self.pushButton2.clicked.connect(self.b2)
        self.pushButton2.setGeometry(QtCore.QRect(0, 280, 400, 35))

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("等线", 60))
        self.label.setGeometry(QtCore.QRect(0, 60, 400, 100))

    def btn11(self, msg):
        if msg == "完成":
            self.pushButton1.setEnabled(True)
            return
        self.label.setText(str(msg))

    def btn12(self):
        global mode
        mode = 2
        self.pushButton1.setEnabled(False)
        self.thread = newthread()
        self.thread.signal.connect(self.btn11)
        self.thread.start()

    def b2(self):
        os.popen("function.pyw")
        exit()


class AvatarWidget(NavigationWidget):

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage("logo.png").scaled(
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
            font = QFont("Segoe UI")
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, "Ianzb")


class TitleBar(StandardTitleBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.maxBtn.setParent(None)
        self._isDoubleClickEnabled = False


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        setThemeColor("#0078D4")
        self.setTitleBar(TitleBar(self))
        self.titleBar.raise_()
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)
        self.tab1 = tab1()
        self.tab2 = tab2()
        self.settingtab = Widget("版本" + version + "\n设置即将到来", self)
        self.initLayout()
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
        self.navigationInterface.setCurrentItem("功能")

    def initWindow(self):
        self.resize(weight, height)

        self.setWindowIcon(QIcon("logo.png"))
        self.setWindowTitle("zb小程序 PyQt版 " + version)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.windowEffect.setMicaEffect(self.winId())
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - weight // 2, h // 2 - height // 2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
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
        message = MessageBox("zb小程序", "是否打开作者网站？", self)
        if message.exec():
            webbrowser.open("https://ianzb.github.io/")
        else:
            message = None

    def closeEvent(self, event):
        #os.popen("hide.pyw")
        event.accept()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.processEvents()
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    w = Window()
    stopLoading()
    w.show()
    app.exec_()
