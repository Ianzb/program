import logging

from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, setting, window
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window
    setting.adds({"messageTitle": "",
                  "messageContent": "",
                  "messageEnabled": False,
                  "canCloseMessage": True,
                  "messageMove": False,
                  })


def addonWidget():
    return SeewoPage(window)


class SetMessageMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置文本")

        self.titleLabel = TitleLabel("设置弹窗内容", self)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText("在此处输入弹窗标题！")
        self.lineEdit.setNewToolTip("在此处输入弹窗标题！")
        self.lineEdit.setText(setting.read("messageTitle"))

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("在此处输入文本内容，支持HTML格式！")
        self.textEdit.setNewToolTip("在此处输入文本内容，支持HTML格式！")
        self.textEdit.setPlainText(setting.read("messageContent"))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.lineEdit)
        self.viewLayout.addWidget(self.textEdit)
        self.widget.setMinimumSize(600, 300)

        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.connect(self.yesButtonClicked)

    def yesButtonClicked(self):
        setting.save("messageTitle", self.lineEdit.text())
        setting.save("messageContent", self.textEdit.toPlainText())


class FakeDialog(Dialog):
    def __init__(self, parent=None):
        super().__init__("提示", "是否确认关闭？")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.yesButton.setText("否")
        self.cancelButton.setText("否")
        self.setModal(True)


class MessageDialog(zbw.ScrollDialog):
    def __init__(self, parent=None):
        super().__init__(setting.read("messageTitle"), setting.read("messageContent"), parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.yesButton.hide()
        self.cancelButton.hide()
        self.contentLabel.setSelectable()
        self.contentLabel.setWordWrap(True)
        self.contentLabel.setTextFormat(Qt.TextFormat.RichText)

        self.closeButton = PrimaryPushButton("关闭", self)
        self.closeButton.clicked.connect(self.closeButtonClicked)

        self.buttonLayout.addWidget(self.closeButton)

        self.setFixedWidth(700)
        self.setMaximumHeight(300)

        # 窗口移动功能
        if setting.read("messageMove"):
            from PyQt5.QtCore import QTimer
            self._dx = 1
            self._dy = 1
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._move_window)
            self._timer.start(5)

    def _move_window(self):
        from PyQt5.QtWidgets import QApplication
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(self)
        current_rect = self.geometry()

        new_x = current_rect.x() + self._dx
        new_y = current_rect.y() + self._dy

        # 检测边缘并反弹
        if new_x <= screen_rect.left() or new_x + current_rect.width() >= screen_rect.right():
            self._dx = -self._dx
        if new_y <= screen_rect.top() or new_y + current_rect.height() >= screen_rect.bottom():
            self._dy = -self._dy

        self.move(current_rect.x() + self._dx, current_rect.y() + self._dy)

    def closeButtonClicked(self):
        if setting.read("canCloseMessage"):
            if hasattr(self, '_timer'):
                self._timer.stop()
            self.accept()
            self.yesSignal.emit()
        else:
            messageBox = FakeDialog(self)
            messageBox.show()


class SeewoPage(zbw.BasicTab):
    showMessageSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CLIPPING_TOOL)
        self.setTitle("Seewo工具箱")

        self.card1 = zbw.GrayCard("自动弹窗", self)

        self.setMessageButton = PrimaryPushButton("设置弹窗文本", self, FIF.EDIT)
        self.setMessageButton.clicked.connect(self.messageButtonClicked)

        self.testMessageButton = PushButton("测试弹窗", self, FIF.PLAY)
        self.testMessageButton.clicked.connect(self.showMessage)

        self.messageCheckBox = CheckBox("自动弹窗", self)
        self.messageCheckBox.setChecked(setting.read("messageEnabled"))
        self.messageCheckBox.clicked.connect(self.messageCheckBoxClicked)

        self.moveCheckBox = CheckBox("窗口移动", self)
        self.moveCheckBox.setChecked(setting.read("messageMove"))
        self.moveCheckBox.clicked.connect(self.moveCheckBoxClicked)

        self.canCloseCheckBox = CheckBox("允许关闭弹窗", self)
        self.canCloseCheckBox.setChecked(setting.read("canCloseMessage"))
        self.canCloseCheckBox.clicked.connect(self.canCloseCheckBoxClicked)

        self.card1.addWidget(self.setMessageButton)
        self.card1.addWidget(self.testMessageButton)
        self.card1.addWidget(self.messageCheckBox, 0, Qt.AlignCenter)
        self.card1.addWidget(self.moveCheckBox, 0, Qt.AlignCenter)
        self.card1.addWidget(self.canCloseCheckBox, 0, Qt.AlignCenter)

        self.vBoxLayout.addWidget(self.card1)

        if setting.read("messageEnabled"):
            program.THREAD_POOL.submit(self._waitAndShowMessage)
            self.showMessageSignal.connect(self.showMessage)

    def messageButtonClicked(self):
        messageBox = SetMessageMessageBox(self.window())
        messageBox.show()

    def messageCheckBoxClicked(self):
        setting.save("messageEnabled", self.messageCheckBox.isChecked())

    def moveCheckBoxClicked(self):
        setting.save("messageMove", self.moveCheckBox.isChecked())

    def canCloseCheckBoxClicked(self):
        setting.save("canCloseMessage", self.canCloseCheckBox.isChecked())

    def _waitAndShowMessage(self):
        import time
        time.sleep(2.5)
        self.showMessageSignal.emit()

    def showMessage(self):
        messageBox = MessageDialog()
        messageBox.show()
