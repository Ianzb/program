from ..program import *
import webbrowser

class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, window):
        super(Tray, self).__init__(QIcon(program.ICON))
        self.window = window

        self.setIcon(QIcon(program.ICON))
        self.setToolTip(program.TITLE)
        self.activated.connect(self.iconClicked)

        self.action1 = Action(FIF.HOME, "打开", triggered=self.window.show)
        self.action2 = Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program.URL))
        self.action3 = Action(FIF.SYNC, "重启", triggered=program.restart)
        self.action4 = Action(FIF.CLOSE, "退出", triggered=program.close)

        self.menu = AcrylicMenu()

        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

    def showTrayMessage(self, title, msg):
        super().showMessage(title, msg, QIcon(program.ICON))

    def iconClicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
            self.contextMenuEvent()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick or QSystemTrayIcon.ActivationReason.MiddleClick:
            self.trayClickedEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == Qt.WindowState.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), aniType=MenuAnimationType.PULL_UP)
        self.menu.show()

#
# class AddonEditMessageBox(MessageBoxBase):
#     """
#     可编辑插件的弹出框
#     """
#
#     def __init__(self, title: str, parent=None):
#         super().__init__(parent)
#         self.titleLabel = SubtitleLabel(title, self)
#
#         self.tableView = TableWidget(self)
#
#         self.tableView.setBorderVisible(True)
#         self.tableView.setBorderRadius(8)
#         self.tableView.setWordWrap(False)
#         self.tableView.setColumnCount(4)
#         self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
#
#         self.tableView.verticalHeader().hide()
#         self.tableView.setHorizontalHeaderLabels(["ID", "名称", "本地版本号", "在线版本号"])
#         self.tableView.resizeColumnsToContents()
#         self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
#
#         self.viewLayout.addWidget(self.titleLabel)
#         self.viewLayout.addWidget(self.tableView, 0, Qt.AlignTop)
#
#         self.yesButton.setText("安装选中")
#         self.yesButton.clicked.connect(self.yesButtonClicked)
#
#         self.removeButton = PrimaryPushButton("删除选中", self.buttonGroup)
#         self.removeButton.clicked.connect(self.removeButtonClicked)
#         self.buttonLayout.insertWidget(1, self.removeButton, 1, Qt.AlignVCenter)
#
#         self.cancelButton.setText("取消")
#
#         self.yesButton.setEnabled(False)
#         self.removeButton.setEnabled(False)
#
#         self.widget.setMinimumWidth(600)
#
#         self.installed = getInstalledAddonInfo()
#         self.tableView.setRowCount(len(self.installed.values()))
#         for i in range(len(self.installed.values())):
#             names = sorted(self.installed.keys())
#
#             self.tableView.setItem(i, 0, QTableWidgetItem(self.installed[names[i]]["id"]))
#             self.tableView.setItem(i, 1, QTableWidgetItem(self.installed[names[i]]["path"]))
#             self.tableView.setItem(i, 2, QTableWidgetItem(self.installed[names[i]]["version"]))
#             self.tableView.setItem(i, 3, QTableWidgetItem("加载中..."))
#
#         self.thread1 = CustomThread("云端插件信息")
#         self.thread1.signalDict.connect(self.threadEvent1_1)
#         self.thread1.signalBool.connect(self.threadEvent1_2)
#         self.thread1.signalStr.connect(self.threadEvent1_3)
#         self.thread1.start()
#
#     def yesButtonClicked(self):
#         self.parent().mainPage.addonSettingCard.button1.setEnabled(False)
#         self.parent().mainPage.addonSettingCard.button2.setEnabled(False)
#         self.parent().mainPage.addonSettingCard.progressBarLoading.show()
#
#         list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[::4]]
#         self.thread2 = CustomThread("下载插件", list)
#         self.thread2.signalDict.connect(self.threadEvent2_1)
#         self.thread2.signalBool.connect(self.threadEvent2_2)
#         self.thread2.start()
#
#     def removeButtonClicked(self):
#         self.parent().mainPage.addonSettingCard.button1.setEnabled(False)
#         self.parent().mainPage.addonSettingCard.button2.setEnabled(False)
#         self.parent().mainPage.addonSettingCard.progressBarLoading.show()
#
#         id_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[::4]]
#         name_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[1::4]]
#         installed_version_list = [self.tableView.itemFromIndex(i).text() for i in self.tableView.selectedIndexes()[2::4]]
#         for i in range(len(id_list)):
#             if installed_version_list[i] != "未安装":
#                 self.parent().removeAddon({"id": id_list[i], "path": name_list[i]})
#
#         self.accept()
#         self.accepted.emit()
#         self.parent().mainPage.addonSettingCard.button1.setEnabled(True)
#         self.parent().mainPage.addonSettingCard.button2.setEnabled(True)
#         self.parent().mainPage.addonSettingCard.progressBarLoading.hide()
#
#     def threadEvent1_1(self, msg):
#         if msg["id"] in self.installed.keys():
#             i = self.tableView.findItems(msg["id"], Qt.MatchFlag.MatchExactly)[0].row()
#             self.tableView.setItem(i, 3, QTableWidgetItem(msg["version"]))
#         else:
#             self.tableView.hide()
#             self.tableView.setRowCount(self.tableView.rowCount() + 1)
#             i = self.tableView.rowCount() - 1
#             self.tableView.setItem(i, 0, QTableWidgetItem(msg["id"]))
#             self.tableView.setItem(i, 1, QTableWidgetItem(msg["path"]))
#             self.tableView.setItem(i, 2, QTableWidgetItem("未安装"))
#             self.tableView.setItem(i, 3, QTableWidgetItem(msg["version"]))
#             self.tableView.show()
#
#     def threadEvent1_2(self, msg):
#         if msg:
#             for i in range(self.tableView.rowCount()):
#                 if self.tableView.item(i, 3).text() == "加载中...":
#                     self.tableView.setItem(i, 3, QTableWidgetItem("云端无数据"))
#         else:
#             self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", "无网络连接！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
#             self.infoBar.show()
#             for i in range(self.tableView.rowCount()):
#                 self.tableView.setItem(i, 3, QTableWidgetItem("无网络连接"))
#             self.yesButton.setEnabled(False)
#             self.removeButton.setEnabled(True)
#             self.titleLabel.setText("管理插件（无网络连接）")
#             return
#         self.titleLabel.setText("管理插件")
#         self.yesButton.setEnabled(True)
#         self.removeButton.setEnabled(True)
#
#     def threadEvent1_3(self, msg):
#         i = self.tableView.findItems(msg["id"], Qt.MatchFlag.MatchExactly)[0].row()
#         self.tableView.setItem(i, 2, QTableWidgetItem("连接失败"))
#
#     def threadEvent2_1(self, msg):
#         self.parent().addAddon(msg)
#
#     def threadEvent2_2(self, msg):
#         if not msg:
#             self.infoBar = InfoBar(InfoBarIcon.WARNING, "提示", f"无网络连接，插件下载失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.window().mainPage)
#             self.infoBar.show()
#         self.parent().mainPage.addonSettingCard.button1.setEnabled(True)
#         self.parent().mainPage.addonSettingCard.button2.setEnabled(True)
#         self.parent().mainPage.addonSettingCard.progressBarLoading.hide()
#
#
# class AddonSettingCard(SettingCard):
#     """
#     插件设置卡片
#     """
#
#     def __init__(self, parent=None):
#         super().__init__(FIF.ADD, "插件", f"管理{program.NAME}的插件", parent)
#
#         self.progressBarLoading = IndeterminateProgressBar(self)
#         self.progressBarLoading.setMaximumWidth(200)
#         self.progressBarLoading.hide()
#
#         self.button1 = PushButton("手动导入", self, FIF.ADD)
#         self.button1.clicked.connect(self.button1Clicked)
#         self.button1.setToolTip("手动导入程序插件")
#         self.button1.installEventFilter(ToolTipFilter(self.button1, 1000))
#
#         self.button2 = PushButton("管理", self, FIF.EDIT)
#         self.button2.clicked.connect(self.button2Clicked)
#         self.button2.setToolTip("管理程序插件")
#         self.button2.installEventFilter(ToolTipFilter(self.button1, 1000))
#
#         self.hBoxLayout.addWidget(self.progressBarLoading, Qt.AlignRight)
#         self.hBoxLayout.addSpacing(8)
#         self.hBoxLayout.addWidget(self.button1, 0, Qt.AlignRight)
#         self.hBoxLayout.addWidget(self.button2, 0, Qt.AlignRight)
#         self.hBoxLayout.addSpacing(16)
#
#         self.setAcceptDrops(True)
#
#     def button1Clicked(self):
#         get = QFileDialog.getOpenFileUrl(self, "选择插件文件", QUrl(""), "zb小程序插件 (*.zbaddon);;压缩包 (*.zip)")[0]
#         get = joinPath(get.path()[1:])
#         if get and get not in ["."]:
#             self.importAddon(get)
#
#     def button2Clicked(self):
#         self.addonEditMessageBox = AddonEditMessageBox("加载中...", self.window())
#         self.addonEditMessageBox.show()
#
#     def dragEnterEvent(self, event):
#         if event.mimeData().hasUrls():
#             if len(event.mimeData().urls()) == 1:
#                 if isFile(event.mimeData().urls()[0].toLocalFile()):
#                     if splitPath(event.mimeData().urls()[0].toLocalFile(), 2) in [".zbaddon", ".zip"]:
#                         event.acceptProposedAction()
#                         self.contentLabel.setText("拖拽到此卡片即可快速导入插件！")
#
#     def dragLeaveEvent(self, event):
#         self.contentLabel.setText(f"管理{program.NAME}的插件")
#
#     def dropEvent(self, event):
#         if event.mimeData().hasUrls():
#             file = event.mimeData().urls()[0].toLocalFile()
#             self.importAddon(file)
#
#     def importAddon(self, path: str):
#         if not existPath(path):
#             return
#         id = importAddon(path)
#         self.window().addAddon(id)
#
