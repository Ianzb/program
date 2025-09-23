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

        self.card1.addWidget(self.setMessageButton)
        self.card1.addWidget(self.testMessageButton)
        self.card1.addWidget(self.messageCheckBox, 0, Qt.AlignCenter)

        self.vBoxLayout.addWidget(self.card1)

        if setting.read("messageEnabled"):
            program.THREAD_POOL.submit(self._waitAndShowMessage)
            self.showMessageSignal.connect(self.showMessage)

    def messageButtonClicked(self):
        messageBox = SetMessageMessageBox(self.window())
        messageBox.show()

    def messageCheckBoxClicked(self):
        setting.save("messageEnabled", self.messageCheckBox.isChecked())

    def _waitAndShowMessage(self):
        import time
        time.sleep(5)
        self.showMessageSignal.emit()

    def showMessage(self):
        messageBox = Dialog(setting.read("messageTitle"), setting.read("messageContent"))
        messageBox.setWindowFlags(Qt.WindowStaysOnTopHint)
        messageBox.cancelButton.hide()
        messageBox.contentLabel.setSelectable()
        messageBox.contentLabel.setTextFormat(Qt.TextFormat.RichText)
        messageBox.show()
