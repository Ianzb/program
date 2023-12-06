from ..custom import *


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

        self.thread = NewThread("下载文件", (self.data["文件名称"], self.data["下载链接"]))
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


class AppStoreTab(BasicTab):
    """
    应用商店页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)

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

            self.thread = NewThread("搜索应用", [self.lineEdit.text(), self.comboBox.currentText()])
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
