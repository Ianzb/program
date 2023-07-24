# coding:utf-8

from zb import *

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

from app.view.main_window import MainWindow

saveSetting(abs_cache, os.getpid())

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
translator = FluentTranslator(QLocale())
app.installTranslator(translator)
w = MainWindow()
w.show()
if ":\WINDOWS\system32".lower() in old_path.lower():
    w.hide()
app.exec_()
