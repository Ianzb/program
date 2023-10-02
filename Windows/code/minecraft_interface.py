from gallery_interface import *
from mod_downloader import *


class minecraftInterface(GalleryInterface):

    def __init__(self, parent=None):
        super().__init__(
            title="",
            subtitle="",
            parent=parent
        )
        # 组件设置
        self.setObjectName("Minecraft")
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.modDownload = GalleryInterface("", "模组下载", parent=self)
        self.modUpdate = GalleryInterface("", "模组更新", parent=self)
        self.modDownload.vBoxLayout.setSpacing(15)
        self.modDownload.toolBar.setParent(None)
        self.modUpdate.toolBar.setParent(None)
        self.modDownload.setViewportMargins(0, 0, 0, 0)
        self.modDownload.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.modUpdate.setViewportMargins(0, 0, 0, 0)
        self.modUpdate.vBoxLayout.setContentsMargins(0, 20, 0, 0)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setPlaceholderText("输入模组名称")
        self.lineEdit.setFixedSize(300, 33)
        self.lineEdit.setMaxLength(50)
        self.thread = newThread(10)
        self.thread.signal2.connect(self.btn1_2)
        self.thread.start()
        self.comboBox = EditableComboBox()
        self.comboBox.setText("加载中")
        self.comboBox.setPlaceholderText("加载中")
        self.button = PrimaryPushButton("搜索", self, FIF.SEARCH)
        self.button.clicked.connect(self.btn2_1)
        self.card1 = self.modDownload.addExampleCard(
            title="搜索模组",
            widget=[self.lineEdit, self.comboBox, self.button],
        )

        self.lineEdit.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.button.setEnabled(False)
        # 窗口设置
        self.addSubInterface(self.modDownload, "modDownload", "模组下载")
        self.addSubInterface(self.modUpdate, "modUpdate", "模组更新")

        self.vBoxLayout.addWidget(self.pivot, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 0)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.modDownload)
        self.pivot.setMaximumSize(300, 33)
        self.pivot.setCurrentItem(self.modDownload.objectName())
        self.num = 0

    def addModCard(self, title, loader, version, download, time, description, icon="./img/zb.png", data=None):
        self.modCard = modCard(QIcon(icon), title, f"{description}\n加载器 {loader} 支持的游戏版本 {version}", f"下载量 {download}\n最近更新 {time}", data, self.modDownload)
        self.modDownload.vBoxLayout.addWidget(self.modCard, 0, Qt.AlignTop)

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

    # 打开时后台加载版本列表
    def btn1_2(self, msg):
        self.comboBox.addItems(msg[0])
        self.comboBox.setText("全部")
        self.comboBox.setPlaceholderText("游戏版本")
        self.lineEdit.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.button.setEnabled(True)

    # 搜索按钮事件
    def btn2_1(self):
        for i in range(self.modDownload.vBoxLayout.count())[1:]:
            self.modDownload.vBoxLayout.itemAt(i).widget().deleteLater()
        self.lineEdit.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.button.setEnabled(False)
        mod_name = self.lineEdit.text()
        mod_version = self.comboBox.text()
        if mod_version == "全部":
            mod_version = None
        self.thread = newThread(11, data=[mod_name, mod_version])
        self.thread.signal2.connect(self.btn2_2)
        self.thread.start()

    def btn2_2(self, msg):
        if msg:
            self.infoBar1 = InfoBar(
                icon=InfoBarIcon.SUCCESS,
                title="提示",
                content=f"搜索模组{self.lineEdit.text()}成功！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2500,
                parent=self
            )
            self.infoBar1.show()
        else:
            self.infoBar1 = InfoBar(
                icon=InfoBarIcon.ERROR,
                title="提示",
                content=f"名称{self.lineEdit.text()}无搜索结果！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2500,
                parent=self
            )
            self.infoBar1.show()
        for i in msg:
            self.addModCard(i["名称"], "/".join(i["加载器"]), i["适配版本范围"], i["下载次数"], datetime.datetime.strptime(i["更新日期"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d"), i["介绍"], join(user_path, "zb", "cache", i["名称"] + ".png"), data=i)
            self.num += 1
        self.lineEdit.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.button.setEnabled(True)
