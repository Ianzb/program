import logging

from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, setting, window, sf
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window
    setting.adds({"sortGoalPath": "",
                  "wechatPath": "",
                  "sortNameBlacklist": [],
                  "sortPathBlacklist": [],
                  "sortFolder": [zb.DESKTOP_PATH()],
                  "sortFormat": {"PPT": [".ppt", ".pptx"],
                                 "文档": [".doc", ".docx", ".txt", ".pdf"],
                                 "表格": [".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".csv"],
                                 "图片": [".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tga", ".bmp", ".dds", ".svg", ".eps", ".hdr", ".raw", ".exr", ".psd"],
                                 "音频": [".mp3", ".wav", ".ogg", ".wma", ".ape", ".flac", ".aac"],
                                 "视频": [".mp4", ".flv", ".mov", ".avi", ".mkv", ".wmv"],
                                 "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
                                 "镜像": [".iso", ".img", ".bin"],
                                 "安装包": [".exe", ".msi", ".apk"]
                                 },
                  "sortWechat": True,
                  "clearFile": True,
                  "clearTrash": False,
                  "deleteToTrash": False,
                  })
    sf = SortFunctions()


def addonWidget():
    return AddonPage(window)


class SortFunctions:
    def clearEmptyFile(self, path: str):
        """
        删除文件夹下的空文件
        :param path: 文件夹路径
        """
        if zb.isDir(path):
            paths = zb.walkFile(path, True)
            if paths:
                for i in paths:
                    if zb.fileSize(i) == 0:
                        zb.deleteFile(i, setting.read("deleteToTrash"))

    def clearEmptyDir(self, path):
        """
        删除文件夹下的空文件夹
        :param path: 文件夹路径
        """
        if zb.isDir(path):
            paths = zb.walkDir(path, True)
            if paths:
                for i in paths:
                    try:
                        os.rmdir(i)
                    except:
                        pass

    def clearRepeatFile(self, path: str):
        """
        清理重复文件
        :param path: 文件夹路径
        """
        from .filecmp import cmp
        if zb.isDir(path):
            names = zb.walkFile(path, True)
            if not names:
                return
            names.sort(key=lambda i: len(i))
            for i in range(len(names)):
                for j in range(len(names[:i])):
                    if not zb.existPath(names[i]) or not zb.existPath(names[j]): continue
                    if cmp(names[i], names[j], False):
                        zb.deletePath(sorted([names[i], names[j]])[0], setting.read("deleteToTrash"))

    def clearFile(self, path: str):
        """
        清理文件夹3合1
        :param path: 文件夹路径
        """
        try:
            self.clearEmptyFile(path)
            self.clearEmptyDir(path)
            self.clearRepeatFile(path)
            logging.debug(f"成功清理{path}文件夹")
        except Exception as ex:
            logging.warning(f"无法清理{path}文件夹，报错信息：{ex}！")

    def belongDir(self, path: str, parent: str) -> bool:
        """
        文件夹是否包含
        :param path: 子文件夹
        :param parent: 母文件夹
        @return: 是否
        """
        path = os.path.abspath(path)
        parent = os.path.abspath(parent)
        try:
            data = os.path.commonpath([parent]) == os.path.commonpath([parent, path])
        except:
            data = False
        return data

    def sortDir(self, old: str, new: str, mode: int = 0):
        """
        整理文件
        :param old: 旧文件夹路径
        :param new: 新文件夹路径
        :param mode: 模式：0 全部整理 1 仅文件 2 仅文件夹
        """

        try:
            blacklist = [self.getSortNameBlacklist(), self.getSortPathBlacklist()]
            if mode in [0, 1]:
                file_list = zb.walkFile(old, True)
                if file_list:
                    for i in file_list:
                        if i.startswith("~$"): continue  # 跳过office临时文件
                        for j in range(len(setting.read("sortFormat").values())):
                            if zb.getFileSuffix(i).lower() in list(setting.read("sortFormat").values())[j]:
                                if zb.getFileName(i) in blacklist[0] or i in blacklist[1]:
                                    continue
                                zb.setOnlyRead(i, False)
                                zb.movePath(i, zb.joinPath(new, list(setting.read("sortFormat").keys())[j], zb.getFileName(i)))
            if mode in [0, 2]:
                file_list = zb.walkDir(old, True)
                if file_list:
                    for i in file_list:
                        if zb.getFileName(i) in blacklist[0] or i in blacklist[1]:
                            continue
                        zb.movePath(i, zb.joinPath(new, "文件夹", zb.getFileName(i)))
            logging.debug(f"成功整理{old}文件夹！")
        except Exception as ex:
            logging.warning(f"无法整理{old}文件夹，报错信息：{ex}！")

    def sortWechatFiles(self):
        """
        整理微信文件
        """
        try:
            list1 = []
            list2 = []
            for i in zb.walkDir(setting.read("wechatPath"), True):
                if zb.existPath(zb.joinPath(i, "FileStorage/File")):
                    list1.append(zb.joinPath(i, "FileStorage/File"))
                elif zb.existPath(zb.joinPath(i, "msg/file/")):
                    list1.append(zb.joinPath(i, "msg/file/"))
            for i in list1:
                if zb.walkDir(i, True) is None:
                    return
                list2 = list2 + zb.walkDir(i, True)
            for i in list2:
                self.sortDir(i, setting.read("sortGoalPath"))
            for i in list1:
                self.sortDir(i, setting.read("sortGoalPath"), 1)
            logging.debug("成功整理微信文件！")
        except Exception as ex:
            logging.warning(f"无法整理微信文件，报错信息：{ex}！")

    def clearSystemCache(self):
        """
        清理系统缓存
        """
        try:
            zb.clearDir(os.getenv("TEMP"))
        except:
            pass

    def clearTrash(self):
        """
        清空回收站
        """
        try:
            from winshell import recycle_bin
            recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            logging.debug("成功清空回收站！")
        except Exception as ex:
            logging.warning(f"无法清空回收站，报错信息：{ex}！")

    def getSortNameBlacklist(self):
        """
        获取整理文件名称黑名单
        @return: 整理文件名称黑名单列表
        """
        data = setting.read("sortNameBlacklist")
        return data

    def getSortPathBlacklist(self):
        """
        获取整理文件路径黑名单
        @return: 整理文件路径黑名单列表
        """
        data = list(setting.read("sortPathBlacklist"))
        if zb.isSamePath(setting.read("sortGoalPath"), zb.DESKTOP_PATH()):
            data += [zb.joinPath(zb.DESKTOP_PATH(), i) for i in list(setting.read("sortFormat").keys()) + ["文件夹"]]
        elif self.belongDir(setting.read("sortGoalPath"), zb.DESKTOP_PATH()):
            for i in zb.walkDir(zb.DESKTOP_PATH(), True):
                if self.belongDir(setting.read("sortGoalPath"), i):
                    data.append(i)
        return list(set(data))


class NameBlacklistEditMessageBox(MessageBoxBase):
    """
    可编辑名称黑名单的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("整理文件名称黑名单", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件名称\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortNameBlacklist")))
        self.textEdit.setNewToolTip("输入文件名称\n一行一个")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortNameBlacklist", sorted(list(set([i.strip() for i in zb.clearIllegalPathName(self.textEdit.toPlainText()).split("\n") if i]))))

        self.accept()
        self.accepted.emit()


class PathBlacklistEditMessageBox(MessageBoxBase):
    """
    可编辑路径黑名单的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("整理文件路径黑名单", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件完整路径\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortPathBlacklist")))
        self.textEdit.setNewToolTip("输入文件完整路径\n一行一个")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.addFolderButton = PushButton("选择文件夹", self.buttonGroup)
        self.addFolderButton.clicked.connect(self.addFolderButtonClicked)

        self.addFileButton = PushButton("选择文件", self.buttonGroup)
        self.addFileButton.clicked.connect(self.addFileButtonClicked)

        self.buttonLayout.insertWidget(1, self.addFolderButton, 1, Qt.AlignVCenter)
        self.buttonLayout.insertWidget(2, self.addFileButton, 1, Qt.AlignVCenter)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortPathBlacklist", sorted(list(set([zb.formatPathString(i.strip()) for i in zb.clearIllegalPathName(self.textEdit.toPlainText()).split("\n") if i]))))

        self.accept()
        self.accepted.emit()

    def addFolderButtonClicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择黑名单文件夹", "C:/")
        if zb.existPath(get):
            get = zb.formatPathString(get)
            if get not in sorted(list(set([zb.formatPathString(i.strip()) for i in zb.clearIllegalPathName(self.textEdit.toPlainText()).split("\n") if i]))):
                self.textEdit.setText((self.textEdit.toPlainText().strip() + "\n" + get).strip())

    def addFileButtonClicked(self):
        get = QFileDialog.getOpenFileName(self, "选择黑名单文件", "C:/")[0]
        if zb.existPath(get):
            get = zb.formatPathString(get)
            if get not in sorted(list(set([zb.formatPathString(i.strip()) for i in zb.clearIllegalPathName(self.textEdit.toPlainText()).split("\n") if i]))):
                self.textEdit.setText((self.textEdit.toPlainText().strip() + "\n" + get).strip())


class SortFolderEditMessageBox(MessageBoxBase):
    """
    可编辑整理目录的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("整理目录", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件夹完整路径\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortFolder")))
        self.textEdit.setNewToolTip("输入文件夹完整路径\n一行一个")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.addButton = PushButton("选择文件夹", self.buttonGroup)
        self.addButton.clicked.connect(self.addButtonClicked)

        self.resetButton = PushButton("重置", self.buttonGroup)
        self.resetButton.clicked.connect(self.resetButtonClicked)

        self.buttonLayout.insertWidget(1, self.addButton, 1, Qt.AlignVCenter)
        self.buttonLayout.insertWidget(2, self.resetButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortFolder", sorted(list(set([zb.formatPathString(i.strip()) for i in zb.clearIllegalPathName(self.textEdit.toPlainText()).split("\n") if i]))))
        self.accept()
        self.accepted.emit()

    def addButtonClicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择整理文件夹", "C:/")
        if zb.existPath(get):
            get = zb.formatPathString(get)
            if get not in sorted(list(set([zb.formatPathString(i.strip()) for i in zb.clearIllegalPathName(self.textEdit.toPlainText()).split("\n") if i]))):
                self.textEdit.setText((self.textEdit.toPlainText().strip() + "\n" + get).strip())

    def resetButtonClicked(self):
        setting.reset("sortFolder")
        self.accept()
        self.accepted.emit()


class SortFormatEditMessageBox(MessageBoxBase):
    """
    可编辑整理文件类型的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("整理文件类型", self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(2)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["类型", "后缀名"])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.tableView.setNewToolTip("后缀名逗号（中英文均可）分割，加不加分割点均可")

        self.tableView.setRowCount(len(setting.read("sortFormat").keys()))
        for i in range(len(setting.read("sortFormat").keys())):
            self.tableView.setItem(i, 0, QTableWidgetItem(list(setting.read("sortFormat").keys())[i]))
            self.tableView.setItem(i, 1, QTableWidgetItem(",".join(sorted(list(setting.read("sortFormat").values())[i])).replace(".", "")))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.tableView)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.addButton = PushButton("添加行", self.buttonGroup)
        self.addButton.clicked.connect(self.addButtonClicked)

        self.removeButton = PushButton("删除选中行", self.buttonGroup)
        self.removeButton.clicked.connect(self.removeButtonClicked)

        self.resetButton = PushButton("重置", self.buttonGroup)
        self.resetButton.clicked.connect(self.resetButtonClicked)

        self.buttonLayout.insertWidget(1, self.addButton, 1, Qt.AlignVCenter)
        self.buttonLayout.insertWidget(2, self.removeButton, 1, Qt.AlignVCenter)
        self.buttonLayout.insertWidget(3, self.resetButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumSize(600, 400)

    def yesButtonClicked(self):
        data = {}
        for i in range(self.tableView.rowCount()):
            try:
                k = self.tableView.item(i, 0).text()
                v = self.tableView.item(i, 1).text()
            except:
                continue
            v = v.lower().replace("，", ",").replace(" ", "").strip().split(",")
            for i in range(len(v)):
                if v[i][0] != ".":
                    v[i] = "." + v[i]
            v = sorted(list(set(v)))
            if k.strip():
                if k not in data.keys():
                    data[k] = v
                else:
                    data[k] += v
                    data[k] = sorted(list(set(data[k])))
        setting.save("sortFormat", data)
        self.accept()
        self.accepted.emit()

    def addButtonClicked(self):
        self.tableView.hide()
        self.tableView.setRowCount(self.tableView.rowCount() + 1)
        self.tableView.show()

    def removeButtonClicked(self):
        selected = self.tableView.selectedIndexes()[::2]
        for i in range(len(selected)):
            selected[i] = selected[i].row()
        selected.sort(reverse=True)
        for i in selected:
            self.tableView.removeRow(i)

    def resetButtonClicked(self):
        setting.reset("sortFormat")
        self.accept()
        self.accepted.emit()


class SortPathSettingCard(SettingCard):
    """
    整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.ALIGNMENT, "路径", f"整理目标路径：{setting.read("sortGoalPath")}\n微信路径：{setting.read("wechatPath")}", parent)
        self.button1 = PushButton("整理目标目录", self, FIF.FOLDER_ADD)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setNewToolTip("设置整理目标目录")

        self.button2 = PushButton("微信目录", self, FIF.FOLDER_ADD)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setNewToolTip("设置微信WeChat Files文件夹目录")

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setAcceptDrops(True)

        self.setText()
        setting.signalConnect(self.setEvent)

    def setEvent(self, msg):
        if msg in ["sortGoalPath", "wechatPath"]:
            self.setText()

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择整理目标目录", setting.read("sortGoalPath"))
        self.saveSetting(get)

    def button2Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择微信WeChat Files文件夹目录", setting.read("wechatPath"))
        self.saveWechatPath(get)

    def setText(self):
        self.contentLabel.setText(f"整理目标路径：{setting.read("sortGoalPath")}\n微信路径：{setting.read("wechatPath")}")

    def saveSetting(self, path: str):
        if zb.existPath(path):
            setting.save("sortGoalPath", path)
        self.setText()

    def saveWechatPath(self, path: str):
        if zb.existPath(path):
            setting.save("wechatPath", path)
        self.setText()


class SortSettingCard(SettingCard):
    """
    整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.EDIT, "目录", "", parent)
        self.button1 = PushButton("整理文件名称黑名单", self)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setNewToolTip("编辑整理文件名称黑名单（填写文件名）")

        self.button2 = PushButton("整理文件路径黑名单", self)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setNewToolTip("编辑整理文件路径黑名单（填写文件完整路径）")

        self.button3 = PushButton("整理目录", self)
        self.button3.clicked.connect(self.button3Clicked)
        self.button3.setNewToolTip("自定义需要整理的文件夹（填写文件夹完整路径）")

        self.button4 = PushButton("整理文件类型", self)
        self.button4.clicked.connect(self.button4Clicked)
        self.button4.setNewToolTip("自定义整理文件类型")

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button3, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button4, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        self.nameBlacklistMessageBox = NameBlacklistEditMessageBox(self.window())
        self.nameBlacklistMessageBox.show()

    def button2Clicked(self):
        self.pathBlacklistMessageBox = PathBlacklistEditMessageBox(self.window())
        self.pathBlacklistMessageBox.show()

    def button3Clicked(self):
        self.sortFolderEditMessageBox = SortFolderEditMessageBox(self.window())
        self.sortFolderEditMessageBox.show()

    def button4Clicked(self):
        self.sortFormatEditMessageBox = SortFormatEditMessageBox(self.window())
        self.sortFormatEditMessageBox.show()


class FeaturesSettingCard(SettingCard):
    """
    功能设置卡片
    """

    def __init__(self, parent=None):

        super().__init__(FIF.DEVELOPER_TOOLS, "功能", "", parent)
        self.checkBox1 = CheckBox("整理微信", self)
        self.checkBox1.clicked.connect(lambda: setting.save("sortWechat", self.checkBox1.isChecked()))
        self.checkBox1.setNewToolTip("是否整理微信下载文件")

        self.checkBox3 = CheckBox("清理文件", self)
        self.checkBox3.clicked.connect(lambda: setting.save("clearFile", self.checkBox3.isChecked()))
        self.checkBox3.setNewToolTip("是否删除整理过程中发现的重复文件和空文件，该功能较耗费时间")

        self.checkBox4 = CheckBox("清理回收站", self)
        self.checkBox4.clicked.connect(lambda: setting.save("clearTrash", self.checkBox4.isChecked()))
        self.checkBox4.setNewToolTip("是否清空回收站文件，删除后文件将不可恢复")

        self.checkBox5 = CheckBox("删除至回收站", self)
        self.checkBox5.clicked.connect(lambda: setting.save("deleteToTrash", self.checkBox5.isChecked()))
        self.checkBox5.setNewToolTip("是否将整理过程中的无用文件删除至回收站而非直接删除")

        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox4, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox5, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.set()
        setting.signalConnect(self.setEvent)

    def setEvent(self, msg):
        if msg in ["sortWechat", "clearFile", "clearTrash", "deleteToTrash"]:
            self.set()

    def set(self):
        self.checkBox1.setChecked(setting.read("sortWechat"))
        self.checkBox3.setChecked(setting.read("clearFile"))
        self.checkBox4.setChecked(setting.read("clearTrash"))
        self.checkBox5.setChecked(setting.read("deleteToTrash"))

    def button1Clicked(self):
        if self.checkBox1.isChecked():
            self.checkBox5.setEnabled(True)
        else:
            self.checkBox5.setEnabled(False)

    def button2Clicked(self):
        setting.save("autoHide", self.checkBox5.isChecked())


class AddonPage(zbw.BasicTab):
    """
    插件主页面
    """
    restartExplorerSignal = pyqtSignal(bool)
    sortFileSignal = pyqtSignal(bool)
    signalBool = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.ZIP_FOLDER)
        self.setTitle("文件整理")

        self.button1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.button1_1.clicked.connect(self.button1_1Clicked)
        self.button1_1.setNewToolTip("开始整理+清理文件，范围包括：\n  整理指定目录文件\n  整理微信文件\n  清空回收站\n  清理系统缓存")

        self.button1_2 = ToolButton(FIF.FOLDER, self)
        self.button1_2.clicked.connect(lambda: zb.showFile(setting.read("sortGoalPath")))
        self.button1_2.setNewToolTip("打开整理文件所在目录")

        self.button2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.button2_1.clicked.connect(self.button2_1Clicked)
        self.button2_1.setNewToolTip("重启文件资源管理器")

        self.card1 = zbw.GrayCard("文件整理", self.view)
        self.card1.addWidget(self.button1_1)
        self.card1.addWidget(self.button1_2)

        self.card2 = zbw.GrayCard("快捷功能", self.view)
        self.card2.addWidget(self.button2_1)

        self.sortPathSettingCard = SortPathSettingCard(self)
        self.sortSettingCard = SortSettingCard(self)
        self.featuresSettingCard = FeaturesSettingCard(self)

        self.cardGroup1 = zbw.CardGroup("设置", self)
        self.cardGroup1.addCard(self.sortPathSettingCard, "sortPathSettingCard")
        self.cardGroup1.addCard(self.sortSettingCard, "sortSettingCard")
        self.cardGroup1.addCard(self.featuresSettingCard, "featuresSettingCard")

        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)

        self.trayMenu = self.window().tray.menu
        self.trayAction = Action(FIF.ALIGNMENT, "整理", triggered=self.action2Clicked)
        self.trayMenu.insertAction(self.window().tray.action2, self.trayAction)
        self.signalBool.connect(self.trayEvent)

        self.restartExplorerSignal.connect(self.restartExplorerFinished)
        self.sortFileSignal.connect(self.threadEvent1)

    def deleteLater(self):
        self.trayMenu.removeAction(self.trayAction)
        super().deleteLater()

    def action2Clicked(self):
        self.trayAction.setEnabled(False)
        self.button1_1.click()

    def trayEvent(self, msg):
        self.trayAction.setEnabled(msg)

    def button1_1Clicked(self):
        if not setting.read("sortGoalPath"):
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前未设置整理文件目标目录，无法整理！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()
            return
        if setting.read("sortWechat") and not setting.read("wechatPath"):
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "当前未设置微信文件目录，无法整理微信文件！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.button1_1.setEnabled(False)
        self.signalBool.emit(False)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "整理", "正在整理中，请耐心等待！", Qt.Orientation.Vertical, False, -1, InfoBarPosition.TOP_RIGHT, self)
        self.infoBar.show()

        program.THREAD_POOL.submit(self.sortFile)

    def sortFile(self):
        try:
            zb.createDir(setting.read("sortGoalPath"))
            if setting.read("clearTrash"):
                program.THREAD_POOL.submit(sf.clearTrash)
            for i in setting.read("sortFolder"):
                if zb.isDir(i):
                    if not (sf.belongDir(i, setting.read("sortGoalPath")) or sf.belongDir(setting.read("sortGoalPath"), i)):
                        sf.sortDir(i, setting.read("sortGoalPath"))
            if setting.read("wechatPath") and setting.read("sortWechat"):
                sf.sortWechatFiles()
            if setting.read("clearFile"):
                for i in list(setting.read("sortFormat").keys()) + ["文件夹"]:
                    sf.clearFile(zb.joinPath(setting.read("sortGoalPath"), i))
                sf.clearFile(setting.read("sortGoalPath"))
            self.sortFileSignal.emit(True)
            logging.debug("一键整理成功")
        except Exception as ex:
            self.sortFileSignal.emit(False)
            logging.warning(f"一键整理失败，报错信息：{ex}！")

    def threadEvent1(self, msg):
        self.button1_1.setEnabled(True)
        self.signalBool.emit(True)
        self.infoBar.closeButton.click()
        if msg:
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "整理", "整理成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()
        else:
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "整理", "整理失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

    def button2_1Clicked(self):
        self.button2_1.setEnabled(False)
        program.THREAD_POOL.submit(self.restartExplorer)

    def restartExplorer(self):
        zb.easyCmd("taskkill /f /im explorer.exe", True)
        self.restartExplorerSignal.emit(True)
        zb.easyCmd("start C:/windows/explorer.exe", True)

    def restartExplorerFinished(self, msg):
        self.button2_1.setEnabled(True)
