from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, setting, window, sf, progressCenter, addonInfo
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window
    progressCenter = addonBase.progressCenter
    addonInfo = addonBase.addonInfo


def addonWidget():
    return AddonMainPage(window)


class AddonMainPage(zbw.BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("测试")
        self.setIcon(FIF.CLOUD_DOWNLOAD)
