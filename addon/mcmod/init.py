import sys, os

sys.path = [os.path.dirname(sys.argv[0])] + sys.path
from source.custom import *

os.chdir(os.path.dirname(__file__))

try:
    from beta.source.custom import *
except:
    pass

RELEASE_VERSIONS = ["1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.18.2", "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.13.2", "1.12.2", "1.9.4", "1.8.9", "1.7.10"]
CURSEFORGE_API_KEY = {
    "Accept": "application/json",
    "x-api-key": "$2a$10$21wJppLHY6oZ4Fs/Jb85WuJdpWppY6RcX3o.G9.372hxeiec8Wy6m"
}
CURSEFORGE_POST_API_KEY = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-api-key": "$2a$10$21wJppLHY6oZ4Fs/Jb85WuJdpWppY6RcX3o.G9.372hxeiec8Wy6m"
}
CURSEFORGE_VERSION_TYPE = {
    1: "release",
    2: "beta",
    3: "alpha",
}
CURSEFORGE_LOADER_TYPE = {
    0: "any",
    1: "forge",
    2: "cauldron",
    3: "liteloader",
    4: "fabric",
    5: "quilt",
    6: "neoforge",
}


def getMCVersionList():
    """
    获取我的世界版本列表
    @return: 我的世界版本列表
    """
    global RELEASE_VERSIONS
    try:
        list = []
        response = f.requestGet("https://api.modrinth.com/v2/tag/game_version", program.REQUEST_HEADER)
        response = json.loads(response)
        for i in response:
            if i["version_type"] == "release":
                list.append(i["version"])
        MINECRAFT_VERSIONS = list
        return list
    except:
        return MINECRAFT_VERSIONS


def searchMod(name: str, source: str, version: str) -> list:
    """
    搜索模组
    @param name: 名称
    @return: 列表
    """
    logging.debug(f"在{source}搜索应用{name}")
    list = []

    if source == "Modrinth":
        version = f',["versions:{version}"]' if version != "全部" else ""
        data = f.requestGet(f'https://api.modrinth.com/v2/search?query={name}&facets=[["project_type:mod"]{version}]&limit=50', program.REQUEST_HEADER)
        if "hits" in json.loads(data):
            data = json.loads(data)["hits"]
            for i in data:
                list.append({"id": i["project_id"],
                             "名称": i["title"],
                             "图标": i["icon_url"],
                             "介绍": i["description"],
                             "下载量": i["downloads"],
                             "游戏版本": f.sortVersion([j for j in i["versions"] if j in RELEASE_VERSIONS]),
                             "更新日期": i["date_modified"].split("T")[0],
                             "作者": i["author"],
                             "来源": "Modrinth",
                             })
    elif source == "CurseForge":
        version = f"&gameVersion={version}" if version != "全部" else ""
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/search?gameId=432&classId=6{version}&searchFilter={name}&pageSize=50&sortOrder=desc", CURSEFORGE_API_KEY)
        if "data" in json.loads(data):
            data = json.loads(data)["data"]
            for i in data:
                list.append({"id": i["id"],
                             "名称": i["name"],
                             "图标": i["logo"]["url"],
                             "介绍": i["summary"],
                             "下载量": i["downloadCount"],
                             "游戏版本": f.sortVersion([j for j in [k["gameVersion"] for k in i["latestFilesIndexes"]] if j in RELEASE_VERSIONS]),
                             "更新日期": i["dateModified"].split("T")[0],
                             "作者": i["authors"][0]["name"],
                             "来源": "CurseForge",
                             })
    return list


def getModInfo(info: dict) -> dict:
    """
    获得模组信息
    @param info: 该模组搜索结果
    """
    dict = {}
    if info["来源"] == "Modrinth":
        data = f.requestGet(f"https://api.modrinth.com/v2/project/{info["id"]}", program.REQUEST_HEADER)
        data = json.loads(data)
        dict.update(info)
        dict.update({
            "模组版本id": data["versions"],
            "源代码链接": data["source_url"],
            "加载器": data["loaders"],
            "发布日期": data["published"].split("T")[0],
            "网站链接": f"https://modrinth.com/mod/{data["slug"]}",
        })
    elif info["来源"] == "CurseForge":
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/{info["id"]}", CURSEFORGE_API_KEY)
        data = json.loads(data)["data"]

        data2 = f.requestGet(f"https://api.curseforge.com/v1/mods/{info["id"]}/files", CURSEFORGE_API_KEY)
        data2 = json.loads(data2)["data"]

        loader = []
        for i in data2:
            loader += [j.lower() for j in i["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()]
        loader = list(set(loader))

        dict.update(info)
        dict.update({
            "模组版本id": [i["id"] for i in data2],
            "源代码链接": data["links"]["sourceUrl"],
            "加载器": loader,
            "发布日期": data["dateCreated"].split("T")[0],
            "网站链接": data["links"]["websiteUrl"],
        })
    return dict


def getModFile(info: dict) -> dict:
    """
    获得模组文件
    @param info: 该模组搜索结果
    """
    list1 = []
    if info["来源"] == "Modrinth":
        data = f.requestGet(f"https://api.modrinth.com/v2/project/{info["id"]}/version", program.REQUEST_HEADER)
        data = json.loads(data)
        for i in data:
            list1.append({
                "id": i["id"],
                "模组id": i["project_id"],
                "名称": i["name"],
                "版本号": i["version_number"],
                "前置": i["dependencies"],
                "游戏版本": f.sortVersion([j for j in i["game_versions"] if j in RELEASE_VERSIONS]),
                "版本类型": i["version_type"],
                "加载器": i["loaders"],
                "下载量": i["downloads"],
                "更新日期": i["date_published"].split("T")[0],
                "来源": "Modrinth",
                "哈希值": i["files"][0]["hashes"]["sha1"],
                "下载链接": i["files"][0]["url"],
                "文件名称": i["files"][0]["filename"],
                "文件大小": i["files"][0]["size"],
            })
    elif info["来源"] == "CurseForge":
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/{info["id"]}/files", CURSEFORGE_API_KEY)
        data = json.loads(data)["data"]

        for i in data:
            list1.append({
                "id": i["id"],
                "模组id": i["modId"],
                "名称": i["displayName"],
                # "版本号": i["version_number"],
                "前置": i["dependencies"],
                "游戏版本": f.sortVersion([j for j in i["gameVersions"] if j in RELEASE_VERSIONS]),
                "版本类型": CURSEFORGE_VERSION_TYPE[i["releaseType"]],
                "加载器": [j.lower() for j in i["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()],
                "下载量": i["downloadCount"],
                "更新日期": i["fileDate"].split("T")[0],
                "来源": "CurseForge",
                "哈希值": i["hashes"][0]["value"],
                "下载链接": i["downloadUrl"],
                "文件名称": i["fileName"],
                "文件大小": i["fileLength"],
            })

    dict = {}
    for i in RELEASE_VERSIONS:
        for j in list1:
            if i in j["游戏版本"]:
                if i not in dict.keys():
                    dict[i] = [j]
                else:
                    dict[i].append(j)
    for i in dict.keys():
        dict[i].sort(key=lambda x: x["更新日期"], reverse=True)
    return dict


def getFileInfo(info: dict):
    """
    获得文件信息
    @param info: 文件数据
    """
    dict = {}
    if info["来源"] == "Modrinth":
        data = f.requestGet(f"https://api.modrinth.com/v2/version/{info["id"]}", program.REQUEST_HEADER)
        data = json.loads(data)
        dict = {
            "id": data["id"],
            "模组id": data["project_id"],
            "名称": data["name"],
            "版本号": data["version_number"],
            "前置": data["dependencies"],
            "游戏版本": f.sortVersion([j for j in data["game_versions"] if j in RELEASE_VERSIONS]),
            "版本类型": data["version_type"],
            "加载器": data["loaders"],
            "下载量": data["downloads"],
            "更新日期": data["date_published"].split("T")[0],
            "来源": "Modrinth",
            "哈希值": data["files"][0]["hashes"]["sha1"],
            "下载链接": data["files"][0]["url"],
            "文件名称": data["files"][0]["filename"],
            "文件大小": data["files"][0]["size"],
        }

    elif info["来源"] == "CurseForge":
        post_info = {
            "fileIds": [
                info["id"]
            ]
        }
        data = requests.post("https://api.curseforge.com/v1/mods/files", headers=CURSEFORGE_POST_API_KEY, json=post_info)
        data = data.json()
        dict = {
            "id": data["id"],
            "模组id": data["modId"],
            "名称": data["displayName"],
            # "版本号": data["version_number"],
            "前置": data["dependencies"],
            "游戏版本": f.sortVersion([j for j in data["gameVersions"] if j in RELEASE_VERSIONS]),
            "版本类型": CURSEFORGE_VERSION_TYPE[data["releaseType"]],
            "加载器": [j.lower() for j in data["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()],
            "下载量": data["downloadCount"],
            "更新日期": data["fileDate"].split("T")[0],
            "来源": "CurseForge",
            "哈希值": data["hashes"][0]["value"],
            "下载链接": data["downloadUrl"],
            "文件名称": data["fileName"],
            "文件大小": data["fileLength"],
        }
    return dict


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
        if self.mode == "搜索模组":
            try:
                data = searchMod(self.data[0], self.data[1], self.data[2])
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
            path += ".zb.mod.downloading"
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
        if self.mode == "获得游戏版本列表":
            self.signalList.emit(getMCVersionList())
        if self.mode == "获得模组详细信息":
            try:
                data = getModInfo(self.data)
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "加载模组下载列表":
            data = getModFile(self.data)
            try:
                data = getModFile(self.data)
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)

    def cancel(self):
        logging.debug("取消下载")
        self.isCancel = True


class SmallModInfoCard(SmallInfoCard):
    """
    模组信息小卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, data: dict, source: str, parent: QWidget = None):
        """
        @param data: 模组数据
        @param source: 模组来源
        """
        super().__init__(parent)

        self.data = data
        self.source = source

        self.mainButton.deleteLater()

        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data["名称"])}.png", self.data["图标"])
        self.setTitle(f"{self.data["名称"]}")

        self.setInfo(self.data["介绍"], 0)
        self.setInfo(f"下载量：{self.data["下载量"]}", 1)
        self.setInfo(f"游戏版本：{self.data["游戏版本"][0] + "-" + self.data["游戏版本"][-1] if len(self.data["游戏版本"]) > 1 else self.data["游戏版本"][0] if len(self.data["游戏版本"]) > 0 else "无"}", 2)
        self.setInfo(f"更新日期：{self.data["更新日期"]}", 3)

    def mousePressEvent(self, event):
        self.signalDict.emit(self.data)

    # def mainButtonClicked(self):
    #     self.mainButton.setEnabled(False)
    #
    #     self.thread = MyThread("下载模组", (self.data["文件名称"], self.data["下载链接"]))
    #     self.thread.signalStr.connect(self.thread1)
    #     self.thread.signalInt.connect(self.thread2)
    #     self.thread.signalBool.connect(self.thread3)
    #     self.thread.start()
    #
    #     self.progressBar = ProgressBar(self)
    #     self.progressBar.setAlignment(Qt.AlignCenter)
    #     self.progressBar.setRange(0, 100)
    #     self.progressBar.setValue(0)
    #     self.progressBar.setMinimumWidth(200)
    #
    #     self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载模组 {self.data["名称"]}", Qt.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
    #     self.infoBar.addWidget(self.progressBar)
    #     self.infoBar.show()
    #     self.infoBar.closeButton.clicked.connect(self.thread.cancel)
    #
    # def thread1(self, msg):
    #     self.filePath = msg
    #
    # def thread2(self, msg):
    #     try:
    #         self.infoBar.contentLabel.setText(f"正在下载模组 {self.data["名称"]}")
    #         self.progressBar.setValue(msg)
    #     except:
    #         return
    #     if msg == 100:
    #         f.moveFile(self.filePath, self.filePath.replace(".zb.mod.downloading", ""))
    #
    #         self.infoBar.contentLabel.setText(f"{self.data["名称"]} 下载成功")
    #         self.infoBar.closeButton.click()
    #
    #         self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载", f"模组 {self.data["名称"]} 下载成功", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
    #         self.infoBar.show()
    #         self.button1 = PushButton("打开目录", self, FIF.FOLDER)
    #         self.button1.clicked.connect(self.button1Clicked)
    #         self.infoBar.addWidget(self.button1)
    #
    #         self.progressBar.setValue(0)
    #         self.progressBar.deleteLater()
    #         self.mainButton.setEnabled(True)

    def thread3(self, msg):
        if msg:
            f.delete(self.filePath)
        self.mainButton.setEnabled(True)

    def button1Clicked(self):
        f.startFile(setting.read("downloadPath"))
        self.infoBar.closeButton.click()


class BigModInfoCard(BigInfoCard):
    """
    模组信息大卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, data: dict, loading_card, card_group, parent: QWidget = None):
        """
        @param data: 模组数据
        @param source: 模组来源
        """
        super().__init__(parent)
        self.data = data
        self.loadingCard = loading_card
        self.cardGroup = card_group
        self.hide()

        self.mainButton.deleteLater()

        self.loadingCard.setText("加载中")
        self.loadingCard.show()

        self.thread1 = MyThread("获得模组详细信息", data)
        self.thread1.signalDict.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

    def thread1_1(self, msg):
        self.setTitle(msg["名称"])
        self.setInfo(msg["介绍"])
        self.setImg(f"{msg["来源"]}/{f.removeIllegalPath(msg["名称"])}.png", msg["图标"])
        self.addUrl(msg["来源"], msg["网站链接"], FIF.LINK)
        if msg["源代码链接"]:
            self.addUrl("源代码", msg["源代码链接"], FIF.GITHUB)
        self.addUrl("MC百科", f"https://search.mcmod.cn/s?key={msg["名称"]}", FIF.LINK)

        self.addData("作者", msg["作者"])
        self.addData("下载量", msg["下载量"])
        self.addData("发布日期", msg["发布日期"])
        self.addData("更新日期", msg["更新日期"])
        for i in msg["加载器"]:
            self.addTag(i)
        self.show()
        self.loadingCard.hide()

        self.cardGroup.hide()
        self.loadingCard.setText("加载中")
        self.loadingCard.show()

        self.thread2 = MyThread("加载模组下载列表", self.data)
        self.thread2.signalDict.connect(self.thread2_1)
        self.thread2.signalBool.connect(self.thread2_2)
        self.thread2.start()

    def thread1_2(self, msg):
        if not msg:
            self.backButtonClicked()
            self.loadingCard.hide()

    def backButtonClicked(self):
        self.signalBool.emit(True)
        self.deleteLater()

    def thread2_1(self, msg):
        self.loadingCard.hide()
        for k in msg.keys():
            self.cardGroup.addWidget(StrongBodyLabel(k, self))
            for v in msg[k]:
                self.cardGroup.addWidget(SmallFileInfoCard(v))
        self.cardGroup.show()

    def thread2_2(self, msg):
        if not msg:
            self.loadingCard.setText("加载失败")
            self.loadingCard.show()


class SmallFileInfoCard(SmallInfoCard):
    """
    文件信息小卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, data: dict, parent: QWidget = None):
        """
        @param data: 模组数据
        """
        super().__init__(parent)
        self.data = data

        self.image.deleteLater()

        self.setTitle(f"{data["名称"]} · {data["版本类型"]}")
        self.setInfo("、".join(data["加载器"]) + (" | " if len(data["加载器"]) > 0 else "") + ("、".join(data["游戏版本"]) if len(data["游戏版本"]) <= 10 else f"支持{data["游戏版本"][0]}-{data["游戏版本"][-1]}共{len(data["游戏版本"])}个版本"), 0)
        self.setInfo(f"下载量：{data["下载量"]}", 2)
        self.setInfo(f"更新日期：{data["更新日期"]}", 3)

        self.mainButton.setText("下载")
        self.mainButton.setIcon(FIF.DOWNLOAD)

    def mainButtonClicked(self):
        print(self.data)


class AddonTab(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.GAME)

        self.vBoxLayout.setSpacing(8)

        self.lineEdit = AcrylicSearchLineEdit(self)
        self.lineEdit.setPlaceholderText("模组名称")
        self.lineEdit.setToolTip("搜索模组，数据来源：\n Curseforge\n Modrinth")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.lineEdit.returnPressed.connect(self.lineEditReturnPressed)
        self.lineEdit.searchButton.setEnabled(False)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("下载应用来源")
        self.comboBox1.addItems(["CurseForge", "Modrinth"])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择下载应用来源")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("模组版本")
        self.comboBox2.addItems(["全部"])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择模组版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox2, 1000))
        self.comboBox2.setMaxVisibleItems(10)

        self.card1 = GrayCard("搜索")
        self.card1.addWidget(self.lineEdit)

        self.card2 = GrayCard("筛选")
        self.card2.addWidget(self.comboBox1)
        self.card2.addWidget(self.comboBox2)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.thread1 = MyThread("获得游戏版本列表")
        self.thread1.signalList.connect(self.thread1_1)
        self.thread1.start()

        self.loadingCard.setText("正在获得游戏版本列表")
        self.loadingCard.show()
        self.lineEdit.setEnabled(False)
        self.comboBox2.setEnabled(False)
        self.comboBox1.setEnabled(False)

    def lineEditChanged(self, text):
        self.lineEdit.searchButton.setEnabled(bool(text))

    def lineEditReturnPressed(self):
        self.lineEdit.searchButton.click()

    def searchButtonClicked(self):
        if self.lineEdit.text():
            self.cardGroup1.deleteLater()
            self.cardGroup1 = CardGroup(self.view)
            self.vBoxLayout.addWidget(self.cardGroup1)

            self.cardGroup1.setTitleEnabled(False)
            self.lineEdit.setEnabled(False)
            self.comboBox2.setEnabled(False)
            self.comboBox1.setEnabled(False)

            self.loadingCard.setText("搜索中...")
            self.loadingCard.show()

            self.thread2 = MyThread("搜索模组", [self.lineEdit.text(), self.comboBox1.currentText(), self.comboBox2.currentText()])
            self.thread2.signalList.connect(self.thread2_1)
            self.thread2.signalBool.connect(self.thread2_2)
            self.thread2.start()

    def thread1_1(self, msg):
        self.loadingCard.hide()
        self.comboBox2.addItems(msg)
        self.lineEdit.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox1.setEnabled(True)

    def thread2_1(self, msg):
        self.loadingCard.hide()
        for i in msg:
            self.infoCard = SmallModInfoCard(i, self.comboBox1.currentText())
            self.infoCard.signalDict.connect(self.showModPage)
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignTop)
            self.cardGroup1.addWidget(self.infoCard)
        if msg:
            self.cardGroup1.setTitle(f"搜索结果（{len(msg)}个）")
        else:
            self.cardGroup1.setTitle(f"无搜索结果")
        self.cardGroup1.setTitleEnabled(True)

        self.lineEdit.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox1.setEnabled(True)

    def thread2_2(self, msg):
        if not msg:
            self.loadingCard.setText("搜索失败！")
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox2.setEnabled(True)
            self.comboBox1.setEnabled(True)

    def showModPage(self, msg):
        """
        展示模组页面
        """
        self.cardGroup1.hide()
        self.card1.hide()
        self.card2.hide()

        self.cardGroup2 = CardGroup("文件", self.view)
        self.vBoxLayout.addWidget(self.cardGroup2)
        self.cardGroup2.hide()

        self.bigModInfoCard = BigModInfoCard(msg, self.loadingCard, self.cardGroup2)
        self.bigModInfoCard.signalBool.connect(self.hideModPage)
        self.vBoxLayout.insertWidget(0, self.bigModInfoCard)

    def hideModPage(self, msg):
        """
        隐藏模组页面
        """
        self.loadingCard.hide()
        self.cardGroup2.deleteLater()
        self.vBoxLayout.removeWidget(self.bigModInfoCard)
        self.cardGroup1.show()
        self.card1.show()
        self.card2.show()
