from gallery_interface import *
from mod_downloader import *


class minecraftInterface(GalleryInterface):

    def __init__(self, parent=None):
        super().__init__(
            title="",
            subtitle="",
            parent=parent
        )
        self.setObjectName("Minecraft")
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.modDownload = GalleryInterface("", "模组下载", parent=self)
        self.modUpdate = GalleryInterface("", "模组更新", parent=self)
        self.modDownload.toolBar.setParent(None)
        self.modUpdate.toolBar.setParent(None)
        self.modDownload.setViewportMargins(0, 0, 0, 0)
        self.modDownload.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.modUpdate.setViewportMargins(0, 0, 0, 0)
        self.modUpdate.vBoxLayout.setContentsMargins(0, 20, 0, 0)

        # 上方请勿修改
        self.lineEdit = LineEdit(self)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setPlaceholderText("输入模组名称")
        self.lineEdit.setFixedSize(300, 33)
        self.lineEdit.setMaxLength(50)
        self.thread = newThread(10)
        self.thread.signal2.connect(self.btn1_2)
        self.thread.start()
        self.comboBox = EditableComboBox()
        self.comboBox.setEnabled(False)
        self.comboBox.setText("加载中")
        self.comboBox.setPlaceholderText("加载中")
        self.button = PrimaryPushButton("搜索", self, FIF.SEARCH)
        self.button.clicked.connect(self.btn2_1)
        self.card1 = self.modDownload.addExampleCard(
            title="搜索模组",
            widget=[self.lineEdit, self.comboBox, self.button],
        )
        self.aboutCard = modInfoCard(FIF.PHOTO, "JEI物品管理器", "介绍\nForge/Fabric 1.18-1.20.2", "257000000", self)
        self.aboutCard.setParent(self.modDownload)

        self.modDownload.vBoxLayout.addWidget(self.aboutCard, 0, Qt.AlignTop)
        # 下方请勿修改
        self.addSubInterface(self.modDownload, "modDownload", "模组下载")
        self.addSubInterface(self.modUpdate, "modUpdate", "模组更新")

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 0)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.modDownload)
        self.pivot.setCurrentItem(self.modDownload.objectName())

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
        self.comboBox.setEnabled(True)

    # 搜索按钮事件
    def btn2_1(self):
        print(self.comboBox.text(), self.lineEdit.text())
