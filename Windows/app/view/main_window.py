from PyQt5 import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets.menu import *
from qframelesswindow import *
from zb import *
from .gallery_interface import GalleryInterface
from .setting_interface import settingInterface
from .main_interface import *
from ..common.signal_bus import signalBus
from ..common import resource


class Tray(QSystemTrayIcon):
    def __init__(self, UI):
        super(Tray, self).__init__()
        self.window = UI
        self.menu = RoundMenu()
        self.menu.addAction(Action(FIF.HOME, "打开", triggered=lambda: self.window.show()))
        # self.menu.addSeparator()
        self.menu.addAction(Action(FIF.ALIGNMENT, "整理", triggered=lambda: self.window.mainInterface.btn1_1()))
        self.menu.addAction(Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program_url)))
        self.menu.addAction(Action(FIF.CLOSE, "退出", triggered=lambda: sys.exit()))
        self.setIcon(QIcon("img/logo.png"))
        self.setToolTip(title_name)
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
            if self.window.windowState() == QtCore.Qt.WindowMinimized:
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


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()
        self.tray = Tray(self)
        # create sub interface
        self.settingInterface = settingInterface(self)
        self.mainInterface = mainInterface(self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()
        self.thread = newThread(8)
        self.thread.signal.connect(self.ifShow)
        self.thread.start()

    def ifShow(self, msg):
        if msg == "展示":
            self.show()

    def initLayout(self):
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.mainInterface, FIF.HOME, "主页", pos)

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=NavigationAvatarWidget(zb_name, "img/zb.png"),
            onClick=self.onSupport,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon("img/logo.png"))
        self.setWindowTitle(title_name)

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        w = MessageBox(
            "欢迎使用zb小程序！",
            "作者：" + zb_name,
            self
        )
        w.yesButton.setText("前往作者网站")
        w.cancelButton.setText("取消")
        if w.exec():
            QDesktopServices.openUrl(QUrl(SUPPORT_URL))

    def switchToSample(self, routeKey, index):
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.hide()

    def closeEvent(self, QCloseEvent):
        QCloseEvent.ignore()
        self.hide()
