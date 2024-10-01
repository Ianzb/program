from ..widget import *
from .widget import *

class MainPage(BasicTab):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)
