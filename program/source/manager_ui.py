from .mc_api import *


class MyThread(QThread, SignalBase):
    """
    多线程模块
    """

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data

    def run(self):
        logging.info(f"MC资源管理器插件 {self.mode} 线程开始")

        if self.mode == "搜索资源":
            try:
                data = searchMod(self.data[0], self.data[1], self.data[2], type=self.data[3])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得游戏版本列表":
            try:
                self.signalList.emit(getVersionList())
            except:
                self.signalBool.emit(False)
        elif self.mode == "获得资源信息":
            try:
                data = getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得资源文件":
            try:
                data = getModFile(self.data[0], self.data[1], self.data[2], self.data[3])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得单独模组信息":
            try:
                data = getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        elif self.mode == "获得文件信息":
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
        elif self.mode == "从文件获得模组信息":
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
        elif self.mode == "获得模组最新版本":
            try:
                if self.data[3] == "Modrinth":
                    self.signalInt.emit(0)
                    response = getInfoFromHash(self.data[0], self.data[3])
                    self.signalInt.emit(50)
                    data = getNewestFromHash(self.data[0], self.data[1], self.data[2], self.data[3])
                elif self.data[3] == "CurseForge":
                    self.signalInt.emit(0)
                    response = getInfoFromHash(self.data[0], self.data[3])
                    data = []
                    self.signalInt.emit(int(100 / (len(response) + 1)))
                    for i in range(len(response)):
                        try:
                            data1 = getModFile(response[i]["模组id"], self.data[1], self.data[2], self.data[3])
                            data.append(data1[self.data[1]][0])
                        except:
                            pass
                        self.signalInt.emit(int(100 * (i + 2) / (len(response) + 1)))
                self.signalInt.emit(100)
                self.signalDict.emit({"old": response, "new": data})
            except:
                self.signalBool.emit(False)
        logging.info(f"MC资源管理器插件 {self.mode} 线程结束")


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

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择要添加的Minecraft Java版目录", setting.read("minecraftJavaPath"))
        if isMinecraftPath(get):
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

        self.scrollArea.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignmentFlag.AlignTop)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.scrollArea)

        self.yesButton.setText("关闭")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.deleteLater()

        self.widget.setMinimumSize(600, 400)

    def yesButtonClicked(self):
        self.accept()
        self.accepted.emit()





class SearchButton(ToolButton):
    """
    搜索按钮
    """

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        self.setIcon(FIF.SEARCH)

        self.setToolTip(f"在{data['来源']}上搜索组件")
        self.installEventFilter(ToolTipFilter(self, 1000))
        self.clicked.connect(self.searchButtonClicked)

    def searchButtonClicked(self):
        widget = self.parent().parent().parent().parent().parent().parent().parent().stackedWidget.widget(0)
        widget.showModPage(self.data, self.parent().parent().parent().parent().parent().comboBox2_2.currentText(), self.parent().parent().parent().parent().parent().comboBox2_3.currentText())
        self.parent().parent().parent().parent().parent().parent().parent().pivot.setCurrentItem("资源下载")
        self.parent().parent().parent().parent().parent().parent().parent().stackedWidget.setCurrentWidget(widget)
        widget.comboBox3.currentIndexChanged.disconnect(widget.searchButtonClicked)
        widget.comboBox3.setCurrentText(self.parent().parent().parent().parent().parent().comboBox1_1.currentText())
        widget.comboBox3.currentIndexChanged.connect(widget.searchButtonClicked)


class UpdateModWidget(QWidget):
    """
    下载文件ui接口
    """

    def __init__(self, link: str, name: str, old: str = "", parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.name = name
        self.link = link
        self.old = old

        self.thread1 = CustomThread("下载文件", (link, name))
        self.thread1.signalInt.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

        self.progressBar = ProgressBar(self.parent)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载文件 {f.splitPath(name)}", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()
        self.infoBar.closeButton.clicked.connect(self.thread1.cancel)

    def thread1_1(self, msg):
        try:
            self.infoBar.contentLabel.setText(f"正在下载文件 {f.splitPath(self.name)}")
            self.progressBar.setValue(msg)
        except:
            return
        if msg == 100:
            self.infoBar.contentLabel.setText(f"{self.name} 下载成功")
            self.infoBar.closeButton.click()

            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载", f"资源 {f.splitPath(self.name)} 下载成功", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
            self.button1 = PushButton("打开目录", self.parent, FIF.FOLDER)
            self.button1.clicked.connect(self.button1Clicked)
            self.infoBar.addWidget(self.button1)

            if self.old:
                f.moveFile(self.old, self.old + ".old")

            self.progressBar.setValue(0)
            self.progressBar.deleteLater()

    def thread1_2(self, msg):
        if not msg:
            try:
                self.infoBar.closeButton.click()
            except:
                self.thread1.cancel()
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", "下载失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()

    def button1Clicked(self):
        if f.existPath(self.name):
            f.showFile(self.name)
        else:
            f.showFile(f.splitPath(self.name, 3))

        self.infoBar.closeButton.click()


class ModUpdateMessageBox(MessageBoxBase):
    """
    更新资源的弹出框
    """

    def __init__(self, title: str, data: list, path: str, parent=None):
        super().__init__(parent.parent().parent().parent().parent().parent())
        self.data = data
        self.path = path
        self.parent = parent

        self.titleLabel = SubtitleLabel(title, self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(3)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["文件名", "本地版本号", "在线版本号"])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.tableView, 0, Qt.AlignmentFlag.AlignTop)

        self.yesButton.setText("更新")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(690)

        self.setMinimumWidth(690)

        import string

        abc = string.ascii_lowercase + string.ascii_uppercase + "-_. \n"

        self.tableView.setRowCount(len(data))
        for i in range(len(data)):
            self.tableView.setItem(i, 0, QTableWidgetItem(data[i][0]["源文件名称"]))
            self.tableView.setItem(i, 1, QTableWidgetItem(data[i][0]["文件名称"].strip(abc)))
            self.tableView.setItem(i, 2, QTableWidgetItem(data[i][1]["文件名称"].strip(abc)))
            if not data[i][1]["下载链接"]:
                self.tableView.hideRow(i)

    def yesButtonClicked(self):
        for i in self.data:
            if i[1]["下载链接"]:
                UpdateModWidget(i[1]["下载链接"], f.pathJoin(self.path, i[1]["文件名称"]), f.pathJoin(self.path, i[0]["源文件名称"]), self.parent)


class ModFileInfoCard(SmallInfoCard, SignalBase):
    """
    文件信息小卡片
    """

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
        self.hBoxLayout.insertWidget(5, self.openButton, alignment=Qt.AlignmentFlag.AlignRight)

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
                    self.setInfo(f"文件大小：{f.fileSizeAddUnit(data['文件大小'])}", 1)
                    self.setInfo(f"下载量：{f.numberAddUnit(data['下载量'])}", 2)
                    self.setInfo(f"更新日期：{data['更新日期']}", 3)
                self.hBoxLayout.insertWidget(4, CopyTextButton(data["下载链接"]), alignment=Qt.AlignmentFlag.AlignRight)
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
            self.setImg(f"{list1[0]['来源']}/{f.removeIllegalPath(list1[0]['名称'])}.png", list1[0]["图标"])
            self.setInfo(list1[0]["介绍"], 0)
            for data in list1:
                self.mod[data["来源"]] = data
                self.hBoxLayout.insertWidget(4, SearchButton(data, self), alignment=Qt.AlignmentFlag.AlignRight)


class FileTab(BasicTab):
    """
    插件第二页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源管理")

        self.vBoxLayout.setSpacing(8)

        self.label1_1 = StrongBodyLabel("类型", self)

        self.comboBox1_1 = AcrylicComboBox(self)
        self.comboBox1_1.setPlaceholderText("Minecraft路径")
        self.comboBox1_1.addItems(["模组", "光影", "资源包"])
        self.comboBox1_1.setCurrentIndex(0)
        self.comboBox1_1.setToolTip("选择资源类型")
        self.comboBox1_1.installEventFilter(ToolTipFilter(self.comboBox1_1, 1000))
        self.comboBox1_1.currentIndexChanged.connect(self.loadModList)

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

        self.updateButton = PushButton("立刻更新", self, FIF.UPDATE)
        self.updateButton.clicked.connect(self.updateButtonClicked)
        self.updateButton.setToolTip("更新资源")
        self.updateButton.installEventFilter(ToolTipFilter(self.updateButton, 1000))

        self.label2_1 = StrongBodyLabel("更新方式", self)

        self.comboBox2_1 = AcrylicComboBox(self)
        self.comboBox2_1.setPlaceholderText("更新方式")
        self.comboBox2_1.addItems(["CurseForge", "Modrinth"])
        self.comboBox2_1.setCurrentIndex(0)
        self.comboBox2_1.setToolTip("选择更新方式")
        self.comboBox2_1.installEventFilter(ToolTipFilter(self.comboBox2_1, 1000))
        self.comboBox2_1.setMinimumWidth(0)

        self.label2_2 = StrongBodyLabel("目标版本", self)

        self.comboBox2_2 = AcrylicComboBox(self)
        self.comboBox2_2.setPlaceholderText("目标版本")
        self.comboBox2_2.addItems(RELEASE_VERSIONS)
        self.comboBox2_2.setCurrentIndex(0)
        self.comboBox2_2.setToolTip("选择目标版本")
        self.comboBox2_2.installEventFilter(ToolTipFilter(self.comboBox2_2, 1000))
        self.comboBox2_2.setMaxVisibleItems(15)
        self.comboBox2_2.setMinimumWidth(0)

        self.label2_3 = StrongBodyLabel("目标加载器", self)

        self.comboBox2_3 = AcrylicComboBox(self)
        self.comboBox2_3.setPlaceholderText("目标加载器")
        self.comboBox2_3.addItems(sorted(list(LOADER_TYPE.keys())))
        self.comboBox2_3.setCurrentIndex(0)
        self.comboBox2_3.setToolTip("选择目标加载器")
        self.comboBox2_3.installEventFilter(ToolTipFilter(self.comboBox1_1, 1000))
        self.comboBox2_3.setMaxVisibleItems(15)
        self.comboBox2_3.setMinimumWidth(0)

        self.switchButton = SwitchButton("跨版本", self, IndicatorPosition.RIGHT)
        self.switchButton.setChecked(False)
        self.switchButton.setOnText("跨版本")
        self.switchButton.setOffText("跨版本")
        self.switchButton.setToolTip("如果要将模组更新到与现有版本不同的版本与加载器，请勾选！")
        self.switchButton.installEventFilter(ToolTipFilter(self.switchButton, 1000))
        self.switchButton.setMinimumWidth(0)

        self.card1 = GrayCard("管理")
        self.card1.addWidget(self.label1_1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card1.addWidget(self.comboBox1_1)

        self.card1.addWidget(self.button1)
        self.card1.addWidget(self.settingButton)
        self.card1.addWidget(self.reloadButton)

        self.card2 = GrayCard("更新")

        self.card2.addWidget(self.updateButton)
        self.card2.addWidget(self.label2_1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card2.addWidget(self.comboBox2_1)
        self.card2.addWidget(self.label2_2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card2.addWidget(self.comboBox2_2)
        self.card2.addWidget(self.label2_3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.card2.addWidget(self.comboBox2_3)
        self.card2.addWidget(self.switchButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)

        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

    def button1Clicked(self):
        f.showFile(f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1_1.currentText()]))

    def settingButtonClicked(self):
        self.modSettingMessageBox = ModSettingMessageBox(self.parent().parent().parent().parent().parent())
        self.modSettingMessageBox.show()

    def loadModList(self):
        if not f.existPath(f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1_1.currentText()])):
            return
        self.data = []
        self.showWidget(False)

        self.cardGroup1.deleteLater()
        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        data = [i for i in f.walkFile(f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1_1.currentText()]), 1) if f.splitPath(i, 2) in FILE_SUFFIX[self.comboBox1_1.currentText()]]
        self.cardGroup1.setTitle(f"发现{self.comboBox1_1.currentText()}{len(data)}个")
        self.thread1 = MyThread("获得文件信息", f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1_1.currentText()]))
        self.thread2 = MyThread("从文件获得模组信息")
        self.thread1.signalList.connect(self.thread1_1)
        self.thread1.start()
        for i in data:
            self.infoCard = ModFileInfoCard(i, self)
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignmentFlag.AlignTop)
            self.cardGroup1.addWidget(self.infoCard)

    def thread1_1(self, msg):
        self.data = msg

        self.thread2.signalList.connect(self.thread2_1)
        self.thread2.signalBool.connect(self.thread2_1)
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
            self.comboBox2_3.setCurrentText(loader)
        if version:
            version = Counter(version)
            version = dict([val, key] for key, val in version.items())
            version = version[sorted(version.keys())[-1]]

            self.comboBox2_2.setCurrentText(version)

    def thread2_1(self, msg):
        self.showWidget(True)

    def updateButtonClicked(self):
        self.showWidget(False)

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"正在通过{self.comboBox2_1.currentText()}检查资源在{self.comboBox2_2.currentText()}{self.comboBox2_3.currentText()}的更新", Qt.Orientation.Vertical, False, -1, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()

        self.thread3 = MyThread("获得模组最新版本", [f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1_1.currentText()]), self.comboBox2_2.currentText(), self.comboBox2_3.currentText(), self.comboBox2_1.currentText()])
        self.thread3.signalDict.connect(self.thread3_1)
        self.thread3.signalBool.connect(self.thread3_2)
        self.thread3.signalInt.connect(self.thread3_3)
        self.thread3.start()

    def thread3_1(self, msg):
        self.showWidget(True)

        self.data = msg["old"]

        list1 = []
        name_list = []

        for i in msg["new"]:
            for j in msg["old"]:
                if i["模组id"] == j["模组id"]:
                    if i["id"] != j["id"]:
                        if not self.switchButton.checked:
                            if i["更新日期"] < j["更新日期"]:
                                continue
                        if j["源文件名称"] in name_list:
                            continue
                        name_list.append(j["源文件名称"])
                        list1.append([j, i])
        list1 = sorted(list1, key=lambda x: x[0]["文件名称"])
        self.infoBar.isClosable = True
        self.infoBar.closeButton.click()
        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"有{len(list1)}个资源在{self.comboBox2_2.currentText()}{self.comboBox2_3.currentText()}有新版本", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.show()
        self.modUpdateMessageBox = ModUpdateMessageBox("资源更新", list1, f.pathJoin(setting.read("minecraftJavaPath"), FILE_PATH[self.comboBox1_1.currentText()]), self)
        self.modUpdateMessageBox.exec()

    def thread3_2(self, msg):
        if not msg:
            self.showWidget(True)
            self.infoBar.isClosable = True
            self.infoBar.closeButton.click()
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "错误", f"检查更新失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

    def thread3_3(self, msg):
        try:
            self.progressBar.setValue(msg)
        except:
            pass

    def showWidget(self, stat: bool):
        self.updateButton.setEnabled(stat)
        self.switchButton.setEnabled(stat)
        self.comboBox2_1.setEnabled(stat)
        self.comboBox2_2.setEnabled(stat)
        self.comboBox2_3.setEnabled(stat)
