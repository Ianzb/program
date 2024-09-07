import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.widget.custom import *

try:
    from program.source.widget.custom import *
except:
    pass

setting.adds({"sortGoalPath": "",
              "wechatPath": "",
              "sortNameBlacklist": [],
              "sortPathBlacklist": [],
              "sortFolder": [program.DESKTOP_PATH],
              "sortFormat": {"PPT": [".ppt", ".pptx"],
                             "文档": [".doc", ".docx", ".txt", ".pdf"],
                             "表格": [".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".csv"],
                             "图片": [".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tga", ".bmp", ".dds", ".svg", ".eps", ".hdr", ".raw", ".exr", ".psd"],
                             "音频": [".mp3", ".wav", ".ogg", ".wma", ".ape", ".flac", ".aac"],
                             "视频": [".mp4", ".flv", ".mov", ".avi", ".mkv", ".wmv"],
                             "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
                             "镜像": [".iso", ".img", ".bin"],
                             "安装包": [".exe", ".msi"]
                             },
              "sortWechat": True,
              "clearCache": True,
              "clearFile": True,
              "clearTrash": False,
              "deleteToTrash": False,
              })


class SortFunctions:
    def clearEmptyFile(self, path: str):
        """
        删除空文件
        @param path: 文件夹路径
        """
        if f.isDir(path):
            paths = f.walkFile(path, 1)
            if paths:
                for i in paths:
                    if f.getSize(i) == 0:
                        f.delete(i, setting.read("deleteToTrash"))

    def clearEmptyDir(self, path):
        """
        删除空文件夹
        @param path: 文件夹路径
        """
        if f.isDir(path):
            paths = f.walkDir(path, 1)
            if paths:
                for i in paths:
                    try:
                        os.rmdir(i)
                    except:
                        pass

    def clearRepeatFile(self, path: str):
        """
        清理重复文件
        @param path: 文件夹路径
        """
        if f.isDir(path):
            sizes = []
            names = f.walkFile(path)
            if not names:
                return
            names.sort(key=lambda i: len(i))
            for i in names:
                if f.getSize(i) / 1024 / 1024 >= 128:
                    continue
                md5 = f.getMD5(i)
                if md5 in sizes:
                    f.delete(i, setting.read("deleteToTrash"))
                else:
                    sizes.append(md5)

    def clearFile(self, path: str):
        """
        清理文件夹3合1
        @param path: 文件夹路径
        """
        try:
            self.clearEmptyFile(path)
            self.clearEmptyDir(path)
            self.clearRepeatFile(path)
            logging.debug(f"成功清理{path}文件夹")
        except Exception as ex:
            logging.warning(f"无法清理{path}文件夹{ex}")

    def belongDir(self, path: str, parent: str) -> bool:
        """
        文件夹是否包含
        @param path: 子文件夹
        @param parent: 母文件夹
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
        @param old: 旧文件夹路径
        @param new: 新文件夹路径
        @param mode: 模式：0 全部整理 1 仅文件 2 仅文件夹
        """

        try:
            blacklist = [self.getSortNameBlacklist(), self.getSortPathBlacklist()]
            if mode in [0, 1]:
                file_list = f.walkFile(old, 1)
                if file_list:
                    for i in file_list:
                        if i.startwith("~$"): continue  # 跳过office临时文件
                        for j in range(len(setting.read("sortFormat").values())):
                            if f.splitPath(i, 2).lower() in list(setting.read("sortFormat").values())[j]:
                                if f.splitPath(i, 0) in blacklist[0] or i in blacklist[1]:
                                    continue
                                f.moveFile(i, f.pathJoin(new, list(setting.read("sortFormat").keys())[j]))
            if mode in [0, 2]:
                file_list = f.walkDir(old, 1)
                if file_list:
                    for i in file_list:
                        if f.splitPath(i, 0) in blacklist[0] or i in blacklist[1]:
                            continue
                        f.moveFile(i, f.pathJoin(new, "文件夹", f.splitPath(i, 0)))
            logging.debug(f"成功整理{old}文件夹")
        except Exception as ex:
            logging.warning(f"无法整理{old}文件夹{ex}")

    def sortWechatFiles(self):
        """
        整理微信文件
        """
        try:
            list1 = []
            list2 = []
            for i in f.walkDir(setting.read("wechatPath"), 1):
                if f.existPath(f.pathJoin(i, "FileStorage/File")):
                    list1.append(f.pathJoin(i, "FileStorage/File"))
            for i in list1:
                if f.walkDir(i, 1) == None:
                    return
                list2 = list2 + f.walkDir(i, 1)
            for i in list2:
                self.sortDir(i, setting.read("sortGoalPath"))
            for i in list1:
                self.sortDir(i, setting.read("sortGoalPath"), 1)
            logging.debug("成功整理微信文件")
        except Exception as ex:
            logging.warning(f"无法整理微信文件{ex}")

    def clearSystemCache(self):
        """
        清理系统缓存
        """
        try:
            f.clearDir(os.getenv("TEMP"))
        except:
            pass

    def clearTrash(self):
        """
        清空回收站
        """
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            logging.debug("成功清空回收站")
        except Exception as ex:
            logging.warning(f"无法清空回收站{ex}")

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
        if f.isSameFile(setting.read("sortGoalPath"), program.DESKTOP_PATH):
            data += [f.pathJoin(program.DESKTOP_PATH, i) for i in list(setting.read("sortFormat").keys()) + ["文件夹"]]
        elif self.belongDir(setting.read("sortGoalPath"), program.DESKTOP_PATH):
            for i in f.walkDir(program.DESKTOP_PATH, 1):
                if self.belongDir(setting.read("sortGoalPath"), i):
                    data.append(i)
        return list(set(data))


sf = SortFunctions()


class AddonThread(QThread, SignalBase):
    """
    多线程模块
    """

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data

    def run(self):
        logging.info(f"文件整理插件 {self.mode} 线程开始")
        if self.mode == "一键整理+清理":
            try:
                f.makeDir(setting.read("sortGoalPath"))
                if setting.read("clearTrash"):
                    EasyThread(sf.clearTrash)
                if setting.read("clearCache"):
                    EasyThread(sf.clearSystemCache)
                if setting.read("wechatPath") and setting.read("sortWechat"):
                    sf.sortWechatFiles()
                for i in setting.read("sortFolder"):
                    if f.isDir(i):
                        if not (sf.belongDir(i, setting.read("sortGoalPath")) or sf.belongDir(setting.read("sortGoalPath"), i)):
                            sf.sortDir(i, setting.read("sortGoalPath"))
                if setting.read("clearFile"):
                    for i in list(setting.read("sortFormat").keys()) + ["文件夹"]:
                        sf.clearFile(f.pathJoin(setting.read("sortGoalPath"), i))
                    sf.clearFile(setting.read("sortGoalPath"))
                self.signalBool.emit(True)
                logging.debug("一键整理成功")
            except Exception as ex:
                self.signalBool.emit(False)
                logging.warning("一键整理失败")
        elif self.mode == "重启文件资源管理器":
            f.cmd("taskkill /f /im explorer.exe", True)
            self.signalStr.emit("完成")
            f.cmd("start C:/windows/explorer.exe", True)
            logging.debug("重启文件资源管理器")
        logging.info(f"文件整理插件 {self.mode} 线程结束")


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
        self.textEdit.setToolTip("输入文件名称\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortNameBlacklist", sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText()).split("\n") if i]))))

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
        self.textEdit.setToolTip("输入文件完整路径\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

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
        setting.save("sortPathBlacklist", sorted(list(set([f.formatPath(i.strip()) for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))))

        self.accept()
        self.accepted.emit()

    def addFolderButtonClicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择黑名单文件夹", "C:/")
        if f.existPath(get):
            get = f.formatPath(get)
            if get not in sorted(list(set([f.formatPath(i.strip()) for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))):
                self.textEdit.setText((self.textEdit.toPlainText().strip() + "\n" + get).strip())

    def addFileButtonClicked(self):
        get = QFileDialog.getOpenFileName(self, "选择黑名单文件", "C:/")[0]
        if f.existPath(get):
            get = f.formatPath(get)
            if get not in sorted(list(set([f.formatPath(i.strip()) for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))):
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
        self.textEdit.setToolTip("输入文件夹完整路径\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

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
        setting.save("sortFolder", sorted(list(set([f.formatPath(i.strip()) for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))))
        self.accept()
        self.accepted.emit()

    def addButtonClicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择整理文件夹", "C:/")
        if f.existPath(get):
            get = f.formatPath(get)
            if get not in sorted(list(set([f.formatPath(i.strip()) for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))):
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

        self.tableView.setToolTip("后缀名逗号（中英文均可）分割，加不加分割点均可")
        self.tableView.installEventFilter(ToolTipFilter(self.tableView, 1000))

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
        self.button1.setToolTip("设置整理目标目录")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("微信目录", self, FIF.FOLDER_ADD)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("设置微信WeChat Files文件夹目录")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setAcceptDrops(True)

    def button1Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择整理目标目录", setting.read("sortGoalPath"))
        self.saveSetting(get)

    def button2Clicked(self):
        get = QFileDialog.getExistingDirectory(self, "选择微信WeChat Files文件夹目录", setting.read("wechatPath"))
        if get:
            if "WeChat Files" != f.splitPath(get):
                return
        self.saveSetting(get)

    def saveSetting(self, path: str):
        if f.existPath(path):
            if "WeChat Files" == f.splitPath(path):
                setting.save("wechatPath", path)
            else:
                setting.save("sortGoalPath", path)
        self.contentLabel.setText(f"整理目标路径：{setting.read("sortGoalPath")}\n微信路径：{setting.read("wechatPath")}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if f.isDir(event.mimeData().urls()[0].toLocalFile()):
                    event.acceptProposedAction()
                    self.contentLabel.setText("拖拽到此卡片即可快速导入目录！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"整理目标路径：{setting.read("sortGoalPath")}\n微信路径：{setting.read("wechatPath")}")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            self.saveSetting(file)


class SortSettingCard(SettingCard):
    """
    整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.EDIT, "目录", "", parent)
        self.button1 = PushButton("整理文件名称黑名单", self)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("编辑整理文件名称黑名单（填写文件名）")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("整理文件路径黑名单", self)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("编辑整理文件路径黑名单（填写文件完整路径）")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.button3 = PushButton("整理目录", self)
        self.button3.clicked.connect(self.button3Clicked)
        self.button3.setToolTip("自定义需要整理的文件夹（填写文件夹完整路径）")
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.button4 = PushButton("整理文件类型", self)
        self.button4.clicked.connect(self.button4Clicked)
        self.button4.setToolTip("自定义整理文件类型")
        self.button4.installEventFilter(ToolTipFilter(self.button4, 1000))

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
        self.checkBox1.setChecked(setting.read("sortWechat"))
        self.checkBox1.clicked.connect(lambda: setting.save("sortWechat", self.checkBox1.isChecked()))
        self.checkBox1.setToolTip("是否整理微信下载文件")
        self.checkBox1.installEventFilter(ToolTipFilter(self.checkBox1, 1000))

        self.checkBox2 = CheckBox("清理缓存", self)
        self.checkBox2.setChecked(setting.read("clearCache"))
        self.checkBox2.clicked.connect(lambda: setting.save("clearCache", self.checkBox2.isChecked()))
        self.checkBox2.setToolTip("是否清理电脑缓存（可能会影响部分运行中软件）")
        self.checkBox2.installEventFilter(ToolTipFilter(self.checkBox2, 1000))
        self.checkBox2.setEnabled(f.checkStartup())

        self.checkBox3 = CheckBox("清理文件", self)
        self.checkBox3.setChecked(setting.read("clearFile"))
        self.checkBox3.clicked.connect(lambda: setting.save("clearFile", self.checkBox3.isChecked()))
        self.checkBox3.setToolTip("是否删除整理过程中发现的重复文件和空文件，该功能较耗费时间")
        self.checkBox3.installEventFilter(ToolTipFilter(self.checkBox3, 1000))
        self.checkBox3.setEnabled(f.checkStartup())

        self.checkBox4 = CheckBox("清理回收站", self)
        self.checkBox4.setChecked(setting.read("clearTrash"))
        self.checkBox4.clicked.connect(lambda: setting.save("clearTrash", self.checkBox4.isChecked()))
        self.checkBox4.setToolTip("是否清空回收站文件，删除后文件将不可恢复")
        self.checkBox4.installEventFilter(ToolTipFilter(self.checkBox4, 1000))
        self.checkBox4.setEnabled(f.checkStartup())

        self.checkBox5 = CheckBox("删除至回收站", self)
        self.checkBox5.setChecked(setting.read("deleteToTrash"))
        self.checkBox5.clicked.connect(lambda: setting.save("deleteToTrash", self.checkBox5.isChecked()))
        self.checkBox5.setToolTip("是否将整理过程中的无用文件删除至回收站而非直接删除")
        self.checkBox5.installEventFilter(ToolTipFilter(self.checkBox5, 1000))
        self.checkBox5.setEnabled(f.checkStartup())

        self.hBoxLayout.addWidget(self.checkBox1, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox2, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox4, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.checkBox5, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        if self.checkBox1.isChecked():
            self.checkBox5.setEnabled(True)
        else:
            self.checkBox5.setEnabled(False)

    def button2Clicked(self):
        setting.save("autoHide", self.checkBox5.isChecked())


class AddonPage(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.ZIP_FOLDER)
        self.button1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.button1_1.clicked.connect(self.button1_1Clicked)
        self.button1_1.setToolTip("开始整理+清理文件，范围包括：\n  整理指定目录文件\n  整理微信文件\n  清空回收站\n  清理系统缓存")
        self.button1_1.installEventFilter(ToolTipFilter(self.button1_1, 1000))

        self.button1_2 = ToolButton(FIF.FOLDER, self)
        self.button1_2.clicked.connect(lambda: f.showFile(setting.read("sortGoalPath")))
        self.button1_2.setToolTip("打开整理文件所在目录")
        self.button1_2.installEventFilter(ToolTipFilter(self.button1_2, 1000))

        self.button2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.button2_1.clicked.connect(self.button2_1Clicked)
        self.button2_1.setToolTip("重启文件资源管理器")
        self.button2_1.installEventFilter(ToolTipFilter(self.button2_1, 1000))

        self.card1 = GrayCard("文件整理", self.view)
        self.card1.addWidget(self.button1_1)
        self.card1.addWidget(self.button1_2)

        self.card2 = GrayCard("快捷功能", self.view)
        self.card2.addWidget(self.button2_1)

        self.sortPathSettingCard = SortPathSettingCard(self)
        self.sortSettingCard = SortSettingCard(self)
        self.featuresSettingCard = FeaturesSettingCard(self)

        self.cardGroup1 = CardGroup("设置", self)
        self.cardGroup1.addWidget(self.sortPathSettingCard)
        self.cardGroup1.addWidget(self.sortSettingCard)
        self.cardGroup1.addWidget(self.featuresSettingCard)

        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)

        self.trayMenu = self.parent().tray.menu
        self.trayAction = Action(FIF.ALIGNMENT, "整理", triggered=self.action2Clicked)
        self.trayMenu.insertAction(self.parent().tray.action2, self.trayAction)
        self.signalBool.connect(self.trayEvent)

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

        self.thread1 = AddonThread("一键整理+清理")
        self.thread1.signalBool.connect(self.threadEvent1)
        self.thread1.start()

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

        self.thread2 = AddonThread("重启文件资源管理器")
        self.thread2.signalStr.connect(self.threadEvent2)
        self.thread2.start()

    def threadEvent2(self, msg):
        self.button2_1.setEnabled(True)
