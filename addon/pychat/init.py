import sys, os

sys.path = [os.path.dirname(sys.argv[0])] + sys.path
from source.custom import *
os.chdir(os.path.dirname(__file__))
from .chatapi import *


class AddonPage(BasicPage):
    """
    插件主页面
    """
    title = "PyChat"
    subtitle = "聊天"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
