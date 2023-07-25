from ..zb import *
from PyQt5.QtCore import *

class SignalBus(QObject):
    switchToSampleCard = pyqtSignal(str, int)
    supportSignal = pyqtSignal()


signalBus = SignalBus()