import time

from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, setting, window
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window


def addonWidget():
    return AddonMainPage(window)


class AddonMainPage(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CLOUD_DOWNLOAD)
