import sys, os

try:
    from beta.source.custom import *
except:
    sys.path = [os.path.dirname(sys.argv[0])] + sys.path
    from source.custom import *


def searchSoftware(name: str, source: str) -> list:
    """
    搜索软件
    @param name: 名称
    @return: 列表
    """
    logging.debug(f"在{source}搜索应用{name}")
    list = []
    if source == "腾讯":
        data = requests.get(f"https://s.pcmgr.qq.com/tapi/web/searchcgi.php?type=search&keyword={name}&page=1&pernum=100", headers=program.REQUEST_HEADER, stream=True).text
        data = json.loads(data)["list"]
        for i in range(len(data)):
            data[i]["xmlInfo"] = f.xmlToJson(data[i]["xmlInfo"])
            if len(data[i]["xmlInfo"]["soft"]["feature"]) >= 20:
                data[i]["xmlInfo"]["soft"]["feature"] = data[i]["xmlInfo"]["soft"]["feature"][:20] + "..."
        for i in data:
            list.append({"名称": i["SoftName"],
                         "图标": f"https://pc3.gtimg.com/softmgr/logo/48/{i["xmlInfo"]["soft"]["logo48"]}",
                         "介绍": i["xmlInfo"]["soft"]["feature"],
                         "当前版本": i["xmlInfo"]["soft"]["versionname"],
                         "更新日期": i["xmlInfo"]["soft"]["publishdate"],
                         "文件大小": f"{eval("%.2f" % eval("%.5g" % (eval(i["xmlInfo"]["soft"]["filesize"]) / 1024 / 1024)))} MB",
                         "文件名称": i["xmlInfo"]["soft"]["filename"],
                         "下载链接": i["xmlInfo"]["soft"]["url"],
                         })
            if i["xmlInfo"]["soft"]["@osbit"] == "2":
                list[-1]["名称"] += " 64位"
            elif i["xmlInfo"]["soft"]["@osbit"] == "1":
                list[-1]["名称"] += " 32位"
    elif source == "360":
        data = requests.get(f"https://bapi.safe.360.cn/soft/search?keyword={name}&page=1", headers=program.REQUEST_HEADER, stream=True).text
        data = json.loads(data)["data"]["list"]
        for i in data:
            list.append({"名称": i["softname"],
                         "图标": i["logo"] if "https:" in i["logo"] else f"https:{i["logo"]}",
                         "介绍": f.clearString(i["desc"]),
                         "当前版本": i["version"],
                         "更新日期": i["date"],
                         "文件大小": i["size"],
                         "文件名称": f.splitPath(i["soft_download"], 0),
                         "下载链接": i["soft_download"],
                         })
    return list


class MyThread(QThread):
    """
    多线程模块
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data
        self.isCancel = False

    def run(self):
        if self.mode == "搜索应用":
            try:
                data = searchSoftware(self.data[0], self.data[1])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "下载文件":
            path = f.pathJoin(setting.read("downloadPath"), self.data[0])
            if f.existPath(path):
                i = 1
                while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))):
                    i = i + 1
                path = f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))
            logging.debug(f"开始下载文件{path}")
            path += ".zb.appstore.downloading"
            url = self.data[1]
            self.signalStr.emit(path)
            response = requests.get(url, headers=program.REQUEST_HEADER, stream=True)
            size = 0
            file_size = int(response.headers["content-length"])
            if response.status_code == 200:
                with open(path, "wb") as file:
                    for data in response.iter_content(256):
                        if self.isCancel:
                            self.signalBool.emit(True)
                            return
                        file.write(data)
                        size += len(data)
                        self.signalInt.emit(int(100 * size / file_size))
            logging.debug(f"文件{path}下载成功")

    def cancel(self):
        logging.debug("取消下载")
        self.isCancel = True


class AppInfoCard(SmallInfoCard):
    """
    应用商店信息卡片
    """

    def __init__(self, data: dict, source: str, parent: QWidget = None):
        super().__init__(parent)

        self.data = data
        self.source = source

        self.mainButton.setText("下载")
        self.mainButton.setIcon(FIF.DOWNLOAD)
        self.mainButton.setToolTip("下载软件")
        self.mainButton.installEventFilter(ToolTipFilter(self.mainButton, 1000))

        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data["名称"])}", self.data["图标"])
        self.setTitle(f"{self.data["名称"]}")

        self.setInfo(self.data["介绍"], 0)
        self.setInfo(self.data["文件大小"], 1)
        self.setInfo(f"当前版本：{self.data["当前版本"]}", 2)
        self.setInfo(f"更新日期：{self.data["更新日期"]}", 3)

    def mainButtonClicked(self):
        self.mainButton.setEnabled(False)

        self.thread = MyThread("下载文件", (self.data["文件名称"], self.data["下载链接"]))
        self.thread.signalStr.connect(self.thread1)
        self.thread.signalInt.connect(self.thread2)
        self.thread.signalBool.connect(self.thread3)
        self.thread.start()

        self.stateTooltip = StateToolTip(f"正在下载软件：{self.data["名称"]}", "正在连接到服务器...", self.parent().parent().parent().parent())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.closeButton.clicked.connect(self.thread.cancel)
        self.stateTooltip.show()

    def thread1(self, msg):
        self.filePath = msg

    def thread2(self, msg):
        self.stateTooltip.setContent(f"下载中，当前进度{msg}%")
        if msg == 100:
            f.moveFile(self.filePath, self.filePath.replace(".zb.appstore.downloading", ""))
            self.stateTooltip.setContent("下载成功")
            self.stateTooltip.setState(True)

            self.mainButton.setEnabled(True)

    def thread3(self, msg):
        if msg:
            f.delete(self.filePath)
        self.mainButton.setEnabled(True)


class AddonTab(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.SHOPPING_CART)

        self.vBoxLayout.setSpacing(8)

        self.lineEdit = SearchLineEdit(self)
        self.lineEdit.setPlaceholderText("应用名称")
        self.lineEdit.setToolTip("搜索应用，数据来源：\n 360软件中心\n 腾讯软件中心")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.lineEdit.returnPressed.connect(self.lineEditReturnPressed)
        self.lineEdit.searchButton.setEnabled(False)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)

        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("下载应用来源")
        self.comboBox.addItems(["360", "腾讯"])
        self.comboBox.setCurrentIndex(0)
        self.comboBox.setToolTip("选择下载应用来源")
        self.comboBox.installEventFilter(ToolTipFilter(self.comboBox, 1000))

        self.card = GrayCard()
        self.card.addWidget(self.lineEdit)
        self.card.addWidget(self.comboBox)

        self.progressRingLoading = IndeterminateProgressRing(self)

        self.loadingCard = DisplayCard(self)
        self.loadingCard.setDisplay(self.progressRingLoading)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

        self.cardGroup = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup)

    def lineEditChanged(self, text):
        self.lineEdit.searchButton.setEnabled(bool(text))

    def lineEditReturnPressed(self):
        self.lineEdit.searchButton.click()

    def searchButtonClicked(self):
        if self.lineEdit.text():
            self.vBoxLayout.itemAt(2).widget().deleteLater()
            self.cardGroup = CardGroup(self.view)
            self.vBoxLayout.addWidget(self.cardGroup)

            self.cardGroup.setTitleEnabled(False)
            self.lineEdit.setEnabled(False)
            self.comboBox.setEnabled(False)

            self.loadingCard.setText("搜索中...")
            self.loadingCard.show()

            self.thread = MyThread("搜索应用", [self.lineEdit.text(), self.comboBox.currentText()])
            self.thread.signalList.connect(self.thread1)
            self.thread.signalBool.connect(self.thread2)
            self.thread.start()

    def thread1(self, msg):
        self.loadingCard.hide()
        for i in msg:
            self.infoCard = AppInfoCard(i, self.comboBox.currentText())
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignTop)
            self.cardGroup.addWidget(self.infoCard)
        if msg:
            self.cardGroup.setTitle(f"搜索结果（{len(msg)}个）")
        else:
            self.cardGroup.setTitle(f"无搜索结果")
        self.cardGroup.setTitleEnabled(True)
        self.lineEdit.setEnabled(True)
        self.comboBox.setEnabled(True)

    def thread2(self, msg):
        if not msg:
            self.loadingCard.setText("网络连接失败！")
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox.setEnabled(True)
