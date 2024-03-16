import sys, os

sys.path = [os.path.dirname(sys.argv[0])] + sys.path
from source.custom import *

os.chdir(os.path.dirname(__file__))

try:
    from beta.source.custom import *
except:
    pass
from .api import *

setting.add("minecraftJavaPath", f.pathJoin(program.USER_PATH, r"AppData\Roaming\.minecraft"))


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

    def run(self):
        if self.mode == "搜索资源":
            try:
                data = searchMod(self.data[0], self.data[1], self.data[2], type=self.data[3])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "获得游戏版本列表":
            try:
                self.signalList.emit(getVersionList())
            except:
                self.signalBool.emit(False)
        if self.mode == "获得资源信息":
            try:
                data = getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "获得资源文件":
            try:
                data = getModFile(self.data[0], self.data[1], self.data[2], self.data[3])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "获得单独模组信息":
            try:
                data = getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "获得文件信息":
            try:
                try:
                    data1 = getInfoFromHash(self.data)
                except:
                    data1 = []
                try:
                    data2 = getInfoFromHash(self.data, source="Modrinth")
                except:
                    data2 = []
                if not data1 and not data2:
                    self.signalBool.emit(False)
                self.signalList.emit(data1 + data2)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "从文件获得模组信息":
            try:
                list = [i["模组id"] for i in self.data]
                try:
                    data2 = getModsInfo([i for i in list if isinstance(i, int)])
                except:
                    data2 = []
                try:
                    data1 = getModsInfo([i for i in list if isinstance(i, str)], source="Modrinth")
                except:
                    data1 = []
                if not data1 and not data2:
                    self.signalBool.emit(False)
                self.signalList.emit(data1 + data2)
            except Exception as ex:
                self.signalBool.emit(False)


class MinecraftJavaSettingCard(SettingCard):
    """
    整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "Java版目录", "默认选择.minecraft文件夹，若开启版本隔离请选择版本文件夹", parent)
        self.button1 = PushButton("选择", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("设置Java版目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择要添加的Minecraft Java版目录", setting.read("minecraftJavaPath"))
        if f.existPath(get):
            setting.save("minecraftJavaPath", get)


class ModSettingMessageBox(MessageBoxBase):
    """
    可编辑整理目录的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("插件 MC资源管理器 设置", self)

        self.scrollArea = BetterScrollArea(self)
        self.scrollArea.vBoxLayout.setContentsMargins(8, 8, 8, 8)

        self.cardGroup1 = CardGroup("路径", self)

        self.minecraftJavaSettingCard = MinecraftJavaSettingCard(self)

        self.cardGroup1.addWidget(self.minecraftJavaSettingCard)

        self.scrollArea.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.scrollArea)

        self.yesButton.setText("关闭")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.deleteLater()

        self.widget.setMinimumSize(600, 400)

    def yesButtonClicked(self):
        self.accept()
        self.accepted.emit()


class CopyButton(ToolButton):
    """
    复制按钮
    """

    def __init__(self, link, parent=None):
        super().__init__(parent)
        self.link = link

        self.setIcon(FIF.COPY)

        self.setToolTip(link if link else "")
        self.installEventFilter(ToolTipFilter(self, 1000))
        self.clicked.connect(self.copyButtonClicked)
        if not link:
            self.setEnabled(False)

    def copyButtonClicked(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.link)


class SearchButton(ToolButton):
    """
    搜索按钮
    """

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        self.setIcon(FIF.SEARCH)

        self.setToolTip(f"在{data["来源"]}上搜索组件")
        self.installEventFilter(ToolTipFilter(self, 1000))
        self.clicked.connect(self.searchButtonClicked)

    def searchButtonClicked(self):
        widget = self.parent().parent().parent().parent().parent().parent().widget(1)
        widget.showModPage(self.data, self.parent().parent().parent().parent().parent().comboBox2.currentText(), self.parent().parent().parent().parent().parent().comboBox3.currentText())
        self.parent().parent().parent().parent().parent().parent().parent().pivot.setCurrentItem("资源下载")
        self.parent().parent().parent().parent().parent().parent().setCurrentWidget(widget)


class ModFileInfoCard(SmallInfoCard):
    """
    文件信息小卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, path: str, parent: QWidget = None):
        """
        @param path: 资源数据
        """
        super().__init__(parent)
        self.path = path
        self.name = f.splitPath(self.path)

        self.data = {"CurseForge": {},
                     "Modrinth": {}}
        self.mod = {"CurseForge": {},
                    "Modrinth": {}}

        self.image.hide()
        self.hBoxLayout.setSpacing(8)

        self.setTitle(self.name)
        self.setInfo(f"文件大小：{f.fileSizeAddUnit(f.getSize(self.path))}", 1)

        self.mainButton.deleteLater()
        self.openButton = ToolButton(FIF.FOLDER, self)
        self.openButton.clicked.connect(self.openButtonClicked)
        self.openButton.setToolTip("在文件夹中展示文件")
        self.openButton.installEventFilter(ToolTipFilter(self.openButton, 1000))
        self.hBoxLayout.insertWidget(5, self.openButton, alignment=Qt.AlignRight)

        self.parent().thread1.signalList.connect(self.thread1_1)
        self.parent().thread1.signalBool.connect(self.thread1_2)
        self.parent().thread2.signalList.connect(self.thread2_1)

    def openButtonClicked(self):
        f.showFile(self.path)

    def thread1_1(self, msg):
        list1 = [i for i in msg if i["源文件名称"] == self.name]
        if list1:
            for data in list1:
                self.data[data["来源"]] = data
                if {} in self.data.values():
                    self.setInfo("、".join(data["加载器"]) + (" | " if len(data["加载器"]) > 0 else "") + ("、".join(data["游戏版本"]) if len(data["游戏版本"]) <= 10 else f"支持{data["游戏版本"][0]}-{data["游戏版本"][-1]}共{len(data["游戏版本"])}个版本"), 0)
                    self.setInfo(f"文件大小：{f.fileSizeAddUnit(data["文件大小"])}", 1)
                    self.setInfo(f"下载量：{f.numberAddUnit(data["下载量"])}", 2)
                    self.setInfo(f"更新日期：{data["更新日期"]}", 3)
                self.hBoxLayout.insertWidget(4, CopyButton(data["下载链接"]), alignment=Qt.AlignRight)
        else:
            self.setInfo("文件无在线数据！", 0)

    def thread1_2(self, msg):
        if not msg:
            self.setInfo("在线信息加载失败！", 0)

    def thread2_1(self, msg):
        mod_id = [i["模组id"] for i in self.data.values() if i]
        list1 = [i for i in msg if i["id"] in mod_id]
        if list1:
            self.image.show()
            self.setImg(f"{list1[0]["来源"]}/{f.removeIllegalPath(list1[0]["名称"])}.png", list1[0]["图标"])
            for data in list1:
                self.mod[data["来源"]] = data
                self.hBoxLayout.insertWidget(4, SearchButton(data, self), alignment=Qt.AlignRight)


class FileManageTab(BasicTab):
    """
    插件第二页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源管理")

        self.vBoxLayout.setSpacing(8)

        self.label1 = StrongBodyLabel("类型", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("Minecraft路径")
        self.comboBox1.addItems(["模组", "光影", "资源包"])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择资源类型")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.currentIndexChanged.connect(self.loadModList)

        self.button1 = PushButton("打开目录", self, FIF.FOLDER)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("打开当前资源目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.settingButton = ToolButton(FIF.SETTING, self)
        self.settingButton.clicked.connect(self.settingButtonClicked)

        self.reloadButton = ToolButton(FIF.SYNC, self)
        self.reloadButton.clicked.connect(self.loadModList)
        self.reloadButton.setToolTip("刷新")
        self.reloadButton.installEventFilter(ToolTipFilter(self.reloadButton, 1000))

        self.label2 = StrongBodyLabel("版本", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("版本")
        self.comboBox2.addItems(["全部"] + RELEASE_VERSIONS)
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择资源版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox2, 1000))
        self.comboBox2.setMaxVisibleItems(15)

        self.label3 = StrongBodyLabel("加载器", self)

        self.comboBox3 = AcrylicComboBox(self)
        self.comboBox3.setPlaceholderText("加载器版本")
        self.comboBox3.addItems(["全部"] + sorted(list(LOADER_TYPE.keys())))
        self.comboBox3.setCurrentIndex(0)
        self.comboBox3.setToolTip("选择加载器版本")
        self.comboBox3.installEventFilter(ToolTipFilter(self.comboBox1, 1000))

        self.card1 = GrayCard("资源管理")
        self.card1.addWidget(self.label1, alignment=Qt.AlignCenter)
        self.card1.addWidget(self.comboBox1)
        self.card1.addWidget(self.label2, alignment=Qt.AlignCenter)
        self.card1.addWidget(self.comboBox2)
        self.card1.addWidget(self.label3, alignment=Qt.AlignCenter)
        self.card1.addWidget(self.comboBox3)

        self.card1.addWidget(self.button1)
        self.card1.addWidget(self.settingButton)
        self.card1.addWidget(self.reloadButton)

        self.vBoxLayout.addWidget(self.card1)

        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.loadModList()

    def button1Clicked(self):
        f.showFile(f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1.currentText()]))

    def settingButtonClicked(self):
        self.modSettingMessageBox = ModSettingMessageBox(self.parent().parent().parent().parent().parent())
        self.modSettingMessageBox.show()

    def loadModList(self):
        if not f.existPath(f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1.currentText()])):
            return
        self.comboBox2.setEnabled(False)
        self.comboBox3.setEnabled(False)

        self.cardGroup1.deleteLater()
        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        data = [i for i in f.walkFile(f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1.currentText()]), 1) if f.splitPath(i, 2) in FILE_SUFFIX[self.comboBox1.currentText()]]
        self.cardGroup1.setTitle(f"发现{self.comboBox1.currentText()}{len(data)}个")
        self.thread1 = MyThread("获得文件信息", f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1.currentText()]))
        self.thread2 = MyThread("从文件获得模组信息")
        self.thread1.signalList.connect(self.thread1_1)
        self.thread1.start()
        for i in data:
            self.infoCard = ModFileInfoCard(i, self)
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignTop)
            self.cardGroup1.addWidget(self.infoCard)

    def thread1_1(self, msg):
        self.thread2.signalList.connect(self.thread2_1)
        self.thread2.data = msg
        self.thread2.start()

        loader = []
        version = []
        for i in msg:
            loader += i["加载器"]
            version += i["游戏版本"]
        from collections import Counter

        if loader:
            loader = Counter(loader)
            loader = dict([val, key] for key, val in loader.items())
            loader = loader[sorted(loader.keys())[-1]]
            self.comboBox3.setCurrentText(loader)
        if version:
            version = Counter(version)
            version = dict([val, key] for key, val in version.items())
            version = version[sorted(version.keys())[-1]]
            self.comboBox2.setCurrentText(version)

    def thread2_1(self, msg):
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)
