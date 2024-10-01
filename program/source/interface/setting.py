from ..widget import *
from .widget import *

class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "个性化设置程序功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.SETTING)

        self.cardGroup1 = CardGroup("外观", self)
        self.cardGroup2 = CardGroup("行为", self)
        self.cardGroup3 = CardGroup("功能", self)

        self.themeSettingCard = ThemeSettingCard(self)
        self.colorSettingCard = ColorSettingCard(self)
        self.micaEffectSettingCard = MicaEffectSettingCard(self)

        self.startupSettingCard = StartupSettingCard(self)
        self.traySettingCard = TraySettingCard(self)
        self.hideSettingCard = HideSettingCard(self)

        self.downloadSettingCard = DownloadSettingCard(self)

        self.cardGroup1.addWidget(self.themeSettingCard)
        self.cardGroup1.addWidget(self.colorSettingCard)
        self.cardGroup1.addWidget(self.micaEffectSettingCard)

        self.cardGroup2.addWidget(self.startupSettingCard)
        self.cardGroup2.addWidget(self.traySettingCard)
        self.cardGroup2.addWidget(self.hideSettingCard)

        self.cardGroup3.addWidget(self.downloadSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup3, 0, Qt.AlignTop)

        if not (WINDOWS_VERSION[0] >= 10 and WINDOWS_VERSION[2] >= 22000):
            self.micaEffectSettingCard.hide()
