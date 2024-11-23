import time

from .widget import *


class AddonInfoMessageBox(MessageBox):
    """
    插件信息消息框
    """

    def __init__(self, parent=None):
        super().__init__(title="", content="", parent=parent)
        self.image = Image(self)

        self.yesButton.deleteLater()
        self.cancelButton.setText("关闭")
        self.cancelButton.clicked.connect(self.closeMessageBox)

    def closeMessageBox(self):
        self.accept()
        self.accepted.emit()

    def setData(self, data: dict):
        if "icon" in data.keys():
            if f.isUrl(data["icon"]):
                self.image.setImg(program.cache(f.joinPath("addon", f.getFileNameFromUrl(data["icon"]))), data["icon"])
                self.textLayout.insertWidget(1, self.image)
            else:
                if f.existPath(f.joinPath(program.ADDON_PATH, data["id"], data["icon"])):
                    self.image.setImg(f.joinPath(program.ADDON_PATH, data["id"], data["icon"]))
                    self.textLayout.insertWidget(1, self.image)


class AddonInfoCard(SmallInfoCard):
    """
    插件信息卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.mainButton.clicked.connect(self.downloadAddon)

        self.infoButton = ToolButton(FIF.INFO, self)
        self.infoButton.clicked.connect(self.showInfo)
        self.infoButton.hide()

        self.removeButton = ToolButton(FIF.DELETE, self)
        self.removeButton.clicked.connect(self.removeAddon)
        self.removeButton.hide()

        self.hBoxLayout.insertWidget(4, self.infoButton)
        self.hBoxLayout.insertWidget(7, self.removeButton)
        self.hBoxLayout.setSpacing(8)

        self.offlineData: dict = {}
        self.onlineData: dict = {}

        self.setButtonStatement()

        self.messageBox = AddonInfoMessageBox(self.window())

    def downloadAddon(self):
        if self.onlineData:
            self.window().addAddonFinishEvent.connect(self.addAddon)
            self.mainButton.setEnabled(False)
            self.removeButton.setEnabled(False)
            self.window().downloadAddon(self.onlineData)

    def addAddon(self, msg):
        data = self.onlineData if self.onlineData else self.offlineData
        if msg == data["id"]:
            self.mainButton.setEnabled(True)
            self.removeButton.setEnabled(True)
            self.window().addAddonFinishEvent.disconnect(self.addAddon)
            self.setInstalledData(self.onlineData)

    def removeAddon(self):
        data = self.onlineData if self.onlineData else self.offlineData
        self.window().removeAddon(data)
        self.removeButton.setEnabled(False)
        self.infoButton.setEnabled(False)
        self.mainButton.setEnabled(False)
        self.setTitle(f"{data["name"]}（已删除）")
        self.setInfo("本地未安装", 0)
        self.setInfo("", 1)

    def showInfo(self):
        if self.offlineData or self.onlineData:
            data = self.onlineData if self.onlineData else self.offlineData
            title = f"{data["name"]}插件信息"
            info = f"ID：{data["id"]}\n版本：{data["version"]}\n作者：{data["author"]}\n介绍：{data["description"]}\n更新日期：{data["history"][data["version"]]["time"]}\n更新内容：{data["history"][data["version"]]["log"]}\n"
            self.messageBox.setData(data)
            self.messageBox.titleLabel.setText(title)
            self.messageBox.contentLabel.setText(info)
            self.messageBox.show()

    def setInstalledData(self, data):
        self.offlineData = data
        self.setTitle(self.offlineData["name"])
        if "icon" in self.offlineData.keys():
            if f.isUrl(self.offlineData["icon"]):
                self.setImg(program.cache(f.joinPath("addon", f.getFileNameFromUrl(self.offlineData["icon"]))), self.offlineData["icon"], program.THREAD_POOL)
            else:
                if f.existPath(f.joinPath(program.ADDON_PATH, self.offlineData["id"], self.offlineData["icon"])):
                    self.setImg(f.joinPath(program.ADDON_PATH, self.offlineData["id"], self.offlineData["icon"]))
        self.setInfo(f"本地版本：{self.offlineData["version"]}", 0)
        if "history" in self.offlineData.keys():
            self.setInfo(f"更新时间：{self.offlineData["history"][self.offlineData["version"]]["time"]}", 1)
        self.setButtonStatement()
        self.infoButton.show()
        self.removeButton.show()

    def setOnlineData(self, data):
        self.onlineData = data
        self.mainButton.setEnabled(True)

        self.setTitle(self.onlineData["name"])
        if "icon" in self.onlineData.keys():
            if f.isUrl(self.onlineData["icon"]):
                self.setImg(program.cache(f.joinPath("addon", f.getFileNameFromUrl(self.onlineData["icon"]))), self.onlineData["icon"], program.THREAD_POOL)
            else:
                if f.existPath(f.joinPath(program.ADDON_PATH, self.onlineData["id"], self.onlineData["icon"])):
                    self.setImg(f.joinPath(program.ADDON_PATH, self.onlineData["id"], self.onlineData["icon"]))
        self.setInfo(f"在线版本：{self.onlineData["version"]}", 2)
        if "history" in self.onlineData.keys():
            self.setInfo(f"更新时间：{self.onlineData["history"][self.onlineData["version"]]["time"]}", 3)
        self.setButtonStatement()
        self.infoButton.show()
        self.removeButton.show()

    def setButtonStatement(self):
        if self.onlineData and self.offlineData:
            if self.onlineData["version"] != self.offlineData["version"]:
                self.mainButton.setText("更新")
                self.mainButton.setIcon(FIF.UPDATE)
                self.mainButton.setEnabled(True)
            elif self.onlineData["version"] == self.offlineData["version"]:
                self.mainButton.setText("重新安装")
                self.mainButton.setIcon(FIF.DOWNLOAD)
                self.mainButton.setEnabled(True)
        elif not self.onlineData and self.offlineData:
            self.mainButton.setText("仅本地")
            self.mainButton.setIcon(FIF.DOWNLOAD)
            self.mainButton.setEnabled(False)
        elif self.onlineData and not self.offlineData:
            self.mainButton.setText("下载")
            self.mainButton.setIcon(FIF.DOWNLOAD)
            self.mainButton.setEnabled(True)
        else:
            self.mainButton.setText("加载中")
            self.mainButton.setIcon(FIF.SEARCH)
            self.mainButton.setEnabled(False)


class MainPage(BasicTab):
    """
    主页
    """
    title = "主页"
    signalAddCardOffline = pyqtSignal(dict)
    signalAddCardOnline = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)

        self.addon_list = {}
        self.cardIdDict = {}
        self.onlineCount = 0

        self.image = ImageLabel(program.source("title.png"))
        self.image.setFixedSize(410, 135)

        self.card1 = GrayCard("插件管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.setEnabled(False)
        self.reloadButton.clicked.connect(self.reload)
        self.card1.addWidget(self.reloadButton)

        self.cardGroup1 = CardGroup("插件列表", self)

        self.vBoxLayout.addWidget(self.image, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.signalAddCardOffline.connect(self.addCardOffline)
        self.signalAddCardOnline.connect(self.addCardOnline)

        program.THREAD_POOL.submit(self.getInstalledAddonList)

    def getInstalledAddonList(self):
        info = program.getInstalledAddonInfo()
        for k, v in info.items():
            self.signalAddCardOffline.emit(v)
        program.THREAD_POOL.submit(self.getOnlineAddonList)

    def getOnlineAddonList(self):
        self.addon_list = program.getOnlineAddonDict()

        self.onlineCount = 0
        for k, v in self.addon_list.items():
            program.THREAD_POOL.submit(self.getOnlineAddonInfo, v)
        while self.onlineCount < len(self.addon_list.keys()):
            time.sleep(0.5)
        for i in self.cardIdDict.keys():
            if i not in self.addon_list.keys():
                self.cardIdDict[i].mainButton.setText("无数据")
                self.cardIdDict[i].setInfo("无在线数据", 2)
        self.reloadButton.setEnabled(True)

    def getOnlineAddonInfo(self, info: str):
        try:
            info = program.getAddonInfoFromUrl(info)
            self.signalAddCardOnline.emit(info)
        except Exception as ex:
            log.error(f"程序发生异常，无法获取插件{info["name"]}的在线信息，报错信息：{ex}！")
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
                log.error(f"程序发生异常，插件{info["name"]}的卡片组件无法加载，报错信息：{ex}！")
        else:
            try:
                self.cardIdDict[info["id"]].setInstalledData(info)
            except RuntimeError:
                log.warning(f"组件{info["id"]}已被删除，无法设置数据了！")

    def addCardOnline(self, info):
        if info["id"] not in self.cardIdDict.keys():
            try:
                card = AddonInfoCard(self)
                card.setOnlineData(info)
                self.cardIdDict[info["id"]] = card
                self.cardGroup1.addWidget(card)
                card.show()
            except Exception as ex:
                log.error(f"程序发生异常，插件{info["name"]}的卡片组件无法加载，报错信息：{ex}！")
        else:
            try:
                self.cardIdDict[info["id"]].setOnlineData(info)
            except RuntimeError:
                log.warning(f"组件{info["id"]}已被删除，无法设置数据了！")
        self.onlineCount += 1

    def reload(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup1.cardLayout.clearWidget()
        self.cardIdDict = {}
        program.THREAD_POOL.submit(self.getInstalledAddonList)
