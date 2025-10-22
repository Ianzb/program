from source.addon import *
from .core import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, setting, window, progressCenter
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window
    progressCenter = addonBase.progressCenter

    setting.adds({"messageTitle": "",
                  "messageContent": "",
                  "messageEnabled": False,
                  "canCloseMessage": True,
                  "messageMove": False,
                  "monitorPath": [],
                  "autoCopy": False,
                  "copyPath": zb.joinPath(program.DATA_PATH, "复制"),
                  })


class PeopleWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(30, 20)
        self.people = None

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

        self.label = SubtitleLabel("", self)
        self.label.setWordWrap(True)

        self.vBoxLayout.addWidget(self.label)

        self.setLayout(self.vBoxLayout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return

        drag_pixmap = QPixmap(self.size())
        drag_pixmap.fill(Qt.transparent)
        self.render(drag_pixmap)

        painter = QPainter(drag_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(drag_pixmap.rect(), QColor(255, 255, 255, 128))  # 设置50%透明度
        painter.end()

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.people))
        mime_data.setData("PeopleWidget", QByteArray(self.people.get_name().encode("utf-8")))
        drag.setMimeData(mime_data)

        drag.setPixmap(drag_pixmap)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        # 执行拖拽操作
        drag.exec_(Qt.MoveAction)

    def getPeople(self):
        return self.people

    def setPeople(self, people: Person):
        self.people = people
        self.label.setText(self.getPeople().get_name())

    def setParent(self, a0):
        old = self.parent()
        if isinstance(old, PeopleWidgetTableBase) or isinstance(old, PeopleWidgetBase):
            self.parent().removePeople()
        super().setParent(a0)

    def stopAnimation(self):
        if hasattr(self, "animation") and self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()
            self.moveAnimationFinished()

    def moveAnimation(self, old_pos: QPoint, new_pos: QPoint):
        self.stopAnimation()

        self.temp_widget = QWidget(self.window())
        self.temp_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.temp_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.temp_widget.setStyleSheet("background: transparent;")

        # 创建组件的副本用于动画
        drag_pixmap = QPixmap(self.size())
        drag_pixmap.fill(Qt.transparent)
        self.render(drag_pixmap)
        self.hide()

        pixmap_label = QLabel(self.temp_widget)
        pixmap_label.setPixmap(drag_pixmap)
        pixmap_label.move(0, 0)

        # 设置临时窗口的位置和大小
        self.temp_widget.resize(self.size())
        self.temp_widget.move(old_pos)
        self.temp_widget.show()

        # 创建动画
        self.animation = QPropertyAnimation(self.temp_widget, b"pos")
        self.animation.setStartValue(old_pos)
        self.animation.setEndValue(new_pos)
        self.animation.setDuration(300)  # 300ms 动画
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        # 动画完成后的回调

        self.animation.finished.connect(self.moveAnimationFinished)

        self.animation.start()

    def moveAnimationFinished(self):
        self.show()
        self.temp_widget.hide()
        self.temp_widget.deleteLater()


class PeopleWidgetTableBase(CardWidget):
    def __init__(self, parent=None, pos: (int, int) = (0, 0)):
        super().__init__(parent)
        self.people = None

        self.pos = tuple(pos)

        self.setAcceptDrops(True)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

        self.setLayout(self.vBoxLayout)

        self.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.removeButton = ToolButton(FIF.CLOSE, self)
        self.removeButton.clicked.connect(self.removeButtonClicked)
        self.removeButton.move(4, 4)
        self.removeButton.setFixedSize(24, 24)
        self.removeButton.hide()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().hasFormat("PeopleWidget"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().hasFormat("PeopleWidget"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().hasFormat("PeopleWidget"):
            people_name = bytes(event.mimeData().data("PeopleWidget")).decode()
            if manager.hasPeople(people_name):
                self.setPeople(manager.getPeopleWidget(people_name))
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def getPeople(self):
        return self.people

    def setPeople(self, people: PeopleWidget):
        people.stopAnimation()
        old_pos = people.mapToGlobal(QPoint(0, 0))
        old_people = self.people
        old_parent = people.parent()

        if old_people:
            if isinstance(old_parent, PeopleWidgetTableBase):
                self.removePeople()
                old_parent.setPeople(old_people)
            else:
                return
        else:
            if isinstance(old_parent, PeopleWidgetTableBase):
                old_parent.removePeople()
            elif isinstance(old_parent, PeopleWidgetBase):
                old_parent.removePeople()

        self.removePeople()
        self.people = people

        # 计算目标位置
        self.vBoxLayout.addWidget(people)
        self.people.stackUnder(self.removeButton)
        self.layout().activate()  # 强制布局更新
        QApplication.processEvents()  # 处理 pending 事件

        new_pos = self.mapToGlobal(self.people.pos())

        self.people.moveAnimation(old_pos, new_pos)

        self.setNewToolTip("\n".join([self.people.people.get_name()] + [f"{k}：{v}" for k, v in self.people.people.get_properties().items()]))

    def removePeople(self):
        self.vBoxLayout.removeWidget(self.people)
        self.people, people = None, self.people
        return people

    def deletePeople(self):
        self.removePeople()

    def clearPeople(self):
        self.removePeople()

    def enterEvent(self, event):
        if self.people:
            self.removeButton.show()

    def leaveEvent(self, event):
        self.removeButton.hide()

    def removeButtonClicked(self):
        if self.people:
            manager.removeTablePeople(self.pos)
            self.removeButton.hide()


class PeopleWidgetBase(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.people = None

        self.setMaximumHeight(40)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.vBoxLayout)

    def getPeople(self):
        return self.people

    def setPeople(self, people: PeopleWidget):
        self.people = people
        self.vBoxLayout.addWidget(people)
        self.setNewToolTip("\n".join([self.people.people.get_name()] + [f"{k}：{v}" for k, v in self.people.people.get_properties().items()]))

    def removePeople(self):
        self.parent().removeCard(self.people.people.get_name())
        self.deleteLater()

    def deletePeople(self):
        self.removePeople()

    def clearPeople(self):
        self.removePeople()


class Manager(QWidget):
    PEOPLE_PARSER = PeopleParser()
    XLSX_PARSER = SeatTableParserXlsx()
    JSON_PARSER = SeatTableParserJson()
    EXPORTER = SeatTableExporter()

    def __init__(self):
        super().__init__()
        self.table: SeatTable = None
        self.people: dict = {}  # {name:{"people":Person, "widget": PeopleWidget}}
        self.table_widget: dict = {}

        self.editInterface = None
        self.shuffleInterface = None
        self.tableInterface = None
        self.listInterface = None
        self.rulesInterface = None

    def getTable(self):
        """
        获取表格
        :return:
        """
        return self.table

    def setTable(self, table, widget=None):
        """
        设置表格
        :param table:
        """
        if widget is None:
            widget = {}
        self.table = table
        self.removeTable()

        self.table_widget = widget

        offset_r, offset_c = self.table.get_offset()
        for group in self.table.get_seat_groups():
            for seat in group.get_seats():
                r, c = seat.get_pos()
                widget = PeopleWidgetTableBase(self, (r, c))
                self.table_widget[(r, c)] = widget
                self.tableInterface.gridLayout.addWidget(widget, r - offset_r, c - offset_c, 1, 1)
        rt, ct = self.table.get_size()
        for r in range(rt):
            for c in range(ct):
                if not self.tableInterface.gridLayout.itemAtPosition(r, c):
                    self.tableInterface.gridLayout.addWidget(QWidget(self), r, c, 1, 1)
                self.tableInterface.gridLayout.setRowStretch(r, 1)
                self.tableInterface.gridLayout.setColumnStretch(c, 1)

    def getPeople(self, name: str | Person | PeopleWidget):
        """
        获取指定person
        :param name:
        :return:
        """
        if isinstance(name, str):
            return self.people.get(name, {}).get("people", None)
        elif isinstance(name, Person):
            return name
        elif isinstance(name, PeopleWidget):
            return name.getPeople()
        return None

    def getPeopleWidget(self, name: str | Person | PeopleWidget):
        """
        获取指定PeopleWidget
        :param name:
        :return:
        """
        if isinstance(name, str):
            return self.people.get(name, {}).get("widget", None)
        elif isinstance(name, Person):
            return self.people.get(name.get_name(), {}).get("widget", None)
        elif isinstance(name, PeopleWidget):
            return name
        return None

    def getPeoples(self):
        """
        获取所有Person
        :return:
        """
        return [p["people"] for p in self.people.values()]

    def getPeopleWidgets(self):
        """
        获取所有PeopleWidget
        :return:
        """
        return [p["widget"] for p in self.people.values()]

    def setPeople(self, people: Person | PeopleWidget):
        """
        通过Person对象或PeopleWidget对象向people列表新增People
        :param people:
        """
        if isinstance(people, Person):
            people_widget = PeopleWidget()
            people_widget.setPeople(people)
            name = people.get_name()
            if name in self.people.keys():
                existing_widget = self.people[name]["widget"]
                if isinstance(existing_widget.parent(), PeopleWidgetBase):
                    existing_widget.parent().removePeople()
                elif isinstance(existing_widget.parent(), PeopleWidgetTableBase):
                    existing_widget.parent().removePeople()
                existing_widget.deleteLater()
            self.people[name] = {"people": people, "widget": people_widget}
        elif isinstance(people, PeopleWidget):
            name = people.getPeople().get_name()
            if name in self.people.keys():
                existing_widget = self.people[name]["widget"]
                if isinstance(existing_widget.parent(), PeopleWidgetBase):
                    existing_widget.parent().removePeople()
                elif isinstance(existing_widget.parent(), PeopleWidgetTableBase):
                    existing_widget.parent().removePeople()
                existing_widget.deleteLater()
            self.people[name] = {"people": people.getPeople(), "widget": people}

    def setPeoples(self, peoples: list[Person | PeopleWidget]):
        """
        设置多个people
        :param peoples:
        """
        for people in peoples:
            self.setPeople(people)

    def hasPeople(self, name: str | Person | PeopleWidget):
        """
        是否有指定people
        :param name:
        :return:
        """
        if isinstance(name, str):
            return name in self.people.keys()
        elif isinstance(name, Person):
            return name.get_name() in self.people.keys()
        elif isinstance(name, PeopleWidget):
            return name.getPeople().get_name() in self.people.keys()
        return False

    def removePeople(self, name: str | Person | PeopleWidget):
        """
        移除指定people，并从ui上移除
        :param name: people
        :return:
        """
        if isinstance(name, str):
            if name in self.people.keys():
                name = name
        elif isinstance(name, Person):
            if name.get_name() in self.people.keys():
                name = name.get_name()
        elif isinstance(name, PeopleWidget):
            if name.getPeople().get_name() in self.people.keys():
                name = name.getPeople().get_name()
        else:
            return
        v = self.people.pop(name, None)
        if isinstance(v, dict):
            widget = v["widget"]
            if isinstance(widget.parent(), PeopleWidgetBase):
                widget.parent().removePeople()
            elif isinstance(widget.parent(), PeopleWidgetTableBase):
                widget.parent().removePeople()
            widget.deleteLater()

    def clearPeople(self):
        """
        清空people列表
        """
        for widget in self.getPeopleWidgets():
            if isinstance(widget.parent(), PeopleWidgetBase):
                widget.parent().removePeople()
            elif isinstance(widget.parent(), PeopleWidgetTableBase):
                widget.parent().removePeople()
            widget.deleteLater()
        self.people = {}

    def setListPeoples(self, move: bool = True):
        """
        根据当前的people列表重新创建列表
        :param move: 是否从表格移动人到列表
        """
        self.listInterface.cardGroup.clearCard()

        for k, v in self.people.items():
            people_widget: PeopleWidget = v["widget"]
            parent = people_widget.parent()
            if move or not isinstance(parent, PeopleWidgetTableBase):
                people_widget.setParent(self.listInterface)
                widget = PeopleWidgetBase(self.listInterface)
                widget.setPeople(people_widget)
                self.listInterface.cardGroup.addCard(widget, k)
                widget.layout()

    def getTableWidgets(self):
        """
        获得所有TableWidget
        :return:
        """
        return self.table_widget

    def getTableWidget(self, pos: (int, int)):
        """
        获取指定位置的TableWidget
        :param pos: 坐标
        :return:
        """
        return self.table_widget.get(tuple(pos), None)

    def getTablePeople(self, pos: (int, int)):
        """
        获取指定位置的人员
        :return: People
        """
        widget: PeopleWidgetTableBase | None = self.getTableWidget(tuple(pos))
        if widget:
            return widget.getPeople().getPeople()
        return None

    def getTablePeoples(self):
        """
        获取所有人员
        :return: dict
        """
        return {k: v.getPeople().getPeople() for k, v in self.table_widget.items() if v.getPeople() is not None and v.getPeople().getPeople() is not None}

    def setTablePeople(self, pos: (int, int), name: str | Person | PeopleWidget):
        """
        设置表格指定位置的人
        :param name: 人的名字，可以为字符串，Person对象或People组件
        :param pos: （行，列）
        :return: widget
        """
        people = self.getPeopleWidget(name)
        widget = self.getTableWidget(tuple(pos))
        if widget:
            widget.setPeople(people)
            logging.info(f"设置表格位置{pos}的人为{people.people.get_name()}！")
            return True
        return False

    def removeTablePeople(self, pos: (int, int)):
        """
        移除表格指定位置的人并放回列表
        :param pos:
        """
        widget = self.table_widget.get(tuple(pos), None)
        if widget:
            people = widget.removePeople()
            people.setParent(None)
            self.setListPeoples(False)

    def clearTablePeople(self):
        """
        清空表格中的所有人，并放回列表
        """
        self.setListPeoples()
        self.table.clear_all_users()

    def removeTable(self):
        """
        移除表格
        """
        while self.tableInterface.gridLayout.count():
            item = self.tableInterface.gridLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.setListPeoples()
        for r in range(self.tableInterface.gridLayout.rowCount()):
            self.tableInterface.gridLayout.setRowStretch(r, 0)
        for c in range(self.tableInterface.gridLayout.columnCount()):
            self.tableInterface.gridLayout.setColumnStretch(c, 0)
        self.table_widget = {}


manager = Manager()
