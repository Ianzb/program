import json

try:
    from source.addon import *
    import pySeatShuffle.core as core

    addonBase = AddonBase()


    def addonInit1():
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
except:
    import core
    from ..program import *

try:
    from program.source.addon import *
except:
    pass


class PersonWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(30, 20)
        self.person = None

        self.move_back = False

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

        self.label = SubtitleLabel("", self)

        self.vBoxLayout.addWidget(self.label)

        self.setLayout(self.vBoxLayout)

        self.setStyleSheet("background: transparent;")

        setting.signalConnect(self.setFontSize)
        self.setFontSize()

    def setFontSize(self, msg="fontSize"):
        if msg == "fontSize":
            self.label.getFont = lambda: getFont(setting.read("fontSize"), QFont.DemiBold)
            self.label.setFont(self.label.getFont())

    def deleteLater(self):
        setting.changeSignal.disconnect(self.setFontSize)
        super().deleteLater()

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
        mime_data.setText(str(self.person))
        mime_data.setData("PersonWidget", QByteArray(self.getID().encode("utf-8")))
        drag.setMimeData(mime_data)

        drag.setPixmap(drag_pixmap)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        # 执行拖拽操作
        drag.exec_(Qt.MoveAction)

    def getPerson(self):
        return self.person

    def setPerson(self, person: core.Person):
        self.person = person
        self.label.setText(self.getName())

        self.setNewToolTip("\n".join([str(self.getID())] + [f"{k}：{v}" for k, v in self.getProterties().items()]))

    def getID(self):
        return self.person.get_id()

    def getName(self):
        return self.person.get_name()

    def getProterties(self):
        return self.person.get_properties()

    def setParent(self, a0):
        old = self.parent()
        if isinstance(old, PersonWidgetTableBase) or isinstance(old, PersonWidgetBase):
            self.parent().removePerson()
        super().setParent(a0)

    def stopAnimation(self):
        if hasattr(self, "animation") and self.animation_group.state() == QPropertyAnimation.Running:
            self.animation_group.stop()
            self.moveAnimationFinished()

    def setTransparent(self, value: float):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(value)
        self.setGraphicsEffect(opacity_effect)

    def moveAnimation(self, old_pixmap: QPixmap, old_pos: QPoint, new_pos: QPoint):
        self.stopAnimation()
        self.setTransparent(0.0)
        if hasattr(self, 'old_temp_widget'):
            self.old_temp_widget.hide()
            self.old_temp_widget.deleteLater()
            del self.old_temp_widget
        if hasattr(self, 'new_temp_widget'):
            self.new_temp_widget.hide()
            self.new_temp_widget.deleteLater()
            del self.new_temp_widget

        # 创建旧位置的临时控件
        self.old_temp_widget = QLabel(manager.mainPage)
        self.old_temp_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.old_temp_widget.setPixmap(old_pixmap)
        self.old_temp_widget.resize(old_pixmap.size())
        self.old_temp_widget.move(old_pos)

        # 创建新位置的临时控件（使用当前状态渲染）
        new_pixmap = QPixmap(self.size())
        new_pixmap.fill(Qt.transparent)
        self.setTransparent(1.0)
        self.render(new_pixmap)
        self.setTransparent(0.0)

        self.new_temp_widget = QLabel(manager.mainPage)
        self.new_temp_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.new_temp_widget.setPixmap(new_pixmap)
        self.new_temp_widget.resize(new_pixmap.size())
        self.new_temp_widget.move(old_pos)  # 从相同位置开始

        # 设置初始透明度
        old_opacity_effect = QGraphicsOpacityEffect(self.old_temp_widget)
        old_opacity_effect.setOpacity(1.0)  # 旧pixmap初始完全不透明
        self.old_temp_widget.setGraphicsEffect(old_opacity_effect)

        new_opacity_effect = QGraphicsOpacityEffect(self.new_temp_widget)
        new_opacity_effect.setOpacity(0.0)
        self.new_temp_widget.setGraphicsEffect(new_opacity_effect)

        self.old_temp_widget.show()
        self.new_temp_widget.show()

        # 创建位置动画（两个控件同时移动）
        self.pos_animation = QPropertyAnimation(self)
        self.pos_animation.setDuration(int(setting.read("shuffleAnimationLength") * 1000))
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 创建透明度动画
        old_opacity_animation = QPropertyAnimation(old_opacity_effect, b"opacity")
        old_opacity_animation.setDuration(int(setting.read("shuffleAnimationLength") * 1000))
        old_opacity_animation.setStartValue(1.0)
        old_opacity_animation.setKeyValueAt(0.4, 1.0)
        old_opacity_animation.setKeyValueAt(0.8, 0.0)
        old_opacity_animation.setEndValue(0.0)

        new_opacity_animation = QPropertyAnimation(new_opacity_effect, b"opacity")
        new_opacity_animation.setDuration(int(setting.read("shuffleAnimationLength") * 1000))
        new_opacity_animation.setStartValue(0.0)
        new_opacity_animation.setKeyValueAt(0.2, 0.0)
        new_opacity_animation.setKeyValueAt(0.6, 1.0)
        new_opacity_animation.setEndValue(1.0)

        # 使用动画组同时执行所有动画
        self.animation_group = QParallelAnimationGroup(self)

        # 为两个控件分别创建位置动画
        old_pos_animation = QPropertyAnimation(self.old_temp_widget, b"pos", self)
        old_pos_animation.setDuration(int(setting.read("shuffleAnimationLength") * 1000))
        old_pos_animation.setStartValue(old_pos)
        old_pos_animation.setEndValue(new_pos)
        old_pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        new_pos_animation = QPropertyAnimation(self.new_temp_widget, b"pos", self)
        new_pos_animation.setDuration(int(setting.read("shuffleAnimationLength") * 1000))
        new_pos_animation.setStartValue(old_pos)
        new_pos_animation.setEndValue(new_pos)
        new_pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.animation_group.addAnimation(old_pos_animation)
        self.animation_group.addAnimation(new_pos_animation)
        self.animation_group.addAnimation(old_opacity_animation)
        self.animation_group.addAnimation(new_opacity_animation)

        self.animation_group.finished.connect(self.moveAnimationFinished)
        self.animation_group.start()

    def moveAnimationFinished(self):
        self.setTransparent(1.0)
        if hasattr(self, 'old_temp_widget'):
            self.old_temp_widget.hide()
            self.old_temp_widget.deleteLater()
            del self.old_temp_widget
        if hasattr(self, 'new_temp_widget'):
            self.new_temp_widget.hide()
            self.new_temp_widget.deleteLater()
            del self.new_temp_widget


class PersonWidgetTableBase(CardWidget):
    def __init__(self, parent=None, pos: (int, int) = (0, 0)):
        super().__init__(parent)
        self.person = None

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
        if event.mimeData().hasText() and event.mimeData().hasFormat("PersonWidget"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().hasFormat("PersonWidget"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().hasFormat("PersonWidget"):
            id = bytes(event.mimeData().data("PersonWidget")).decode()
            if manager.hasPerson(id) and not self.person or not isinstance(manager.getPersonWidget(id).parent(), PersonWidgetBase):
                self.setPerson(manager.getPersonWidget(id))
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def getPerson(self):
        return self.person

    def setPerson(self, person: PersonWidget):
        old_person = self.person
        old_parent = person.parent()

        if old_parent is self:
            return

        person.stopAnimation()

        # 在移动前获取旧位置的pixmap
        person.setTransparent(1.0)
        old_pixmap = QPixmap(person.size())
        old_pixmap.fill(Qt.transparent)
        person.render(old_pixmap)
        person.setTransparent(0.0)

        old_pos = person.mapToGlobal(QPoint(0, 0)) - manager.mainPage.mapToGlobal(QPoint(0, 0))

        if old_person:
            if isinstance(old_parent, PersonWidgetTableBase):
                self.removePerson()
                old_parent.setPerson(old_person)
            else:
                return
        else:
            if isinstance(old_parent, PersonWidgetTableBase):
                old_parent.removePerson()
            elif isinstance(old_parent, PersonWidgetBase):
                old_parent.removePerson()

        self.removePerson()
        self.person = person

        # 计算目标位置
        self.vBoxLayout.addWidget(person)
        self.person.stackUnder(self.removeButton)
        self.layout().activate()  # 强制布局更新
        QApplication.processEvents()  # 处理 pending 事件

        new_pos = self.person.mapToGlobal(QPoint(0, 0)) - manager.mainPage.mapToGlobal(QPoint(0, 0))

        # 传入旧位置的pixmap进行动画
        self.person.moveAnimation(old_pixmap, old_pos, new_pos)

    def removePerson(self):
        self.removeNewToolTip()
        if self.person:
            self.vBoxLayout.removeWidget(self.person)
            self.person, person = None, self.person
            return person
        return None

    def deletePerson(self):
        self.removePerson()

    def clearPerson(self):
        self.removePerson()

    def enterEvent(self, event):
        if self.person:
            self.removeButton.show()

    def leaveEvent(self, event):
        self.removeButton.hide()

    def removeButtonClicked(self):
        if self.person:
            manager.removeTablePerson(self.pos)
            self.removeButton.hide()


class PersonWidgetBase(CardWidget):
    def __init__(self, parent=None, card_group=None):
        super().__init__(parent)
        self.person = None
        self.card_group = card_group

        self.setMaximumHeight(40)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.vBoxLayout)

    def getPerson(self):
        return self.person

    def setPerson(self, person: PersonWidget, animation: bool = True):
        person.stopAnimation()

        if animation:
            # 在移动前获取旧位置的pixmap
            person.setTransparent(1.0)
            old_pixmap = QPixmap(person.size())
            old_pixmap.fill(Qt.transparent)
            person.render(old_pixmap)
            person.setTransparent(0.0)

            old_pos = person.mapToGlobal(QPoint(0, 0)) - manager.mainPage.mapToGlobal(QPoint(0, 0))

        person.setParent(self)

        self.person = person
        self.vBoxLayout.addWidget(person)

        QApplication.processEvents()  # 处理 pending 事件

        if animation:
            new_pos = self.person.mapToGlobal(QPoint(0, 0)) - manager.mainPage.mapToGlobal(QPoint(0, 0))

            self.person.moveAnimation(old_pixmap, old_pos, new_pos)

    def removePerson(self):
        self.parent().removeCard(self.person.getID())

        self.deleteLater()

    def deletePerson(self):
        self.removePerson()

    def clearPerson(self):
        self.removePerson()


class AnimationLengthSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.SPEED_HIGH, "动画时长", "名称标签移动动画的时长", parent)
        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("时长秒数")
        self.lineEdit.setNewToolTip("名称标签移动动画的时长")
        self.lineEdit.textEdited.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QDoubleValidator(0.0, 10.0, 3))

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(setting.read("shuffleAnimationLength")))
        self.lineEdit.blockSignals(False)

    def setEvent(self, msg):
        if msg == "shuffleAnimationLength":
            self.set()

    def textChanged(self):
        try:
            setting.save("shuffleAnimationLength", float(self.lineEdit.text()))
        except:
            return


class AnimationDelaySettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.SPEED_HIGH, "动画延迟", "名称标签移动动画之间的延迟", parent)
        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("延迟秒数")
        self.lineEdit.setNewToolTip("名称标签移动动画之间的延迟")
        self.lineEdit.textEdited.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QDoubleValidator(0.0, 10.0, 3))

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(setting.read("shuffleAnimationDelay")))
        self.lineEdit.blockSignals(False)

    def setEvent(self, msg):
        if msg == "shuffleAnimationDelay":
            self.set()

    def textChanged(self):
        try:
            setting.save("shuffleAnimationDelay", float(self.lineEdit.text()))
        except:
            return


class RetrySettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.DATE_TIME, "重试次数", "排座失败后重试的次数，设置更高的次数会提高成功概率，\n过高的次数可能会导致程序卡顿", parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("重试次数")
        self.lineEdit.setNewToolTip("排座失败后重试的次数")
        self.lineEdit.textEdited.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QIntValidator(1, 100000))

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(setting.read("shuffleRetryTime")))
        self.lineEdit.blockSignals(False)

    def setEvent(self, msg):
        if msg == "shuffleRetryTime":
            self.set()

    def textChanged(self):
        try:
            setting.save("shuffleRetryTime", int(self.lineEdit.text()))
        except:
            return


class FontSizeSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(FIF.FONT_SIZE, "字体大小", "名单字体大小", parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        self.lineEdit = AcrylicLineEdit(self)
        self.lineEdit.setPlaceholderText("字体大小")
        self.lineEdit.setNewToolTip("名单字体大小")
        self.lineEdit.textEdited.connect(self.textChanged)
        self.lineEdit.returnPressed.connect(self.textChanged)
        self.lineEdit.setValidator(QIntValidator(1, 100))

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(setting.read("fontSize")))
        self.lineEdit.blockSignals(False)

    def setEvent(self, msg):
        if msg == "fontSize":
            self.set()

    def textChanged(self):
        try:
            num = int(self.lineEdit.text())
            if 0 < num < 100:
                setting.save("fontSize", num)
        except:
            return


class RandomSeatSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(ZBF.contact_card, "随机组内座位排座", "开启后将随机组内座位排座，增加随机性", parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        self.switchButton = SwitchButton(self)
        self.switchButton.setNewToolTip("随机组内座位排座")
        self.switchButton.checkedChanged.connect(self.checkChanged)

        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.switchButton.blockSignals(True)
        self.switchButton.setChecked(setting.read("randomSeat"))
        self.switchButton.blockSignals(False)

    def setEvent(self, msg):
        if msg == "randomSeat":
            self.set()

    def checkChanged(self):
        try:
            setting.save("randomSeat", self.switchButton.checked)
        except:
            return


class RandomSeatGroupSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(ZBF.contact_card_group, "随机小组排座", "开启后将随机选择小组排座，增加随机性", parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        self.switchButton = SwitchButton(self)
        self.switchButton.setNewToolTip("随机小组排座")
        self.switchButton.checkedChanged.connect(self.checkChanged)

        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.switchButton.blockSignals(True)
        self.switchButton.setChecked(setting.read("randomSeatGroup"))
        self.switchButton.blockSignals(False)

    def setEvent(self, msg):
        if msg == "randomSeatGroup":
            self.set()

    def checkChanged(self):
        try:
            setting.save("randomSeatGroup", self.switchButton.checked)
        except:
            return


class SkipUnavailableSettingCard(SettingCard):

    def __init__(self, parent=None):
        super().__init__(ZBF.skip_forward_tab, "跳过不可用位置", "开启后若座位无解，将跳过该座位", parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        self.switchButton = SwitchButton(self)
        self.switchButton.setNewToolTip("跳过不可用位置")
        self.switchButton.checkedChanged.connect(self.checkChanged)

        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        setting.signalConnect(self.setEvent)
        self.window().initFinished.connect(self.set)

        self.set()

    def set(self):
        self.switchButton.blockSignals(True)
        self.switchButton.setChecked(setting.read("skipUnavailable"))
        self.switchButton.blockSignals(False)

    def setEvent(self, msg):
        if msg == "skipUnavailable":
            self.set()

    def checkChanged(self):
        try:
            setting.save("skipUnavailable", self.switchButton.checked)
        except:
            return


class SetKeyMessageBox(MessageBoxBase):
    def __init__(self, parent=None, keys: list = None):
        super().__init__(parent)

        self.titleLabel = TitleLabel("选择索引项目", self)

        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("请选择索引项目！")
        self.comboBox.addItems(keys)
        self.comboBox.setNewToolTip("请选择索引项目，将作为标签文本显示！")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.comboBox)
        self.widget.setMinimumSize(300, 100)

        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.result = None

    def yesButtonClicked(self):
        self.result = self.comboBox.currentText()
        self.done(self.comboBox.currentIndex())


class AddRuleMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleLabel = TitleLabel("新增规则", self)

        self.comboBox1 = ComboBox(self)
        self.comboBox1.setPlaceholderText("请选择匹配项目名称！")
        self.comboBox1.addItems(manager.person_keys)
        self.comboBox1.setNewToolTip("请选择匹配项目名称！")

        self.comboBox2 = ComboBox(self)
        self.comboBox2.setPlaceholderText("请选择匹配规则！")
        self.comboBox2.addItems(list(core.Rule.rule_names.values()))
        self.comboBox2.setNewToolTip("请选择匹配规则！")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.comboBox1)
        self.viewLayout.addWidget(self.comboBox2)
        self.widget.setMinimumSize(300, 100)

        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.result = None

    def yesButtonClicked(self):
        self.result = {"id": core.Rule.rule_names.inverse.get(self.comboBox2.currentText()), "key": self.comboBox1.currentText()}


class RuleCard(CardWidget):
    def __init__(self, parent, name: str, id: str, key: str):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.name = name
        self.rule_id = id
        self.rule_key = key

        self.contentLabel = BodyLabel(self)

        self.removeButton = ToolButton(FIF.CLOSE, self)
        self.removeButton.setFixedSize(24, 24)
        self.removeButton.clicked.connect(self.removeButtonClicked)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(8)

        self.hBoxLayout.addWidget(self.contentLabel, 0)
        self.hBoxLayout.addWidget(self.removeButton, 0)

        self.setLayout(self.hBoxLayout)

        self.setText()

    def setText(self):
        rule_name = core.Rule.rule_names.get(self.rule_id)
        self.contentLabel.setText(f"{self.rule_key} {rule_name}")
        self.setNewToolTip(self.name)

    def getRule(self):
        return core.Rule(self.rule_id, [self.rule_key])

    def removeButtonClicked(self):
        manager.removeRule(self.name)


class Manager(QWidget):
    PERSON_PARSER = core.PeopleParser()
    XLSX_PARSER = core.SeatTableParserXlsx()
    JSON_PARSER = core.SeatTableParserJson()
    EXPORTER = core.SeatTableExporter()

    def __init__(self):
        super().__init__()
        self.table: core.SeatTable = None
        self.person: dict = {}  # {id:{"person":core.Person, "widget": PersonWidget}}
        self.table_widget: dict = {}
        self.person_keys: list = []  # 名单表头列表
        self.rules: dict = {}

        try:
            self.mainPage = self.parent().mainPage
            self.editInterface = self.parent().mainPage.editInterface
            self.shuffleInterface = self.parent().mainPage.shuffleInterface
            self.tableInterface = self.parent().mainPage.tableInterface
            self.listInterface = self.parent().mainPage.editInterface.listInterface
            self.rulesInterface = self.parent().mainPage.editInterface.rulesInterface
        except:
            pass

    def getRuleJson(self, id: str, key: str):
        """
        获取Json格式的规则名称
        :param id: 规则id
        :param key: 匹配键
        :return:
        """
        return json.dumps({"id": id, "key": key}, indent=4, ensure_ascii=False)

    def addRule(self, id: str, key: str):
        """
        添加规则
        :param id: 规则id
        :param key: 匹配键
        :return:
        """
        name = self.getRuleJson(id, key)
        if name in self.rules:
            return

        self.rules[name] = {"id": id, "key": key}
        card = RuleCard(self, name, id, key)
        self.rulesInterface.cardGroup.addCard(card, name)

        self.rulesInterface.cardGroup.setTitle(f"当前规则数 ({len(self.rules)})")

    def removeRules(self):
        """
        删除所有规则
        """
        self.rules = {}
        self.rulesInterface.cardGroup.clearCard()
        self.rulesInterface.cardGroup.setTitle(f"当前规则数 (0)")

    def getRule(self, name: str):
        """
        获取规则信息
        :param name: 规则名称（Json）
        :return:
        """
        return self.rules.get(name, {})

    def getRuleCard(self, name: str):
        """
        获取规则卡片
        :param name: 规则名称（Json）
        :return:
        """
        return self.rulesInterface.cardGroup.getCard(name)

    def getRuleSet(self):
        """
        获取规则集
        :return:
        """
        rule_list = []

        for i in self.rulesInterface.cardGroup._cards:
            rule_list.append(i.getRule())

        return core.Ruleset(rule_list)

    def removeRule(self, name: str):
        """
        移除规则
        :param name: 规则名称（Json）
        :return:
        """
        if name not in self.rules:
            return
        manager.rulesInterface.cardGroup.removeCard(name)
        del self.rules[name]

        self.rulesInterface.cardGroup.setTitle(f"当前规则数 ({len(self.rules)})")

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
        self.removeTable()
        self.table = table

        self.table_widget = widget

        offset_r, offset_c = self.table.get_offset()
        for group in self.table.get_seat_groups():
            for seat in group.get_seats():
                r, c = seat.get_pos()
                widget = PersonWidgetTableBase(self, (r, c))
                self.table_widget[(r, c)] = widget
                self.tableInterface.gridLayout.addWidget(widget, r - offset_r, c - offset_c, 1, 1)
        rt, ct = self.table.get_size()
        for r in range(rt):
            for c in range(ct):
                if not self.tableInterface.gridLayout.itemAtPosition(r, c):
                    self.tableInterface.gridLayout.addWidget(QWidget(self), r, c, 1, 1)
                self.tableInterface.gridLayout.setRowStretch(r, 1)
                self.tableInterface.gridLayout.setColumnStretch(c, 1)

    def getPerson(self, id: str | core.Person | PersonWidget):
        """
        获取指定person
        :param id:
        :return:
        """
        if isinstance(id, str):
            return self.person.get(id, {}).get("person", None)
        elif isinstance(id, core.Person):
            return id
        elif isinstance(id, PersonWidget):
            return id.getPerson()
        return None

    def getPersonWidget(self, id: str | core.Person | PersonWidget):
        """
        获取指定PersonWidget
        :param id:
        :return:
        """
        if isinstance(id, str):
            return self.person.get(id, {}).get("widget", None)
        elif isinstance(id, core.Person):
            return self.person.get(id.get_id(), {}).get("widget", None)
        elif isinstance(id, PersonWidget):
            return id
        return None

    def getPeople(self):
        """
        获取所有core.Person
        :return:
        """
        return [p["person"] for p in self.person.values()]

    def getPersonWidgets(self):
        """
        获取所有PersonWidget
        :return:
        """
        return [p["widget"] for p in self.person.values()]

    def setPerson(self, person: core.Person | PersonWidget):
        """
        通过Person对象或PersonWidget对象向person列表新增Person
        :param person:
        """
        if isinstance(person, core.Person):
            person_widget = PersonWidget()
            person_widget.setPerson(person)
            id = person.get_id()
            if id in self.person.keys():
                existing_widget = self.person[id]["widget"]
                if isinstance(existing_widget.parent(), PersonWidgetBase):
                    existing_widget.parent().removePerson()
                elif isinstance(existing_widget.parent(), PersonWidgetTableBase):
                    existing_widget.parent().removePerson()
                existing_widget.deleteLater()
            self.person[id] = {"person": person, "widget": person_widget}
        elif isinstance(person, PersonWidget):
            id = person.getID()
            if id in self.person.keys():
                existing_widget = self.person[id]["widget"]
                if isinstance(existing_widget.parent(), PersonWidgetBase):
                    existing_widget.parent().removePerson()
                elif isinstance(existing_widget.parent(), PersonWidgetTableBase):
                    existing_widget.parent().removePerson()
                existing_widget.deleteLater()
            self.person[id] = {"person": person.getPerson(), "widget": person}

    def setPeople(self, people: list[core.Person | PersonWidget]):
        """
        设置多个person
        :param people:
        """
        for person in people:
            self.setPerson(person)

    def hasPerson(self, id: str | core.Person | PersonWidget):
        """
        是否有指定person
        :param id:
        :return:
        """
        if isinstance(id, str):
            return id in self.person.keys()
        elif isinstance(id, core.Person):
            return id.get_id() in self.person.keys()
        elif isinstance(id, PersonWidget):
            return id.getID() in self.person.keys()
        return False

    def removePerson(self, id: str | core.Person | PersonWidget):
        """
        移除指定person，并从ui上移除
        :param id: person
        :return:
        """
        if isinstance(id, str):
            if id in self.person.keys():
                id = id
        elif isinstance(id, core.Person):
            if id.get_id() in self.person.keys():
                id = id.get_id()
        elif isinstance(id, PersonWidget):
            if id.getID() in self.person.keys():
                id = id.getID()
        else:
            return
        v = self.person.pop(id, None)
        if isinstance(v, dict):
            widget = v["widget"]
            if isinstance(widget.parent(), PersonWidgetBase):
                widget.parent().removePerson()
            elif isinstance(widget.parent(), PersonWidgetTableBase):
                widget.parent().removePerson()
            widget.deleteLater()

    def clearPerson(self):
        """
        清空person列表
        """
        for widget in self.getPersonWidgets():
            if isinstance(widget.parent(), PersonWidgetBase):
                widget.parent().removePerson()
            elif isinstance(widget.parent(), PersonWidgetTableBase):
                widget.parent().removePerson()
            widget.deleteLater()
        self.person = {}

    def setListPeople(self, move: bool = True):
        """
        根据当前的person列表重新创建列表
        :param move: 是否从表格移动人到列表
        """
        self.listInterface.cardGroup.blockSignals(True)
        self.listInterface.cardGroup.clearCard()
        count = 0
        for k, v in self.person.items():
            person_widget: PersonWidget = v["widget"]
            parent = person_widget.parent()
            if move or not isinstance(parent, PersonWidgetTableBase) or person_widget.move_back:
                widget = PersonWidgetBase(self.listInterface, self.listInterface.cardGroup)
                person_widget.move_back = False
                self.listInterface.cardGroup.addCard(widget, k)
                if isinstance(parent, PersonWidgetTableBase) or not parent:
                    widget.setPerson(person_widget, True)
                else:
                    widget.setPerson(person_widget, False)
                count += 1
        self.personNumberChanged(count)
        self.listInterface.cardGroup.blockSignals(False)

    def personNumberChanged(self, number: int):
        self.listInterface.cardGroup.setTitle(f"当前人数 ({number}/{len(self.person)})")

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

    def getTablePerson(self, pos: (int, int)):
        """
        获取指定位置的人员
        :return: Person
        """
        widget: PersonWidgetTableBase | None = self.getTableWidget(tuple(pos))
        if widget:
            return widget.getPerson().getPerson()
        return None

    def getTablePeople(self):
        """
        获取所有人员
        :return: dict
        """
        return {k: v.getPerson().getPerson() for k, v in self.table_widget.items() if v.getPerson() is not None and v.getPerson().getPerson() is not None}

    def setTablePerson(self, pos: (int, int), name: str | core.Person | PersonWidget):
        """
        设置表格指定位置的人
        :param name: 人的名字，可以为字符串，Person对象或Person组件
        :param pos: （行，列）
        :return: widget
        """
        person = self.getPersonWidget(name)
        widget = self.getTableWidget(tuple(pos))
        if widget:
            widget.setPerson(person)
            logging.info(f"设置表格位置{pos}的人为{person.getName()}！")
            return True
        return False

    def removeTablePerson(self, pos: (int, int)):
        """
        移除表格指定位置的人并放回列表
        :param pos:
        """
        widget = self.table_widget.get(tuple(pos))
        if widget:
            person = widget.getPerson()
            person.move_back = True
            self.setListPeople(False)

    def clearTablePerson(self):
        """
        清空表格中的所有人，并放回列表
        """
        self.setListPeople(True)
        if self.table:
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
        self.setListPeople(True)
        for r in range(self.tableInterface.gridLayout.rowCount()):
            self.tableInterface.gridLayout.setRowStretch(r, 0)
        for c in range(self.tableInterface.gridLayout.columnCount()):
            self.tableInterface.gridLayout.setColumnStretch(c, 0)
        self.table_widget = {}
        self.table = None


manager = Manager()
