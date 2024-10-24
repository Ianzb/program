import time

from .widget import *


class AddonInfoMessageBox(MessageBox):
    """
    插件信息消息框
    """

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title=title, content=content, parent=parent)
        self.yesButton.deleteLater()
        self.cancelButton.setText("关闭")


class AddonInfoCard(SmallInfoCard):
    """
    插件信息卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.infoButton = ToolButton(FIF.INFO, self)
        self.infoButton.clicked.connect(self.showInfo)
        self.infoButton.hide()

        self.hBoxLayout.insertWidget(4, self.infoButton)
        self.hBoxLayout.setSpacing(8)

        self.offlineData: dict = {}
        self.onlineData: dict = {}
        self.infoState: str = ""

    def showInfo(self):
        if self.infoState:
            data = self.onlineData if self.onlineData else self.offlineData
            title = f"{data["name"]}插件信息"
            info = (f"ID：{data["id"]}\n版本：{data["version"]}\n作者：{data["author"]}\n介绍：{data["description"]}\n更新日期：{data["history"][data["version"]]["time"]}\n更新内容：{data["history"][data["version"]]["log"]}\n")
            messageBox = AddonInfoMessageBox(title, info, self.window())
            messageBox.show()

    def setInstalledData(self, data):
        self.offlineData = data
        self.setTitle(self.offlineData["name"])
        if "icon" in self.offlineData.keys():
            self.setImg(program.cache(f.joinPath("addon", f.getFileNameFromUrl(self.offlineData["icon"]))), self.offlineData["icon"], program.THREAD_POOL)
        self.setInfo(f"本地版本：{self.offlineData["version"]}", 0)
        if "history" in self.offlineData.keys():
            self.setInfo(f"更新时间：{self.offlineData["history"][self.offlineData["version"]]["time"]}", 1)
        self.mainButton.setText("加载中")
        self.mainButton.setEnabled(False)
        self.mainButton.setIcon(FIF.UPDATE)

        self.infoButton.show()
        self.infoState = "Offline"

    def setOnlineData(self, data):
        self.onlineData = data
        self.mainButton.setEnabled(True)

        self.setTitle(self.onlineData["name"])
        if "icon" in self.onlineData.keys():
            self.setImg(program.cache(f.joinPath("addon", f.getFileNameFromUrl(self.onlineData["icon"]))), self.onlineData["icon"], program.THREAD_POOL)
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
        elif not self.infoState:
            self.mainButton.setText("下载并安装")
        self.infoButton.show()
        self.infoState = "Online"


class MainPage(BasicTab):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"
    signalAddCardOffline = pyqtSignal(dict)
    signalAddCardOnline = pyqtSignal(dict)
    signalGetInfoOnline= pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.cardIdDict = {}
        self.onlineCount = 0

        self.image = ImageLabel(program.source("title.png"))
        self.image.setFixedSize(410, 135)

        self.card1 = GrayCard("插件管理", self)

        self.reloadButton = PushButton("重置", self, FIF.SYNC)
        self.reloadButton.setEnabled(False)
        self.reloadButton.clicked.connect(self.reload)
        self.card1.addWidget(self.reloadButton)

        self.cardGroup1 = CardGroup("插件列表", self)

        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.signalAddCardOffline.connect(self.addCardOffline)
        self.signalAddCardOnline.connect(self.addCardOnline)
        self.signalGetInfoOnline.connect(self.getOnlineAddonInfo)

        self.thread1 = program.THREAD_POOL.submit(self.getInstalledAddonList)

    def getInstalledAddonList(self):
        info = getInstalledAddonInfo()
        for k, v in info.items():
            self.signalAddCardOffline.emit(v)
        self.thread2 = program.THREAD_POOL.submit(self.getOnlineAddonListGeneral)

    def getOnlineAddonListGeneral(self):
        info: dict = getOnlineAddonDict()
        self.onlineCount = 0
        for k, v in info.items():
            self.signalGetInfoOnline.emit(v)
        while self.onlineCount < len(info.keys()):
            time.sleep(0.5)
        for i in self.cardIdDict.keys():
            if i not in info.keys():
                self.cardIdDict[i].mainButton.setText("无数据")
                self.cardIdDict[i].setInfo("无在线数据", 2)
        self.reloadButton.setEnabled(True)

    def getOnlineAddonInfo(self, info: str):
        try:
            info = getAddonInfoFromUrl(info)
            self.signalAddCardOnline.emit(info)
        except Exception as ex:
            Log.error(f"程序发生异常，无法获取插件{info["name"]}的在线信息，报错信息：{ex}！")
        self.onlineCount += 1

    def addCardOffline(self, info):
        if info["id"] not in self.cardIdDict.keys():

            try:
                card = AddonInfoCard(self)
                card.setInstalledData(info)
                self.cardIdDict[info["id"]] = card
                self.cardGroup1.addWidget(card)
                card.show()
            except Exception as ex:
                Log.error(f"程序发生异常，插件{info["name"]}的卡片组件无法加载，报错信息：{ex}！")
        else:
            try:
                self.cardIdDict[info["id"]].setInstalledData(info)
            except RuntimeError:
                Log.warning(f"组件{info["id"]}已被删除，无法设置数据了！")

    def addCardOnline(self, info):
        if info["id"] not in self.cardIdDict.keys():
            try:
                card = AddonInfoCard(self)
                card.setOnlineData(info)
                self.cardIdDict[info["id"]] = card
                self.cardGroup1.addWidget(card)
                card.show()
            except Exception as ex:
                Log.error(f"程序发生异常，插件{info["name"]}的卡片组件无法加载，报错信息：{ex}！")
        else:
            try:
                self.cardIdDict[info["id"]].setOnlineData(info)
            except RuntimeError:
                Log.warning(f"组件{info["id"]}已被删除，无法设置数据了！")
        self.onlineCount += 1

    def reload(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup1.cardLayout.clearWidget()
        self.cardIdDict = {}
        self.getInstalledAddonList()
