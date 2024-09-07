import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.widget.custom import *

try:
    from program.source.widget.custom import *
except:
    pass


def xmlToJson(data: str) -> dict:
    """
    xml转json
    @param data: xml字符串
    @return: 字典格式json数据
    """
    from .xmltodict import parse
    data = parse(data)
    return data


def searchSoftware(name: str, source: str) -> list:
    """
    搜索软件
    @param name: 名称
    @return: 列表
    """
    logging.debug(f"在{source}搜索应用{name}")
    list = []
    if source == "腾讯":
        data = f.requestGet(f"https://s.pcmgr.qq.com/tapi/web/searchcgi.php?type=search&keyword={name}&page=1&pernum=100", program.REQUEST_HEADER)
        data = json.loads(data)["list"]
        for i in range(len(data)):
            data[i]["xmlInfo"] = xmlToJson(data[i]["xmlInfo"])
        for i in data:
            list.append({"名称": i["SoftName"],
                         "图标": f"https://pc3.gtimg.com/softmgr/logo/48/{i["xmlInfo"]["soft"]["logo48"]}",
                         "介绍": i["xmlInfo"]["soft"]["feature"],
                         "当前版本": i["xmlInfo"]["soft"]["versionname"],
                         "更新日期": i["xmlInfo"]["soft"]["publishdate"],
                         "文件大小": f.fileSizeAddUnit(int(i["xmlInfo"]["soft"]["filesize"])),
                         "文件名称": i["xmlInfo"]["soft"]["filename"],
                         "下载链接": i["xmlInfo"]["soft"]["url"],
                         })
            if i["xmlInfo"]["soft"]["@osbit"] == "2":
                list[-1]["名称"] += " 64位"
            elif i["xmlInfo"]["soft"]["@osbit"] == "1":
                list[-1]["名称"] += " 32位"
    elif source == "360":
        data = f.requestGet(f"https://bapi.safe.360.cn/soft/search?keyword={name}&page=1", program.REQUEST_HEADER)
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


class MyThread(QThread, SignalBase):
    """
    多线程模块
    """

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data

    def run(self):
        logging.info(f"应用商店插件 {self.mode} 线程开始")
        if self.mode == "搜索应用":
            try:
                data = searchSoftware(self.data[0], self.data[1])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        logging.info(f"应用商店插件 {self.mode} 线程结束")


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

        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data["名称"])}.png", self.data["图标"])
        self.setTitle(f"{self.data["名称"]}")

        self.setInfo(self.data["介绍"], 0)
        self.setInfo(self.data["文件大小"], 1)
        self.setInfo(f"当前版本：{self.data["当前版本"]}", 2)
        self.setInfo(f"更新日期：{self.data["更新日期"]}", 3)

    def mainButtonClicked(self):
        DownloadWidget(self.data["下载链接"], self.data["文件名称"], self.parent().parent().parent())


class AddonPage(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.SHOPPING_CART)

        self.vBoxLayout.setSpacing(8)

        self.lineEdit = AcrylicSearchLineEdit(self)
        self.lineEdit.setPlaceholderText("应用名称")
        self.lineEdit.setToolTip("搜索应用，数据来源：\n 360软件中心\n 腾讯软件中心")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.lineEdit.returnPressed.connect(self.lineEditReturnPressed)
        self.lineEdit.searchButton.setEnabled(False)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)

        self.comboBox = AcrylicComboBox(self)
        self.comboBox.setPlaceholderText("下载应用来源")
        self.comboBox.addItems(["360", "腾讯"])
        self.comboBox.setCurrentIndex(0)
        self.comboBox.setToolTip("选择下载应用来源")
        self.comboBox.installEventFilter(ToolTipFilter(self.comboBox, 1000))

        self.card = GrayCard("应用商店")
        self.card.addWidget(self.lineEdit)
        self.card.addWidget(self.comboBox)

        self.loadingCard = LoadingCard(self)
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
