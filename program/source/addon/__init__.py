import logging
import subprocess
import traceback
import importlib
import time
from concurrent.futures import ThreadPoolExecutor

import functools
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qtpy import *
from qfluentwidgets import *
from qfluentwidgets.components.material import *
from qfluentwidgets import FluentIcon as FIF

import zbToolLib as zb
import zbWidgetLib as zbw
from zbWidgetLib import ZBF
from qtpy import *

sys.path.append(os.path.dirname(sys.argv[0]))


class AddonBase:
    def __init__(self):
        self.program = None
        self.log = None
        self.setting = None

    def set(self, __program, __setting, __window, __progress_center):
        self.program = __program
        self.setting = __setting
        self.window = __window
        self.progressCenter = __progress_center
