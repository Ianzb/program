# coding: utf-8
from PyQt5.QtCore import QObject, pyqtSignal
from zb import *

class SignalBus(QObject):
    """ Signal bus """

    switchToSampleCard = pyqtSignal(str, int)
    supportSignal = pyqtSignal()


signalBus = SignalBus()