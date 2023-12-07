import sys, os

try:
    from beta.source.custom import *
except:
    sys.path = [os.path.dirname(sys.argv[0])] + sys.path
    from source.custom import *
os.chdir(os.path.dirname(__file__))
from chatapi import *


class AddonTab(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
