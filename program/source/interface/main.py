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

        self.image = ImageLabel(program.source("title.png"))
        self.image.setFixedSize(410, 135)

        self.card1 = SmallInfoCard(self)

        self.cardGroup1 = CardGroup(self)
        self.cardGroup1.addWidget(self.card1)

        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.cardGroup1)
