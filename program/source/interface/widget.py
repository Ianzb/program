from ..program import *
import webbrowser

class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, window):
        super(Tray, self).__init__(QIcon(program.ICON))
        self.window = window

        self.setIcon(QIcon(program.ICON))
        self.setToolTip(program.TITLE)
        self.activated.connect(self.iconClicked)

        self.action1 = Action(FIF.HOME, "打开", triggered=self.window.show)
        self.action2 = Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program.URL))
        self.action3 = Action(FIF.SYNC, "重启", triggered=program.restart)
        self.action4 = Action(FIF.CLOSE, "退出", triggered=program.close)

        self.menu = AcrylicMenu(parent=self.window)

        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

    def showTrayMessage(self, title, msg):
        super().showMessage(title, msg, QIcon(program.ICON))

    def iconClicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
            self.contextMenuEvent()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick or QSystemTrayIcon.ActivationReason.MiddleClick:
            self.trayClickedEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == Qt.WindowState.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), aniType=MenuAnimationType.PULL_UP)
        self.menu.show()
