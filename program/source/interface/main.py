import time
import traceback

from .widget import *


class AddonInfoMessageBox(zbw.ScrollMessageBox):
    """
    插件信息消息框
    """

    def __init__(self, parent=None):
        super().__init__(title="", content="", parent=parent)
        self.widget.setFixedSize(600, 400)

        self.image = zbw.WebImage(self)

        self.contentLabel.setSelectable()

        self.yesButton.deleteLater()
        self.cancelButton.setText("关闭")
        self.cancelButton.clicked.connect(self.closeMessageBox)

        self.widget.adjustSize()

    def closeMessageBox(self):
        self.accept()
        self.accepted.emit()

    def setData(self, data: dict):
        if data.get("icon"):
            if zb.isUrl(data.get("icon")):
                self.image.setImg(zb.joinPath(program.ADDON_PATH, data.get("id", ""), zb.getFileNameFromUrl(data.get("icon"))), data.get("icon"))
                self.scrollLayout.insertWidget(0, self.image)
            else:
                if zb.existPath(zb.joinPath(program.ADDON_PATH, data.get("id", ""), data.get("icon"))):
                    self.image.setImg(zb.joinPath(program.ADDON_PATH, data.get("id", ""), data.get("icon")))
                    self.scrollLayout.insertWidget(0, self.image)


class AddonInfoCard(zbw.SmallInfoCard):
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
        self.messageBox.hide()

    def downloadAddon(self):
        if self.onlineData:
            self.window().addAddonFinishEvent.connect(self.addAddon)
            self.mainButton.setEnabled(False)
            self.removeButton.setEnabled(False)
            self.window().downloadAddon(self.onlineData)

    def addAddon(self, msg):
        data = self.onlineData if self.onlineData else self.offlineData
        if msg == data.get("id"):
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
        self.setTitle(f"{data.get("name", "")}（已删除）")
        self.setText("本地未安装", 0)
        self.setText("", 1)

    def showInfo(self):
        if self.offlineData or self.onlineData:
            data = self.onlineData if self.onlineData else self.offlineData
            version = data.get("version", "")
            history = data.get("history", {}).get(version, {})
            info = (
                f"ID：{data.get("id", "")}\n版本：{version} ({data.get("version_code", 0)})\n作者：{data.get("author", "")}\n介绍：{data.get("description", "")}\n"
                f"更新日期：{history.get("time", "")}\n更新内容：{history.get("log", "")}\n"
            )
            self.messageBox.setData(data)
            self.messageBox.titleLabel.setText(f"{data.get("name", "")} 插件信息")
            self.messageBox.contentLabel.setText(info)
            self.messageBox.show()

    def setInstalledData(self, data):
        self.offlineData = data
        self.setTitle(self.offlineData.get("name", ""))
        if self.offlineData.get("icon"):
            if zb.isUrl(self.offlineData.get("icon")):
                self.setImg(
                    zb.joinPath(program.ADDON_PATH, self.offlineData.get("id", ""), zb.getFileNameFromUrl(self.offlineData.get("icon"))),
                    self.offlineData.get("icon"),
                    program.THREAD_POOL,
                )
            else:
                if zb.existPath(zb.joinPath(program.ADDON_PATH, self.offlineData.get("id", ""), self.offlineData.get("icon"))):
                    self.setImg(zb.joinPath(program.ADDON_PATH, self.offlineData.get("id", ""), self.offlineData.get("icon")))
        self.setText(f"本地版本：{self.offlineData.get("version", "")}", 0)
        if self.offlineData.get("history"):
            ver = self.offlineData.get("version", "")
            self.setText(
                f"更新时间：{self.offlineData.get("history", {}).get(ver, {}).get("time", "")}",
                1,
            )
        self.setButtonStatement()
        self.infoButton.show()
        self.removeButton.show()

    def setOnlineData(self, data):
        self.onlineData = data
        self.mainButton.setEnabled(True)

        self.setTitle(self.onlineData.get("name", ""))
        if self.onlineData.get("icon"):
            if zb.isUrl(self.onlineData.get("icon")):
                self.setImg(
                    zb.joinPath(program.ADDON_PATH, self.onlineData.get("id", ""), zb.getFileNameFromUrl(self.onlineData.get("icon"))),
                    self.onlineData.get("icon"),
                    program.THREAD_POOL,
                )
            else:
                if zb.existPath(zb.joinPath(program.ADDON_PATH, self.onlineData.get("id", ""), self.onlineData.get("icon"))):
                    self.setImg(zb.joinPath(program.ADDON_PATH, self.onlineData.get("id", ""), self.onlineData.get("icon")))
        self.setText(f"在线版本：{self.onlineData.get("version", "")}", 2)
        if self.onlineData.get("history"):
            ver = self.onlineData.get("version", "")
            self.setText(
                f"更新时间：{self.onlineData.get("history", {}).get(ver, {}).get("time", "")}",
                3,
            )
        self.setButtonStatement()
        self.infoButton.show()
        self.removeButton.show()

    def setButtonStatement(self):
        if self.onlineData and self.offlineData:
            if self.onlineData.get("version") != self.offlineData.get("version"):
                self.mainButton.setText("更新")
                self.mainButton.setIcon(FIF.UPDATE)
                self.mainButton.setEnabled(True)
            elif self.onlineData.get("version") == self.offlineData.get("version"):
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

    def deleteLater(self):
        super().deleteLater()
        self.messageBox.deleteLater()


class MainPage(zbw.BasicTab):
    """
    主页
    """
    signalAddCardOffline = pyqtSignal(dict)
    signalAddCardOnline = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitle("主页")
        self.setIcon(FIF.HOME)

        self.addon_list = {}
        self.onlineCount = 0

        self.image = ImageLabel(program.source("title.png"))
        self.image.setFixedSize(410, 135)

        self.card1 = zbw.GrayCard("插件管理", self)

        self.reloadButton = PushButton("刷新", self, FIF.SYNC)
        self.reloadButton.setEnabled(False)
        self.reloadButton.clicked.connect(self.reload)
        self.card1.addWidget(self.reloadButton)

        self.cardGroup1 = zbw.CardGroup("插件列表", self)

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
        for i in self.cardGroup1._cardMap.keys():
            if i not in self.addon_list.keys():
                self.cardGroup1._cardMap[i].mainButton.setText("无数据")
                self.cardGroup1._cardMap[i].setText("无在线数据", 2)
        self.reloadButton.setEnabled(True)

    def getOnlineAddonInfo(self, info: str):
        try:
            info = program.getAddonInfoFromUrl(info)
            self.signalAddCardOnline.emit(info)
        except:
            logging.error(f"程序发生异常，无法获取插件{info}的在线信息，报错信息：{traceback.format_exc()}！")
        self.onlineCount += 1

    def addCardOffline(self, info):
        if info.get("id") not in self.cardGroup1._cardMap:
            try:
                card = AddonInfoCard(self)
                card.setInstalledData(info)
                self.cardGroup1.addCard(card, info["id"])
                card.show()
            except:
                logging.error(f"程序发生异常，插件{info.get("name", "")}的卡片组件无法加载，报错信息：{traceback.format_exc()}！")
        else:
            try:
                self.cardGroup1.getCard(info["id"]).setInstalledData(info)
            except RuntimeError:
                logging.warning(f"组件{info.get("id", "")}已被删除，无法设置数据了！")

    def addCardOnline(self, info):
        if info.get("id") not in self.cardGroup1._cardMap:
            try:
                card = AddonInfoCard(self)
                card.setOnlineData(info)
                self.cardGroup1.addCard(card, info["id"])
                card.show()
            except:
                logging.error(f"程序发生异常，插件{info.get("name", "")}的卡片组件无法加载，报错信息：{traceback.format_exc()}！")
        else:
            try:
                self.cardGroup1.getCard(info["id"]).setOnlineData(info)
            except RuntimeError:
                logging.warning(f"组件{info.get("id", "")}已被删除，无法设置数据了！")
        self.onlineCount += 1

    def reload(self):
        self.reloadButton.setEnabled(False)
        self.cardGroup1.clearCard()
        program.THREAD_POOL.submit(self.getInstalledAddonList)
