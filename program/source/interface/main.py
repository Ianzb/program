from .widget import *


class AddonInfoCard(SmallInfoCard):
    """
    插件信息卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent,animation=True)

        self.offlineData: dict = {}
        self.onlineData: dict = {}
        self.infoState: str = ""

    def setInstalledData(self, data):
        self.offlineData = data
        self.setTitle(self.offlineData["name"])
        if "icon" in self.offlineData.keys():
            self.setImg(program.cache(joinPath("addon", getFileNameFromUrl(self.offlineData["icon"]))), self.offlineData["icon"], program.THREAD_POOL)
        self.setInfo(f"当前版本：{self.offlineData["version"]}", 0)
        if "history" in self.offlineData.keys():
            self.setInfo(f"更新时间：{self.offlineData["history"][self.offlineData["version"]]["time"]}", 1)
        self.mainButton.setText("加载中")
        self.mainButton.setEnabled(False)
        self.mainButton.setIcon(FIF.UPDATE)
        self.infoState = "Offline"

    def setOnlineData(self, data):
        self.onlineData = data
        self.mainButton.setEnabled(True)

        self.setTitle(self.onlineData["name"])
        if "icon" in self.onlineData.keys():
            self.setImg(program.cache(joinPath("addon", getFileNameFromUrl(self.onlineData["icon"]))), self.onlineData["icon"], program.THREAD_POOL)
        self.setInfo(f"在线版本：{self.onlineData["version"]}", 2)
        if "history" in self.onlineData.keys():
            self.setInfo(f"更新时间：{self.onlineData["history"][self.onlineData["version"]]["time"]}", 3)
        if self.infoState == "Offline":
            if self.onlineData["version"] != self.offlineData["version"]:
                self.mainButton.setText("更新")
                self.mainButton.setIcon(FIF.UPDATE)
            elif self.onlineData["version"] == self.offlineData["version"]:
                self.mainButton.setText("重新安装")
                self.mainButton.setIcon(FIF.DOWNLOAD)
        self.infoState = "Online"



class MainPage(BasicTab):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"
    signalAddCardOffline = pyqtSignal(dict)
    signalAddCardOnline = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.cardIdDict = {}

        self.image = ImageLabel(program.source("title.png"))
        self.image.setFixedSize(410, 135)

        self.card1 = GrayCard("插件", self)

        self.reloadButton = PushButton("重置", self, FIF.SYNC)
        self.reloadButton.setEnabled(False)
        self.reloadButton.clicked.connect(self.reload)
        self.card1.addWidget(self.reloadButton)

        self.cardGroup1 = CardGroup(self)

        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.signalAddCardOffline.connect(self.addCardOffline)
        self.signalAddCardOnline.connect(self.addCardOnline)

        self.thread1=program.THREAD_POOL.submit(self.getInstalledAddonList)

    def getInstalledAddonList(self):
        info = getInstalledAddonInfo()
        for k, v in info.items():
            self.signalAddCardOffline.emit(v)
        self.thread2=program.THREAD_POOL.submit(self.getOnlineAddonListGeneral)

    def getOnlineAddonListGeneral(self):
        info = getOnlineAddonDict()
        for k, v in info.items():
            self.getOnlineAddonInfo(v)
        self.reloadButton.setEnabled(True)

    def getOnlineAddonInfo(self, info):
        info = getAddonInfoFromUrl(info)
        self.signalAddCardOnline.emit(info)

    def addCardOffline(self, info):
        if info["id"] not in self.cardIdDict.keys():
            card = AddonInfoCard(self)
            card.setInstalledData(info)
            self.cardIdDict[info["id"]] = card
            self.cardGroup1.addWidget(card)
            card.s
        else:
            try:
                self.cardIdDict[info["id"]].setInstalledData(info)
            except RuntimeError:
                logging.warning(f"组件{info["id"]}已被删除，无法设置数据了！")

    def addCardOnline(self, info):
        if info["id"] not in self.cardIdDict.keys():
            card = AddonInfoCard(self)
            card.setOnlineData(info)
            self.cardIdDict[info["id"]] = card
            self.cardGroup1.addWidget(card)
        else:
            try:
                self.cardIdDict[info["id"]].setOnlineData(info)
            except RuntimeError:
                logging.warning(f"组件{info["id"]}已被删除，无法设置数据了！")

    def reload(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup1.cardLayout.clearWidget()
        self.cardIdDict = {}
        self.getInstalledAddonList()
        # self.thread1.cancel()
        # if self.thread2:
        #     self.thread2.cancel()
