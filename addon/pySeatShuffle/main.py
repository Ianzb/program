from .widget import *


class MainPage(QWidget):
    """
    主页
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.hBoxLayout = QHBoxLayout(self)

        self.shuffleInterface = ShuffleInterface(self)
        self.editInterface = EditInterface(self)
        self.tableInterface = TableInterface(self)

        self.rightVBoxLayout = QVBoxLayout(self)
        self.rightVBoxLayout.addWidget(self.shuffleInterface)
        self.rightVBoxLayout.addWidget(self.editInterface)
        self.hBoxLayout.addWidget(self.tableInterface, 2)
        self.hBoxLayout.addLayout(self.rightVBoxLayout, 0)

        self.setLayout(self.hBoxLayout)


class TableInterface(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.listWidget = ListWidget(self)
        self.listWidget.setContentsMargins(0, 0, 0, 0)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.listWidget)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.setTitle("预览区")

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.viewLayout.addLayout(self.gridLayout)

        self.closeButton = ToolButton(FIF.CLOSE, self)
        self.closeButton.setNewToolTip("关闭当前表格")
        self.closeButton.clicked.connect(self.clearTable)
        self.closeButton.hide()

        self.headerLayout.addWidget(self.closeButton, 0, Qt.AlignRight)

        self.tableChooser = zbw.FileChooser(self)
        self.tableChooser.setSuffix({"表格文件": [".xlsx", ".xls", ".json"]})
        self.tableChooser.setOnlyOne(True)
        self.tableChooser.setDefaultPath(setting.read("downloadPath"))
        self.tableChooser.setDescription("座位表")
        self.tableChooser.setFixedHeight(100)
        self.tableChooser.fileChoosedSignal.connect(self.importSeat)
        self.tableChooser.setFixedSize(200, 120)
        self.viewLayout.addWidget(self.tableChooser, Qt.AlignCenter)

        setting.signalConnect(self.settingChanged)

    def settingChanged(self, name):
        if name == "downloadPath":
            self.tableChooser.setDefaultPath(setting.read("downloadPath"))

    def clearTable(self):
        manager.removeTable()
        self.tableChooser.show()
        self.closeButton.hide()

    def importSeat(self, get):
        try:
            if not get or not get[0]:
                return
            if zb.getFileSuffix(get[0]) == ".xlsx":
                manager.setTable(manager.XLSX_PARSER.parse(get[0]))
            elif zb.getFileSuffix(get[0]) == ".json":
                manager.setTable(manager.JSON_PARSER.parse(get[0]))
            setting.save("downloadPath", zb.getFileDir(get[0]))
            logging.info(f"导入座位表格文件{get[0]}成功！")
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"导入座位表格文件{zb.getFileName(get[0])}成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().mainPage)
        except Exception:
            logging.error(f"导入座位表格文件{get[0]}失败，报错信息：{traceback.format_exc()}！")
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", f"导入座位表格文件{zb.getFileName(get[0])}失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().mainPage)
        infoBar.show()
        self.tableChooser.hide()
        self.closeButton.show()


class ShuffleInterface(HeaderCardWidget):
    shuffleSignal = pyqtSignal(tuple, core.Person)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(100)
        self.setMaximumWidth(250)
        self.setTitle("操作区")

        self.vBoxLayout2 = QVBoxLayout(self)
        self.vBoxLayout2.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(self.vBoxLayout2)

        self.hBoxLayout1 = QHBoxLayout(self)
        self.hBoxLayout1.setContentsMargins(0, 0, 0, 0)

        self.hBoxLayout2 = QHBoxLayout(self)
        self.hBoxLayout2.setContentsMargins(0, 0, 0, 0)

        self.shuffleButton = PushButton("自动排座", self, FIF.ADD)
        self.shuffleButton.clicked.connect(self.shuffleButtonClicked)

        self.clearButton = ToolButton(FIF.DELETE, self)
        self.clearButton.setNewToolTip("清空预览区所有人员")
        self.clearButton.clicked.connect(self.handleClearButtonClicked)

        self.exportButton = PushButton("导出", self, FIF.UP)
        self.exportButton.clicked.connect(self.export)

        self.hBoxLayout1.addWidget(self.shuffleButton, 2)
        self.hBoxLayout2.addWidget(self.exportButton, 2)
        self.hBoxLayout2.addWidget(self.clearButton, 0, Qt.AlignCenter)
        self.vBoxLayout2.addLayout(self.hBoxLayout1)
        self.vBoxLayout2.addLayout(self.hBoxLayout2)

        self.shuffleSignal.connect(self._shuffle)

    def shuffleButtonClicked(self):
        self.shuffleButton.setEnabled(False)
        table = manager.getTable()
        if not table:
            return
        manager.clearTablePeople()
        shuffler = core.Shuffler(manager.getPeoples(), table, core.Ruleset([core.Rule("identical_in_group", ["gender"])]))
        self.shuffle(shuffler)

    def _shuffle(self, pos, person):
        manager.setTablePeople(pos, person)

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def shuffle(self, shuffler):
        import time
        try:
            for i in shuffler:
                if i.success:
                    self.shuffleSignal.emit(i.seat.pos, i.person)
                    logging.info(f"成功将{i.person.get_name()}（属性：{i.person.get_properties()}）放置于座位{i.seat}。")
                else:
                    if i.seat:
                        logging.warning(f"无法将{i.person.get_name()}（属性：{i.person.get_properties()}）放置于座位{i.seat}！")
                    else:
                        logging.warning(f"无法将{i.person.get_name()}（属性：{i.person.get_properties()}）放置于座位！")
                time.sleep(0.025)
        except core.NoValidArrangementError:
            logging.error("没有有效的排座方案！")  # TODO
        time.sleep(0.25)
        self.shuffleButton.setEnabled(True)

    def handleClearButtonClicked(self):
        if not manager.table:
            return

        self.clearButton.setEnabled(False)

        infoBar = InfoBar(
            InfoBarIcon.WARNING,
            "清空预览区所有人员",
            "确定清除已排好的座位？（该操作无法撤销！）",
            isClosable=False,
            duration=-1,
            parent=self.window().mainPage
        )

        def confirm():
            manager.clearTablePeople()
            self.clearButton.setEnabled(True)
            infoBar.close()
            InfoBar.info("成功！", "已清空预览区所有人员！", parent=self.window().mainPage)

        def cancel():
            self.clearButton.setEnabled(True)
            infoBar.close()

        confirm_btn = PushButton(text="确定")
        confirm_btn.clicked.connect(confirm)
        infoBar.addWidget(confirm_btn)

        cancel_btn = PushButton(text="取消")
        cancel_btn.clicked.connect(cancel)
        infoBar.addWidget(cancel_btn)
        infoBar.show()

    def export(self):
        try:
            if not manager.getTable():
                return
            presets = manager.getTablePeoples()
            manager.getTable().clear_all_users()
            for k, v in presets.items():
                manager.getTable().set_user_in_pos(k, v)
            path, _ = QFileDialog.getSaveFileName(self, "导出座位表格文件", setting.read("downloadPath"), "Excel 文件 (*.xlsx *.xls);;JSON 文件 (*.json)")
            if not path:
                return
            if not zb.getFileSuffix(path, True, False):
                path += ".xlsx"
            manager.EXPORTER.export(manager.getTable(), format=zb.getFileSuffix(path, True, False), path=path)
            logging.info(f"导出座位表格文件{path}成功！")
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"导出座位表格文件{zb.getFileName(path)}成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().mainPage)
            showFileButton = PushButton("打开", self, FIF.FOLDER)
            showFileButton.clicked.connect(lambda: zb.showFile(path))
            infoBar.addWidget(showFileButton)
        except Exception:
            logging.error(f"导出座位表格文件失败，报错信息：{traceback.format_exc()}！")
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", f"导出座位表格文件失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().mainPage)

        infoBar.show()


class EditInterface(HeaderCardWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumWidth(100)
        self.setMaximumWidth(250)
        self.setTitle("编辑区")

        self.vBoxLayout2 = QVBoxLayout(self.view)
        self.vBoxLayout2.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(self.vBoxLayout2)

        self.importFileChooser2 = zbw.FileChooser(self)
        self.importFileChooser2.setSuffix({"名单文件": [".csv"]})
        self.importFileChooser2.setOnlyOne(True)
        self.importFileChooser2.setDefaultPath(setting.read("downloadPath"))
        self.importFileChooser2.setDescription("名单")
        self.importFileChooser2.setFixedHeight(100)
        self.importFileChooser2.fileChoosedSignal.connect(self.importPeople)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.vBoxLayout2.addWidget(self.pivot)
        self.vBoxLayout2.addWidget(self.stackedWidget)

        self.pivot.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

        self.listInterface = ListInterface(self)
        self.rulesInterface = RulesInterface(self)

        self.listInterface.vBoxLayout.insertWidget(0, self.importFileChooser2, 0, Qt.AlignCenter)

        self.addSubInterface(self.listInterface, "名单", "名单")
        self.addSubInterface(self.rulesInterface, "规则", "规则")

        self.pivot.setCurrentItem("名单")

        setting.signalConnect(self.settingChanged)

    def settingChanged(self, name):
        if name == "downloadPath":
            self.importFileChooser2.setDefaultPath(setting.read("downloadPath"))

    def importPeople(self, get):
        try:
            if not get:
                return
            people = manager.PEOPLE_PARSER.parse(get[0])
            manager.setPeoples(people)
            manager.setListPeoples()
            setting.save("downloadPath", zb.getFileDir(get[0]))
            logging.info(f"导入名单表格文件{get[0]}成功！")
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"导入名单表格文件{zb.getFileName(get[0])}成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().mainPage)
        except Exception:
            logging.error(f"导入名单表格文件{get[0]}失败，报错信息：{traceback.format_exc()}！")
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", f"导入名单表格文件{zb.getFileName(get[0])}失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, self.window().mainPage)
        infoBar.show()

    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)


class RulesInterface(zbw.BasicPage):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)


class ListInterface(zbw.BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.cardGroup = zbw.CardGroup(self)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(8)
        self.vBoxLayout.addWidget(self.cardGroup)
