from ..widget import *
from .widget import *

class AboutPage(BasicPage):
    """
    关于页面
    """
    title = "关于"
    subtitle = "程序运行状态及相关信息"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.INFO)

        self.cardGroup1 = CardGroup("关于", self)

        self.updateSettingCard = UpdateSettingCard(self)
        self.helpSettingCard = HelpSettingCard(self)
        self.controlSettingCard = ControlSettingCard(self)
        self.aboutSettingCard = AboutSettingCard(self)

        self.cardGroup1.addWidget(self.updateSettingCard)
        self.cardGroup1.addWidget(self.helpSettingCard)
        self.cardGroup1.addWidget(self.controlSettingCard)
        self.cardGroup1.addWidget(self.aboutSettingCard)

        self.bigInfoCard = BigInfoCard(self, data=False)
        # self.bigInfoCard.setImg("Ianzb.png", "https://vip.123pan.cn/1813801926/%E8%B5%84%E6%BA%90/%E4%B8%AA%E4%BA%BA/%E5%A4%B4%E5%83%8F/png/%E5%A4%B4%E5%83%8F%E9%AB%98%E6%B8%85%E9%80%8F%E6%98%8E.png")
        self.bigInfoCard.image.setMinimumSize(150, 150)
        self.bigInfoCard.setTitle(program.AUTHOR_NAME)
        self.bigInfoCard.setInfo("Minecraft玩家，科幻迷，编程爱好者！")
        self.bigInfoCard.addUrl("Github", "https://github.com/Ianzb", FIF.GITHUB)
        self.bigInfoCard.addUrl("Bilibili", "https://space.bilibili.com/1043835434", FIF.LINK)
        self.bigInfoCard.addTag("Minecraft")
        self.bigInfoCard.addTag("编程")
        self.bigInfoCard.addTag("科幻")
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.setText("个人网站")
        self.bigInfoCard.mainButton.clicked.connect(lambda: webbrowser.open(program.AUTHOR_URL))
        self.bigInfoCard.mainButton.setIcon(FIF.LINK)

        self.vBoxLayout.addWidget(self.bigInfoCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
