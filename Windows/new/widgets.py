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
        self.setQss()
        qconfig.themeChanged.connect(self.setQss)
    def setQss(self):
        if isDarkTheme():
            self.setStyleSheet("QScrollArea {background-color: rgb(39, 39, 39); border: none; border-top-left-radius: 10px;}")
        else:
            self.setStyleSheet("QScrollArea {background-color: rgb(249, 249, 249); border: none; border-top-left-radius: 10px;}")