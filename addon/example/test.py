import time

from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit(self):
    global program, log, setting
    program = addonBase.program
    log = addonBase.log
    setting = addonBase.setting
    return AddonMainPage()


class AddonMainPage(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CLOUD_DOWNLOAD)
