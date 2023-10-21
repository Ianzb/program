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
        self.titleLabel = TitleLabel(title, self)
        self.subtitleLabel = CaptionLabel(subtitle, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.setFixedHeight(90)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 22, 36, 12)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)


class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, UI):
        super(Tray, self).__init__()
        import webbrowser
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
