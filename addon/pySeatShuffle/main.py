from .widget import *


def addonInit():
    global program, setting, window, progressCenter
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window
    progressCenter = addonBase.progressCenter

    setting.adds({"shuffleAnimationLength": 1.0,
                  "shuffleAnimationDelay": 0.1,
                  "shuffleRetryTime": 5000,
                  "randomSeatGroup": False,
                  "randomSeat": False,
                  "skipUnavailable": True,
                  "fontSize": 20,
                  })
    addonBase.addIcons("icons")
    addonInit1()


def addonWidget():
    return MainPage(window)


class MainPage(QWidget):
    """
    主页
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        manager.mainPage = self

        self.hBoxLayout = QHBoxLayout(self)

        self.shuffleInterface = ShuffleInterface(self)
        self.editInterface = EditInterface(self)
        self.tableInterface = TableInterface(self)

        manager.shuffleInterface = self.shuffleInterface
        manager.editInterface = self.editInterface
        manager.tableInterface = self.tableInterface

        self.rightVBoxLayout = QVBoxLayout(self)
        self.rightVBoxLayout.addWidget(self.shuffleInterface)
        self.rightVBoxLayout.addWidget(self.editInterface)
        self.hBoxLayout.addWidget(self.tableInterface, 2)
        self.hBoxLayout.addLayout(self.rightVBoxLayout, 0)

        self.setLayout(self.hBoxLayout)

    def title(self):
        return "排座工具"

    def icon(self):
        return FIF.LAYOUT


class TableInterface(HeaderCardWidget):
    importTableFinishedSignal = pyqtSignal(bool, core.SeatTable, str)

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
        self.tableChooser.fileChoosedSignal.connect(self.importTable)
        self.tableChooser.setFixedSize(200, 120)
        self.viewLayout.addWidget(self.tableChooser, Qt.AlignCenter)

        setting.signalConnect(self.settingChanged)
        self.importTableFinishedSignal.connect(self.importTableFinished)

    def settingChanged(self, name):
        if name == "downloadPath":
            self.tableChooser.setDefaultPath(setting.read("downloadPath"))

    def clearTable(self):
        manager.removeTable()
        self.tableChooser.show()
        self.closeButton.hide()

    def importTable(self, path):
        if not path:
            return
        self.tableChooser.setEnabled(False)
        self.loadingMessageBox = zbw.LoadingMessageBox(self.window())
        self.loadingMessageBox.show()

        program.THREAD_POOL.submit(self._importTable, path[0])

    def _importTable(self, path):
        try:
            if zb.getFileSuffix(path) == ".xlsx":
                table = manager.XLSX_PARSER.parse(path)
            elif zb.getFileSuffix(path) == ".json":
                table = manager.JSON_PARSER.parse(path)
            else:
                raise Error("文件格式不兼容！")
            setting.save("downloadPath", zb.getFileDir(path))
            logging.info(f"导入座位表格文件{path}成功！")
            self.importTableFinishedSignal.emit(True, table, path)
        except:
            logging.error(f"导入座位表格文件{path}失败，报错信息：{traceback.format_exc()}！")
            self.importTableFinishedSignal.emit(False, core.SeatTable([], (0, 0)), path)

    def importTableFinished(self, status, table, path):
        if status:
            manager.setTable(table)
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"导入座位文件{zb.getFileName(path)}成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)
            self.tableChooser.hide()
            self.closeButton.show()
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", f"导入座位文件{zb.getFileName(path)}失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)
        infoBar.show()
        self.tableChooser.setEnabled(True)
        self.loadingMessageBox.close()


class SettingMessageBox(zbw.ScrollMessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.yesButton.deleteLater()
        self.cancelButton.setText("关闭")

        self.titleLabel = TitleLabel("设置", self)

        self.viewLayout.insertWidget(0, self.titleLabel)

        self.cardGroup1 = zbw.CardGroup("动画", self)
        self.cardGroup2 = zbw.CardGroup("功能", self)

        self.animationLengthSettingCard = AnimationLengthSettingCard(self)
        self.animationDelaySettingCard = AnimationDelaySettingCard(self)

        self.retrySettingCard = RetrySettingCard(self)
        self.fontSizeSettingCard = FontSizeSettingCard(self)
        self.randomSeatSettingCard = RandomSeatSettingCard(self)
        self.randomSeatGroupSettingCard = RandomSeatGroupSettingCard(self)
        self.skipUnavailableSettingCard = SkipUnavailableSettingCard(self)

        self.cardGroup1.addCard(self.animationLengthSettingCard, "animationLengthSettingCard")
        self.cardGroup1.addCard(self.animationDelaySettingCard, "animationDelaySettingCard")

        self.cardGroup2.addCard(self.retrySettingCard, "retrySettingCard")
        self.cardGroup2.addCard(self.fontSizeSettingCard, "fontSizeSettingCard")
        self.cardGroup2.addCard(self.randomSeatSettingCard, "randomSeatSettingCard")
        self.cardGroup2.addCard(self.randomSeatGroupSettingCard, "randomSeatGroupSettingCard")
        self.cardGroup2.addCard(self.skipUnavailableSettingCard, "skipUnavailableSettingCard")

        self.scrollLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.scrollLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)

        self.widget.setFixedSize(600, 500)


class ShuffleInterface(HeaderCardWidget):
    shuffleSignal = pyqtSignal(tuple, core.Person)
    shuffleFinishedSignal = pyqtSignal(bool)

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

        self.settingButton = ToolButton(FIF.SETTING, self)
        self.settingButton.clicked.connect(self.settingButtonClicked)

        self.clearButton = PushButton("清空", self, FIF.DELETE)
        self.clearButton.clicked.connect(self.clearButtonClicked)

        self.exportButton = PushButton("导出", self, FIF.UP)
        self.exportButton.clicked.connect(self.export)

        self.hBoxLayout1.addWidget(self.shuffleButton, 2)
        self.hBoxLayout1.addWidget(self.settingButton, 2)
        self.hBoxLayout2.addWidget(self.exportButton, 1)
        self.hBoxLayout2.addWidget(self.clearButton, 1)
        self.vBoxLayout2.addLayout(self.hBoxLayout1)
        self.vBoxLayout2.addLayout(self.hBoxLayout2)

        self.shuffleSignal.connect(lambda pos, person: manager.setTablePerson(pos, person))
        self.shuffleFinishedSignal.connect(self.shuffleFinished)

    def settingButtonClicked(self):
        messageBox = SettingMessageBox(self.window())
        messageBox.show()

    def shuffleButtonClicked(self):
        table = manager.getTable()
        person = manager.getPeople()
        if not table or not person:
            return
        manager.editInterface.pivot.setCurrentItem("名单")
        manager.mainPage.setEnabled(False)
        table = manager.getTable()

        wait_back: bool = any(isinstance(i.parent(), PersonWidgetTableBase) for i in manager.getPersonWidgets())
        manager.clearTablePerson()
        shuffler = core.Shuffler(
            person,
            table,
            manager.getRuleSet(),
            core.ShufflerConfig(
                int(setting.read("randomSeatGroup")),
                setting.read("skipUnavailable")
            )
        )

        program.THREAD_POOL.submit(self.shuffle, shuffler, wait_back)

    def shuffle(self, shuffler, wait_back: bool):
        import time
        if wait_back:
            time.sleep(setting.read("shuffleAnimationLength"))
        fail_count: int = 0
        try:
            for i in shuffler:
                if i.success:
                    if not isinstance(i.person, core.FakePerson):
                        self.shuffleSignal.emit(tuple(i.seat.pos), i.person)
                        logging.info(f"成功将{i.person.get_name()}（属性：{i.person.get_properties()}）放置于座位{i.seat}。")
                        time.sleep(setting.read("shuffleAnimationDelay"))
                else:
                    if i.seat:
                        logging.warning(f"无法将{i.person.get_name()}（属性：{i.person.get_properties()}）放置于座位{i.seat}！")
                    else:
                        logging.warning(f"无法将{i.person.get_name()}（属性：{i.person.get_properties()}）放置于座位！")
                    fail_count += 1
                    if fail_count >= setting.read("shuffleRetryTime"):
                        raise core.NoValidArrangementError("达到设置的最大重试次数！")
            time.sleep(max(setting.read("shuffleAnimationLength") - setting.read("shuffleAnimationDelay"), 0))
            self.shuffleFinishedSignal.emit(True)
        except core.NoValidArrangementError:
            logging.error(f"没有有效的排座方案，报错信息：{traceback.format_exc()}！")
            self.shuffleFinishedSignal.emit(False)
        except:
            logging.error(f"排座失败，报错信息：{traceback.format_exc()}！")
            self.shuffleFinishedSignal.emit(False)

    def shuffleFinished(self, msg):
        if msg:
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", "自动排座成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", "自动排座失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)

        infoBar.show()
        manager.mainPage.setEnabled(True)

    def clearButtonClicked(self):
        if not manager.table:
            return

        self.clearButton.setEnabled(False)

        infoBar = InfoBar(
            InfoBarIcon.WARNING,
            "清空预览区所有人员",
            "确定清除已排好的座位？（该操作无法撤销！）",
            isClosable=False,
            duration=-1,
            parent=manager.mainPage
        )

        def confirm():
            manager.clearTablePerson()
            self.clearButton.setEnabled(True)
            infoBar.close()
            InfoBar.info("成功！", "已清空预览区所有人员！", parent=manager.mainPage)

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
            table = manager.getTable()
            if not table:
                return
            path, _ = QFileDialog.getSaveFileName(self, "导出座位表格文件", setting.read("downloadPath"), "Excel 文件 (*.xlsx *.xls);;JSON 文件 (*.json)")
            if not path:
                return
            if not zb.getFileSuffix(path, True, False):
                path += ".xlsx"
            manager.EXPORTER.export(table, format=zb.getFileSuffix(path, True, False), path=path)
            logging.info(f"导出座位表格文件{path}成功！")
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"导出座位表格文件{zb.getFileName(path)}成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)
            showFileButton = PushButton("打开", self, FIF.FOLDER)
            showFileButton.clicked.connect(lambda: zb.showFile(path))
            infoBar.addWidget(showFileButton)
        except Exception:
            logging.error(f"导出座位表格文件失败，报错信息：{traceback.format_exc()}！")
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", f"导出座位表格文件失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)

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

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.vBoxLayout2.addWidget(self.pivot)
        self.vBoxLayout2.addWidget(self.stackedWidget)

        self.pivot.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

        self.listInterface = ListInterface(self)
        self.rulesInterface = RulesInterface(self)

        manager.listInterface = self.listInterface
        manager.rulesInterface = self.rulesInterface

        self.addSubInterface(self.listInterface, "名单", "名单")
        self.addSubInterface(self.rulesInterface, "规则", "规则")

        self.pivot.setCurrentItem("名单")

    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)


class RulesInterface(zbw.BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.cardGroup = zbw.CardGroup("当前规则数 (0)", self)
        self.cardGroup.boxLayout.insertSpacing(1, -12)

        self.addButton = PushButton("新增规则", self, FIF.ADD)
        self.addButton.clicked.connect(self.addButtonClicked)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(8)
        self.vBoxLayout.addWidget(self.addButton)
        self.vBoxLayout.addWidget(self.cardGroup)

    def addButtonClicked(self):
        if not manager.person_keys:
            return

        messageBox = AddRuleMessageBox(self.window())
        messageBox.exec()
        result = messageBox.result
        if not result:
            return

        manager.addRule(result.get("id"), result.get("key"))


class ListInterface(zbw.BasicTab):
    getKeyFinishedSignal = pyqtSignal(str, list)
    importPersonFinishedSignal = pyqtSignal(bool, str, list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.listChooser = zbw.FileChooser(self)
        self.listChooser.setSuffix({"名单文件": [".csv"]})
        self.listChooser.setOnlyOne(True)
        self.listChooser.setDefaultPath(setting.read("downloadPath"))
        self.listChooser.setDescription("名单")
        self.listChooser.setFixedHeight(100)
        self.listChooser.fileChoosedSignal.connect(self.importPerson)

        self.cardGroup = zbw.CardGroup("当前人数 (0/0)", self)
        self.cardGroup.boxLayout.insertSpacing(1, -12)
        self.cardGroup.cardCountChanged.connect(manager.personNumberChanged)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(8)
        self.vBoxLayout.addWidget(self.listChooser, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.cardGroup)

        setting.signalConnect(self.settingChanged)
        self.getKeyFinishedSignal.connect(self.getKeyFinished)
        self.importPersonFinishedSignal.connect(self.importPersonFinished)

    def settingChanged(self, name):
        if name == "downloadPath":
            self.listChooser.setDefaultPath(setting.read("downloadPath"))

    def importPerson(self, path: str):
        if not path:
            return
        self.listChooser.setEnabled(False)
        self.loadingMessageBox = zbw.LoadingMessageBox(self.window())
        self.loadingMessageBox.show()
        program.THREAD_POOL.submit(self._getKey, path[0])

    def _getKey(self, path):
        try:
            keys = manager.PERSON_PARSER.get_keys(path)
            setting.save("downloadPath", zb.getFileDir(path))
            self.getKeyFinishedSignal.emit(path, keys)
        except:
            logging.error(f"导入名单表格文件{path}失败，报错信息：{traceback.format_exc()}！")
            self.importPersonFinishedSignal.emit(False, path, [])

    def getKeyFinished(self, path, keys):
        self.loadingMessageBox.close()
        setKeyMessageBox = SetKeyMessageBox(self.window(), keys)
        try:
            result = setKeyMessageBox.exec()
            if not setKeyMessageBox.result:
                self.importPersonFinishedSignal.emit(False, path, [])
            else:
                self.loadingMessageBox = zbw.LoadingMessageBox(self.window())
                self.loadingMessageBox.show()

                key = keys[result]
                program.THREAD_POOL.submit(self._importPerson, key, keys, path)
        except:
            self.importPersonFinishedSignal.emit(False, path, [])

    def _importPerson(self, key, keys, path):
        try:
            manager.person_keys = keys
            person = manager.PERSON_PARSER.parse(path, key)
            self.importPersonFinishedSignal.emit(True, path, person)
            logging.info(f"导入名单表格文件{path}成功！")
        except:
            self.importPersonFinishedSignal.emit(False, path, [])
            logging.error(f"导入名单表格文件{path}失败，报错信息：{traceback.format_exc()}！")

    def importPersonFinished(self, status, path, person):
        if status:
            manager.setPeople(person)
            manager.setListPeople(True)
            manager.removeRules()
            infoBar = InfoBar(InfoBarIcon.SUCCESS, "成功", f"导入名单文件{zb.getFileName(path)}成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)
        else:
            infoBar = InfoBar(InfoBarIcon.ERROR, "失败", f"导入名单文件{zb.getFileName(path)}失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.BOTTOM, manager.mainPage)
        infoBar.show()
        self.listChooser.setEnabled(True)
        self.loadingMessageBox.close()
