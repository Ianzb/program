import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.zbWidgetLib import *

try:
    from program.source.zbWidgetLib import *
except:
    pass
def init(p,l,s,window):
    global program,Log,setting
    program = p
    Log = l
    setting = s

    class MainPage(BasicTab):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setIcon(FIF.CLOUD_DOWNLOAD)
    return MainPage(window)