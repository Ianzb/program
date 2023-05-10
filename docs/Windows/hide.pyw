import random
import sys

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


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(SvgTitleBarButton(self))
        self.resize(30, 30)

        self.setFixedSize(30, 30)
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.windowEffect.setMicaEffect(self.winId())
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w - 10, int(h * settings[2] * 0.01))
        self.pushButton1 = PushButton(" ", self)
        self.pushButton1.clicked.connect(self.close)
        self.pushButton1.setGeometry(QtCore.QRect(0, 0, 150, 50))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
    def close(self):
        os.popen("main.pyw")
        sys.exit()


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
