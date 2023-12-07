import sys, os

sys.path = [os.path.dirname(sys.argv[0])] + sys.path
from source.custom import *
from chatapi import *


class AddonTab(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
