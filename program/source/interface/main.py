from ..widget import *

class MainPage(BasicTab):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.titleImage = Image("logo.png", "https://ianzb.github.io/project/img/program.png", self, False)
        self.titleImage.setFixedSize(410, 135)
        self.card1 = IntroductionCard(self)
        self.card1.setTitle(f"欢迎使用")
        self.card1.setText(f"一款基于Python的Windows多功能工具箱！")
        self.card1.setImg(program.ICON)

        self.card2 = IntroductionCard(self)
        self.card2.setTitle("插件功能")
        self.card2.setText(f"选择并安装你需要的插件，享受程序功能！")
        self.card2.setImg("Ianzb.png", "https://vip.123pan.cn/1813801926/%E8%B5%84%E6%BA%90/%E4%B8%AA%E4%BA%BA/%E5%A4%B4%E5%83%8F/png/%E5%A4%B4%E5%83%8F%E9%AB%98%E6%B8%85%E9%80%8F%E6%98%8E.png")

        self.card3 = IntroductionCard(self)
        self.card3.setTitle("问题反馈")
        self.card3.setText(f"在Github Issue中提交使用过程中遇到的问题！")
        self.card3.setImg("Github.png", "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png")

        self.flowLayout = FlowLayout()
        self.flowLayout.addWidget(self.card1)
        self.flowLayout.addWidget(self.card2)
        self.flowLayout.addWidget(self.card3)

        self.vBoxLayout.addWidget(self.titleImage, 0, Qt.AlignCenter)
        self.vBoxLayout.addLayout(self.flowLayout, Qt.AlignCenter)

        self.cardGroup1 = CardGroup(self)
        self.addonSettingCard = AddonSettingCard(self)
        self.cardGroup1.addWidget(self.addonSettingCard)
        self.vBoxLayout.addWidget(self.cardGroup1)