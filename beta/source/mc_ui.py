from .web_ui import *


class ChangeableTab(BasicTab):
    """
    多页面标签页
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("资源管理")
        self.page = {}
        self.onShowPage = None
        self.onShowName = None

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

    def addPage(self, widget, name=None):
        """
        添加页面
        @param widget: 组件
        @param name: 组件名称（默认为objectName）
        """
        widget.setParent(self)
        widget.hide()
        if not name:
            name = widget.objectName()
        self.page[name] = widget
        self.vBoxLayout.addWidget(widget)

    def showPage(self, name):
        """
        展示页面
        @param name: 组件名称
        """
        self.hidePage()
        self.page[name].show()
        self.onShowPage = self.page[name]
        self.onShowName = name

    def hidePage(self):
        """
        隐藏页面
        """
        if self.onShowPage:
            self.onShowPage.hide()


class MinecraftPathSettingCard(SettingCard):
    """
    我的世界路径设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "Java版目录", "默认选择.minecraft文件夹，若开启版本隔离请选择版本文件夹", parent)
        self.button1 = PushButton("选择", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("设置Java版目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择要添加的Minecraft Java版目录", setting.read("minecraftJavaPath"))
        if f.existPath(get):
            setting.save("minecraftJavaPath", get)


class AddonSettingTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("设置")
        self.cardGroup1 = CardGroup("设置", self)

        self.cardGroup1.addWidget(MinecraftPathSettingCard(self))

        self.vBoxLayout.addWidget(self.cardGroup1)


class AddonManageTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("管理")
        self.cardGroup1 = CardGroup("管理", self)

        self.grayCard = GrayCard("设置", self)

        self.settingButton = PushButton("设置", self, FIF.SETTING)
        self.settingButton.clicked.connect(self.button1Clicked)
        self.settingButton.setToolTip("打开插件设置")
        self.settingButton.installEventFilter(ToolTipFilter(self.settingButton, 1000))

        self.grayCard.addWidget(self.settingButton)

        self.cardGroup1.addWidget(self.grayCard)

        self.vBoxLayout.addWidget(self.cardGroup1)

    def button1Clicked(self):
        self.parent().showPage("设置")


class AddonPage(BasicTabPage):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.GAME)
        self.setObjectName("MC资源管理器")

        self.page = ChangeableTab(self)
        self.page.addPage(AddonManageTab())
        self.page.addPage(AddonSettingTab())
        self.page.showPage("管理")

        self.addPage(self.page)
