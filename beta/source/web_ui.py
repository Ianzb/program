from .web_api import *
from .manager_ui import *

mod_page_list = []


class SmallModInfoCard(SmallInfoCard):
    """
    资源信息小卡片
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self, data: dict, source: str, parent: QWidget = None):
        """
        @param data: 资源数据
        @param source: 资源来源
        """
        super().__init__(parent)

        self.data = data
        self.source = source

        self.mainButton.deleteLater()

        if isinstance(self.data, dict):
            self.loadInfo()
        else:
            self.setTitle("信息正在加载中...")
            self.thread1 = MyThread("获得单独模组信息", [self.data, self.source])
            self.thread1.signalDict.connect(self.thread1_1)
            self.thread1.signalBool.connect(self.thread1_2)
            self.thread1.start()

    def thread1_1(self, msg):
        self.data = msg
        self.loadInfo()

    def thread1_2(self, msg):
        if not msg:
            self.setTitle("信息加载失败！")

    def loadInfo(self):
        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data['名称'])}.png", self.data["图标"])
        self.setTitle(f"{self.data['名称']}")
        self.setInfo(self.data["介绍"], 0)
        self.setInfo(f"下载量：{f.numberAddUnit(self.data['下载量'])}", 1)
        self.setInfo(f"游戏版本：{self.data['游戏版本'][0] + '-' + self.data['游戏版本'][-1] if len(self.data['游戏版本']) > 1 else self.data['游戏版本'][0] if len(self.data['游戏版本']) > 0 else '无'}", 2)
        self.setInfo(f"更新日期：{self.data['更新日期']}", 3)

    def mousePressEvent(self, event):
        if isinstance(self.data, dict):
            self.signalDict.emit(self.data)


class BigModInfoCard(BigInfoCard):
    """
    资源信息大卡片
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self, data: dict, parent: QWidget = None, widgets=[], version=None, loader=None):
        """
        @param data: 资源数据
        """
        super().__init__(parent)
        self.data = data
        self.version = version
        self.loader = loader

        global mod_page_list
        mod_page_list.append(data)

        self.loadingCard = widgets[0]
        self.vBoxLayout = widgets[1]

        self.mainButton.deleteLater()

        self.loadingCard.setText("加载中")
        self.loadingCard.show()

        self.titleLabel.setMaximumWidth(500)
        self.titleLabel.setMinimumWidth(400)

        self.setTitle(data["名称"])
        self.setInfo(data["介绍"])
        self.setImg(f"{data['来源']}/{f.removeIllegalPath(data['名称'])}.png", data["图标"])
        try:
            self.addData("作者", data["作者"])
        except:
            pass
        self.addData("下载量", f.numberAddUnit(data["下载量"]))
        self.addData("发布日期", data["发布日期"])
        self.addData("更新日期", data["更新日期"])

        self.cardGroup = CardGroup("文件", self)
        self.vBoxLayout.insertWidget(3, self.cardGroup)
        self.cardGroup.hide()

        self.thread1 = MyThread("获得资源信息", [data["id"], data["来源"]])
        self.thread1.signalDict.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

    def thread1_1(self, msg):
        self.setTitle(msg["名称"])
        self.setInfo(msg["介绍"])
        self.setImg(f"{msg['来源']}/{f.removeIllegalPath(msg['名称'])}.png", msg["图标"])
        self.addUrl(msg["来源"], msg["网站链接"], FIF.LINK)
        if msg["源代码链接"]:
            self.addUrl("源代码", msg["源代码链接"], FIF.GITHUB)
        self.addUrl("MC百科", f"https://search.mcmod.cn/s?key={msg['名称']}", FIF.SEARCH)

        for i in msg["加载器"]:
            self.addTag(i)

        self.label1 = StrongBodyLabel("版本", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("版本")
        self.comboBox1.addItems(["全部"] + msg["游戏版本"][::-1])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择资源版本")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.setMaxVisibleItems(15)
        if self.version in ["全部"] + msg["游戏版本"][::-1]:
            self.comboBox1.setCurrentText(self.version)
        self.comboBox1.currentIndexChanged.connect(self.getFileInfo)

        self.label2 = StrongBodyLabel("加载器", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("加载器版本")
        self.comboBox2.addItems(["全部"] + msg["加载器"])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择加载器版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        if self.loader in ["全部"] + msg["加载器"]:
            self.comboBox2.setCurrentText(self.loader)
        self.comboBox2.currentIndexChanged.connect(self.getFileInfo)

        self.card1 = GrayCard("筛选")
        self.card1.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card1.addWidget(self.comboBox1)
        self.card1.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card1.addWidget(self.comboBox2)

        self.vBoxLayout.insertWidget(1, self.card1)

        self.getFileInfo()

    def getFileInfo(self):
        self.cardGroup.hide()
        self.loadingCard.setText("加载中")
        self.loadingCard.show()
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)

        self.thread2 = MyThread("获得资源文件", [self.data["id"], self.comboBox1.currentText(), self.comboBox2.currentText(), self.data["来源"]])
        self.thread2.signalDict.connect(self.thread2_1)
        self.thread2.signalBool.connect(self.thread2_2)
        self.thread2.start()

    def thread1_2(self, msg):
        if not msg:
            self.loadingCard.setText("加载失败")

    def backButtonClicked(self):
        global mod_page_list
        mod_page_list = mod_page_list[:-1]
        if len(mod_page_list) > 0:
            self.signalDict.emit(mod_page_list[-1])
            mod_page_list = mod_page_list[:-1]
        else:
            self.signalBool.emit(True)
        self.hidePage()

    def hidePage(self, msg=None):
        """
        隐藏页面
        """
        try:
            self.card1.deleteLater()
        except:
            pass
        self.cardGroup.deleteLater()
        self.deleteLater()

    def thread2_1(self, msg):
        self.cardGroup.deleteLater()
        self.cardGroup = CardGroup("文件", self)
        if len(msg.keys()) == 0:
            self.cardGroup.setTitle("无筛选结果")
        self.vBoxLayout.insertWidget(3, self.cardGroup)

        dependencies = []
        for k in msg.keys():
            for i in msg[k]:
                dependencies += i["前置"]
        dependencies = list(set(dependencies))
        if len(dependencies) > 0:
            self.cardGroup.addWidget(StrongBodyLabel(f"前置（{len(dependencies)}个）", self))
        if len(dependencies) <= 10:
            for i in dependencies:
                self.infoCard = SmallModInfoCard(i, self.data["来源"], self)
                self.infoCard.signalDict.connect(self.signalDict.emit)
                self.cardGroup.addWidget(self.infoCard)
        else:
            self.cardGroup.addWidget(StrongBodyLabel(f"前置数量过多，无法展示，请前往资源网页查看！", self))
        i = 0
        for k in f.sortVersion(msg.keys(), True):
            if k == self.comboBox1.currentText() or self.comboBox1.currentText() == "全部":
                self.cardGroup.addWidget(StrongBodyLabel(k, self))
                for v in msg[k]:
                    self.cardGroup.addWidget(SmallFileInfoCard(v))
                    if i > 50:
                        break
                    i += 1
        self.cardGroup.show()
        self.loadingCard.hide()
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)

    def thread2_2(self, msg):
        if not msg:
            self.loadingCard.setText("加载失败")
            self.loadingCard.show()


class SmallFileInfoCard(SmallInfoCard):
    """
    文件信息小卡片
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self, data: dict, parent: QWidget = None):
        """
        @param data: 资源数据
        """
        super().__init__(parent)
        self.data = data

        self.image.deleteLater()

        self.setTitle(f"{data['名称']}{' · ' if data['版本类型'] else ''}{data['版本类型']}")
        self.setInfo("、".join(data["加载器"]) + (" | " if len(data["加载器"]) > 0 else "") + ("、".join(data["游戏版本"]) if len(data["游戏版本"]) <= 10 else f"支持{data['游戏版本'][0]}-{data['游戏版本'][-1]}共{len(data['游戏版本'])}个版本"), 0)
        self.setInfo(f"文件大小：{f.fileSizeAddUnit(data['文件大小'])}", 1)
        self.setInfo(f"下载量：{f.numberAddUnit(data['下载量'])}", 2)
        self.setInfo(f"更新日期：{data['更新日期']}", 3)

        self.mainButton.setText("下载")
        self.mainButton.setIcon(FIF.DOWNLOAD)

        if not self.data["下载链接"]:
            self.mainButton.setEnabled(False)

    def mainButtonClicked(self):
        if not self.data["下载链接"]:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "该文件暂无下载链接，请更换版本或更换下载源重试！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            return
        open = setting.read("minecraftJavaPath")
        if self.parent().parent().parent().parent().comboBox3.currentText() in FILE_PATH.keys():
            open = f.pathJoin(open, FILE_PATH[self.parent().parent().parent().parent().comboBox3.currentText()])
        path = QFileDialog.getExistingDirectory(self, "选择下载目录", open)
        if not path:
            return
        path = f.pathJoin(path, self.data["文件名称"])
        UpdateModWidget(self.data["下载链接"], path, parent=self.parent().parent().parent())


class SearchTab(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源下载")
        self.onShowPage = None
        self.isInit = False

        self.vBoxLayout.setSpacing(8)

        self.lineEdit = AcrylicSearchLineEdit(self)
        self.lineEdit.setPlaceholderText("资源名称")
        self.lineEdit.setToolTip("搜索资源，数据来源：\n CurseForge\n Modrinth")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.returnPressed.connect(self.lineEditReturnPressed)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)
        self.lineEdit.searchButton.setEnabled(True)

        self.label1 = StrongBodyLabel("数据源", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("下载应用来源")
        self.comboBox1.addItems(["CurseForge", "Modrinth"])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择下载应用来源")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.currentIndexChanged.connect(self.searchButtonClicked)

        self.label2 = StrongBodyLabel("版本", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("版本")
        self.comboBox2.addItems(["全部"])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择资源版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox2, 1000))
        self.comboBox2.setMaxVisibleItems(15)
        self.comboBox2.currentIndexChanged.connect(self.searchButtonClicked)

        self.label3 = StrongBodyLabel("类型", self)

        self.comboBox3 = AcrylicComboBox(self)
        self.comboBox3.setPlaceholderText("类型")
        self.comboBox3.addItems(list(CURSEFORGE_TYPE.keys()))
        self.comboBox3.setCurrentIndex(0)
        self.comboBox3.setToolTip("选择资源类型")
        self.comboBox3.installEventFilter(ToolTipFilter(self.comboBox3, 1000))
        self.comboBox3.setMaxVisibleItems(15)
        self.comboBox3.currentIndexChanged.connect(self.searchButtonClicked)

        self.card1 = GrayCard("搜索")
        self.card1.addWidget(self.lineEdit)

        self.card2 = GrayCard("筛选")
        self.card2.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card2.addWidget(self.comboBox1)
        self.card2.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card2.addWidget(self.comboBox2)
        self.card2.addWidget(self.label3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card2.addWidget(self.comboBox3)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignmentFlag.AlignCenter)

        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

    def showEvent(self, QShowEvent):
        if not self.isInit:
            self.isInit = True
            self.thread1 = MyThread("获得游戏版本列表")
            self.thread1.signalList.connect(self.thread1_1)
            self.thread1.signalBool.connect(self.thread1_2)
            self.thread1.start()

            self.loadingCard.setText("正在获得游戏版本列表")
            self.loadingCard.show()
            self.lineEdit.setEnabled(False)
            self.comboBox1.setEnabled(False)
            self.comboBox2.setEnabled(False)
            self.comboBox3.setEnabled(False)

    def lineEditReturnPressed(self):
        self.lineEdit.searchButton.click()

    def searchButtonClicked(self):
        if self.comboBox1.currentText() == "Modrinth":
            if self.comboBox3.currentText() not in MODRINTH_TYPE.keys():
                self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"{self.comboBox1.currentText()}不支持搜索{self.comboBox3.currentText()}类资源", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
                self.infoBar.show()
                return
        self.cardGroup1.deleteLater()
        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.cardGroup1.setTitleEnabled(False)
        self.lineEdit.setEnabled(False)
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)
        self.comboBox3.setEnabled(False)

        self.loadingCard.setText("搜索中...")
        self.loadingCard.show()

        self.thread2 = MyThread("搜索资源", [self.lineEdit.text(), self.comboBox1.currentText(), self.comboBox2.currentText(), self.comboBox3.currentText()])
        self.thread2.signalList.connect(self.thread2_1)
        self.thread2.signalBool.connect(self.thread2_2)
        self.thread2.start()

    def thread1_1(self, msg):
        self.loadingCard.hide()
        self.comboBox2.addItems(msg)
        self.lineEdit.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)
        self.lineEdit.searchButton.click()

    def thread1_2(self, msg):
        if not msg:
            self.comboBox2.addItems(RELEASE_VERSIONS)

    def thread2_1(self, msg):
        self.loadingCard.hide()
        for i in msg:
            self.infoCard = SmallModInfoCard(i, self.comboBox1.currentText(), self)
            self.infoCard.signalDict.connect(self.showModPage)
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignmentFlag.AlignTop)
            self.cardGroup1.addWidget(self.infoCard)
        if msg:
            self.cardGroup1.setTitle(f"搜索结果（{len(msg)}个）")
        else:
            self.cardGroup1.setTitle(f"无搜索结果")
        self.cardGroup1.setTitleEnabled(True)

        self.lineEdit.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)

    def thread2_2(self, msg):
        if not msg:
            self.loadingCard.setText("搜索失败！")
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox1.setEnabled(True)
            self.comboBox2.setEnabled(True)
            self.comboBox3.setEnabled(True)

    def showModPage(self, msg, version=None, loader=None):
        """
        展示资源页面
        """
        try:
            self.onShowPage.hidePage()
        except:
            pass
        self.setPage(1, msg, version, loader)

    def hideModPage(self, msg):
        """
        退出资源页面
        """
        try:
            self.onShowPage.hidePage()
        except:
            pass
        if msg:
            self.setPage(0, msg)

    def setPage(self, num: int = 0, msg=None, version=None, loader=None):
        if num == 0:
            self.loadingCard.hide()
            self.vBoxLayout.removeWidget(self.bigModInfoCard)
            self.cardGroup1.show()
            self.card1.show()
            self.card2.show()
        elif num == 1:
            self.cardGroup1.hide()
            self.card1.hide()
            self.card2.hide()

            self.bigModInfoCard = BigModInfoCard(msg, self, [self.loadingCard, self.vBoxLayout], version, loader)
            self.bigModInfoCard.signalBool.connect(self.hideModPage)
            self.bigModInfoCard.signalDict.connect(self.showModPage)
            self.onShowPage = self.bigModInfoCard
            self.vBoxLayout.insertWidget(0, self.bigModInfoCard)


class AddonPage(BasicTabPage):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.GAME)
        self.setObjectName("资源下载")

        self.addPage(SearchTab(self))
        self.addPage(FileTab(self))
