import logging
import string
import time
import traceback

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
                  "monitorPath": [],
                  "autoCopy": False,
                  "copyPath": zb.joinPath(program.DATA_PATH, "复制"),
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


class DetectFolderEditMessageBox(MessageBoxBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("监视盘符", self)

        self.textEdit = TextEdit(self)
        self.textEdit.setPlaceholderText("输入盘符名称\n一行一个")
        self.textEdit.setText("\n".join(setting.read("monitorPath")))
        self.textEdit.setNewToolTip("输入盘符名称\n一行一个")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.textEdit)

        self.yesButton.setText("确定")
        self.yesButton.clicked.connect(self.yesButtonClicked)

        self.resetButton = PushButton("重置", self.buttonGroup)
        self.resetButton.clicked.connect(self.resetButtonClicked)

        self.buttonLayout.insertWidget(1, self.resetButton, 1, Qt.AlignVCenter)

        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(350)

    def yesButtonClicked(self):
        setting.save("monitorPath", sorted(list(set([i.upper() for i in self.textEdit.toPlainText().split("\n") if i in string.ascii_letters and len(i) == 1]))))

    def resetButtonClicked(self):
        setting.reset("monitorPath")
        self.accept()
        self.accepted.emit()


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

        self.card2 = zbw.GrayCard("文件复制", self)

        self.detectButton = PrimaryPushButton("监视盘符", self, FIF.FOLDER)
        self.detectButton.clicked.connect(self.detectButtonClicked)

        self.showButton = PushButton("打开复制目录", self, FIF.FOLDER)
        self.showButton.clicked.connect(lambda: zb.showFile(setting.read("copyPath")))

        self.label1 = BodyLabel("自动复制", self)

        self.autoCopyButton = SwitchButton(self)
        self.autoCopyButton.setChecked(setting.read("autoCopy"))
        self.autoCopyButton.checkedChanged.connect(self.autoCopyButtonClicked)

        self.card2.addWidget(self.detectButton)
        self.card2.addWidget(self.showButton)
        self.card2.addWidget(self.label1, 0, Qt.AlignCenter)
        self.card2.addWidget(self.autoCopyButton, 0, Qt.AlignCenter)

        self.label2 = StrongBodyLabel(f"复制路径：{setting.read("copyPath") or "无"}", self)

        self.fileChooser = zbw.FileChooser(self)
        self.fileChooser.setMode("folder")
        self.fileChooser.setDescription("复制路径")
        self.fileChooser.setOnlyOne(True)
        self.fileChooser.setDefaultPath(setting.read("copyPath"))
        self.fileChooser.fileChoosedSignal.connect(self.fileChoosed)

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)
        self.vBoxLayout.addWidget(self.label2)
        self.vBoxLayout.addWidget(self.fileChooser, 0, Qt.AlignCenter)

        if setting.read("messageEnabled"):
            program.THREAD_POOL.submit(self._waitAndShowMessage)
            self.showMessageSignal.connect(self.showMessage)
        program.THREAD_POOL.submit(self.autoCopy)

        setting.signalConnect(self.set)

    def fileChoosed(self, paths):
        path = paths[0]
        if zb.isDir(path):
            setting.save("copyPath", path)

    def set(self, name):
        if name == "autoCopy":
            self.autoCopyButton.setChecked(setting.read("autoCopy"))
        elif name == "messageEnabled":
            self.messageCheckBox.setChecked(setting.read("messageEnabled"))
        elif name == "messageMove":
            self.moveCheckBox.setChecked(setting.read("messageMove"))
        elif name == "canCloseMessage":
            self.canCloseCheckBox.setChecked(setting.read("canCloseMessage"))
        elif name == "copyPath":
            self.label2.setText(f"复制路径：{setting.read("copyPath") or "无"}")
            self.fileChooser.setDefaultPath(setting.read("copyPath"))

    def autoCopyButtonClicked(self, checked):
        setting.save("autoCopy", self.autoCopyButton.isChecked())

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

    def detectButtonClicked(self):
        messageBox = DetectFolderEditMessageBox(self.window())
        messageBox.show()

    def autoCopy(self):
        def get_disk_name(drive_letter):
            """
            获取指定盘符的硬盘产品硬件名称。
            :param drive_letter: 盘符，例如 'C'
            :return: 硬盘产品名称或 None
            """
            try:
                return time.strftime("%Y-%m-%d %H%M%S")
                # from .wmi import WMI
                # c = WMI()
                # for disk in c.Win32_LogicalDisk():
                #     if disk.DeviceID == f"{drive_letter}:":
                #         for partition in c.Win32_DiskPartition():
                #             if partition.DeviceID in disk.DeviceID:
                #                 for physical_disk in c.Win32_DiskDrive():
                #                     if partition.DeviceID in physical_disk.DeviceID:
                #                         return physical_disk.Model
            except Exception as e:
                logging.error(f"获取盘符 {drive_letter} 的硬盘名称失败: {traceback.print_exc()}")
            return None

        copy = {}
        while True:
            time.sleep(5)
            if setting.read("autoCopy") and setting.read("copyPath") and zb.isDir(setting.read("copyPath")):
                for name in setting.read("monitorPath"):
                    path = name + r":/"
                    if zb.existPath(path):
                        if copy.get(name):
                            return
                        try:
                            disc_name = get_disk_name(name) or "UnknownDisk"
                            logging.info(f"正在复制{path}到{zb.joinPath(setting.read("copyPath"), name, disc_name)}！")
                            zb.copyPath(path, zb.joinPath(setting.read("copyPath"), name, disc_name))
                            copy[name] = True
                        except:
                            logging.warning(f"复制{path}到{setting.read('copyPath')}失败，报错信息：{traceback.format_exc()}！")
                    else:
                        copy[name] = False
