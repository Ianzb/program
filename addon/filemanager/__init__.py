import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.custom import *

try:
    from program.source.custom import *
except:
    pass

setting.adds({"sortPath": "",
              "wechatPath": "",
              "sortBlacklist": [],
              "sortFolder": [],
              "sortFormat": {"PPT": [".ppt", ".pptx"],
                             "文档": [".doc", ".docx", ".txt", ".pdf"],
                             "表格": [".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".csv"],
                             "图片": [".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tga", ".bmp", ".dds", ".svg", ".eps", ".hdr", ".raw", ".exr", ".psd"],
                             "音频": [".mp3", ".wav", ".ogg", ".wma", ".ape", ".flac", ".aac"],
                             "视频": [".mp4", ".flv", ".mov", ".avi", ".mkv", ".wmv"],
                             "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
                             "镜像": [".iso", ".img", ".bin"],
                             "安装包": [".exe", ".msi"]
                             }

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
                        f.delete(i)

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
                    f.delete(i)
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
            if mode in [0, 1]:
                file_list = f.walkFile(old, 1)
                if file_list:
                    for i in file_list:
                        for j in range(len(setting.read("sortFormat").values())):
                            if f.splitPath(i, 2).lower() in list(setting.read("sortFormat").values())[j]:
                                if f.splitPath(i, 0) not in self.getSortBlacklist():
                                    f.moveFile(i, f.pathJoin(new, list(setting.read("sortFormat").keys())[j]))
            if mode in [0, 2]:
                file_list = f.walkDir(old, 1)
                if file_list:
                    for i in file_list:
                        if f.splitPath(i, 0) not in self.getSortBlacklist():
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
                self.sortDir(i, setting.read("sortPath"))
            for i in list1:
                self.sortDir(i, setting.read("sortPath"), 1)
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

    def clearRubbish(self):
        """
        清空回收站
        """
        import winshell
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            logging.debug("成功清空回收站")
        except Exception as ex:
            logging.warning(f"无法清空回收站{ex}")

    def getSortBlacklist(self):
        """
        获取整理文件黑名单
        @return: 整理文件黑名单列表
        """
        f.makeDir(setting.read("sortPath"))
        data = setting.read("sortBlacklist")

        if f.isSameFile(setting.read("sortPath"), program.DESKTOP_PATH):
            data += list(setting.read("sortFormat").keys()) + ["文件夹"]
        elif sf.belongDir(setting.read("sortPath"), program.DESKTOP_PATH):
            dirs = f.walkDir(program.DESKTOP_PATH, 1)
            for i in dirs:
                if sf.belongDir(setting.read("sortPath"), i):
                    data.append(f.splitPath(i))
        return data


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
                EasyThread(sf.clearRubbish)
                EasyThread(sf.clearSystemCache)
                sf.sortDir(program.DESKTOP_PATH, setting.read("sortPath"))
                if setting.read("wechatPath"):
                    sf.sortWechatFiles()
                for i in setting.read("sortFolder"):
                    if f.isDir(i):
                        if not (sf.belongDir(i, setting.read("sortPath")) or sf.belongDir(setting.read("sortPath"), i)):
                            sf.sortDir(i, setting.read("sortPath"))
                for i in list(setting.read("sortFormat").keys()) + ["文件夹"]:
                    sf.clearFile(f.pathJoin(setting.read("sortPath"), i))
                sf.clearFile(setting.read("sortPath"))
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


class BlackListEditMessageBox(MessageBoxBase):
    """
    可编辑黑名单的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("整理文件黑名单", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件名称\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortBlacklist")))
        self.textEdit.setToolTip("输入文件名称\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortBlacklist", sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText()).split("\n") if i]))))

        self.accept()
        self.accepted.emit()


class SortFolderEditMessageBox(MessageBoxBase):
    """
    可编辑整理目录的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("自定义整理目录", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入文件夹完整路径\n一行一个")
        self.textEdit.setText("\n".join(setting.read("sortFolder")))
        self.textEdit.setToolTip("输入文件夹完整路径\n一行一个")
        self.textEdit.installEventFilter(ToolTipFilter(self.textEdit, 1000))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.addButton = PushButton("选择目录", self.buttonGroup)
        self.addButton.clicked.connect(self.addButtonClicked)
        self.buttonLayout.insertWidget(1, self.addButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("sortFolder", sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))))

        self.accept()
        self.accepted.emit()

    def addButtonClicked(self):
        get = QFileDialog.getExistingDirectory(self, "添加整理目录", "C:/")
        if f.existPath(get):
            if get not in sorted(list(set([i.strip() for i in f.removeIllegalPath(self.textEdit.toPlainText(), 1).split("\n") if i]))):
                self.textEdit.setText((self.textEdit.toPlainText().strip() + "\n" + get).strip())


class SortFormatEditMessageBox(MessageBoxBase):
    """
    可编辑整理文件类型的弹出框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("自定义整理文件类型", self)

        self.tableView = TableWidget(self)

        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)
        self.tableView.setColumnCount(2)

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(["类型", "后缀名"])
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.tableView.setToolTip("后缀名逗号（中英文均可）分割，加不加.均可")
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
        super().__init__(FIF.ALIGNMENT, "整理文件", f"整理目标路径：{setting.read("sortPath")}\n微信路径：{setting.read("wechatPath")}", parent)
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
        get = QFileDialog.getExistingDirectory(self, "选择整理目标目录", setting.read("sortPath"))
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
                setting.save("sortPath", path)
        self.contentLabel.setText(f"整理目标路径：{setting.read("sortPath")}\n微信路径：{setting.read("wechatPath")}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                if f.isDir(event.mimeData().urls()[0].toLocalFile()):
                    event.acceptProposedAction()
                    self.contentLabel.setText("拖拽到此卡片即可快速导入目录！")

    def dragLeaveEvent(self, event):
        self.contentLabel.setText(f"整理目标路径：{setting.read("sortPath")}\n微信路径：{setting.read("wechatPath")}")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file = event.mimeData().urls()[0].toLocalFile()
            self.saveSetting(file)


class SortSettingCard(SettingCard):
    """
    自定义整理文件设置卡片
    """

    def __init__(self, parent=None):
        super().__init__(FIF.EDIT, "自定义整理文件", "", parent)
        self.button1 = PushButton("整理文件黑名单", self)
        self.button1.clicked.connect(self.button1Clicked)
        self.button1.setToolTip("编辑整理文件黑名单（填写文件名）")
        self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))

        self.button2 = PushButton("自定义整理目录", self)
        self.button2.clicked.connect(self.button2Clicked)
        self.button2.setToolTip("自定义整理文件夹（填写文件夹完整路径）")
        self.button2.installEventFilter(ToolTipFilter(self.button2, 1000))

        self.button3 = PushButton("自定义整理文件类型", self)
        self.button3.clicked.connect(self.button3Clicked)
        self.button3.setToolTip("自定义整理文件类型")
        self.button3.installEventFilter(ToolTipFilter(self.button3, 1000))

        self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.button3, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def button1Clicked(self):
        self.blackListMessageBox = BlackListEditMessageBox(self.parent().parent().parent().parent().parent().parent().parent())
        self.blackListMessageBox.show()

    def button2Clicked(self):
        self.blackListMessageBox = SortFolderEditMessageBox(self.parent().parent().parent().parent().parent().parent().parent())
        self.blackListMessageBox.show()

    def button3Clicked(self):
        self.sortFormatMessageBox = SortFormatEditMessageBox(self.parent().parent().parent().parent().parent().parent().parent())
        self.sortFormatMessageBox.show()


class AddonPage(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.ZIP_FOLDER)
        self.button1_1 = PrimaryPushButton("开始整理+清理", self, FIF.ALIGNMENT)
        self.button1_1.clicked.connect(self.button1_1Clicked)
        self.button1_1.setToolTip("开始整理+清理文件，范围包括：\n  整理桌面文件\n  整理微信文件\n  清空回收站\n  清理系统缓存")
        self.button1_1.installEventFilter(ToolTipFilter(self.button1_1, 1000))

        self.button1_2 = ToolButton(FIF.FOLDER, self)
        self.button1_2.clicked.connect(lambda: f.showFile(setting.read("sortPath")))
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

        self.sortSettingCard = SortPathSettingCard(self)
        self.sortFolderSettingCard = SortSettingCard(self)

        self.cardGroup1 = CardGroup("设置", self)
        self.cardGroup1.addWidget(self.sortSettingCard)
        self.cardGroup1.addWidget(self.sortFolderSettingCard)

        self.vBoxLayout.addWidget(self.card1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)

        self.trayAction = Action(FIF.ALIGNMENT, "整理", triggered=self.action2Clicked)
        self.parent().tray.menu.insertAction(self.parent().tray.action2, self.trayAction)
        self.signalBool.connect(self.trayEventt)

    def action2Clicked(self):
        self.trayAction.setEnabled(False)
        self.button1_1.click()

    def trayEventt(self, msg):
        self.trayAction.setEnabled(msg)

    def button1_1Clicked(self):
        if setting.read("sortPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "当前未设置整理文件目录，无法整理！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()
            return
        if setting.read("wechatPath") == "":
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", "当前未设置微信文件目录，无法整理微信文件！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self)
            self.infoBar.show()

        self.button1_1.setEnabled(False)

        self.signalBool.emit(False)

        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()

        self.thread1 = AddonThread("一键整理+清理")
        self.thread1.signalBool.connect(self.threadEvent1)
        self.thread1.start()

    def threadEvent1(self, msg):
        self.stateTooltip.setState(True)
        self.button1_1.setEnabled(True)
        self.signalBool.emit(True)
        if msg:
            self.stateTooltip.setContent("整理成功")
        else:
            self.stateTooltip.setContent("整理失败")

    def button2_1Clicked(self):
        self.button2_1.setEnabled(False)

        self.thread2 = AddonThread("重启文件资源管理器")
        self.thread2.signalStr.connect(self.threadEvent2)
        self.thread2.start()

    def threadEvent2(self, msg):
        self.button2_1.setEnabled(True)
