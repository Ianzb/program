import string
import traceback

from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, setting, window, sf, progressCenter, addonInfo
    program = addonBase.program
    setting = addonBase.setting
    window = addonBase.window
    progressCenter = addonBase.progressCenter
    addonInfo = addonBase.addonInfo

    setting.adds({"messageTitle": "",
                  "password": "",
                  "messageContent": "",
                  "messageEnabled": False,
                  "canCloseMessage": True,
                  "messageMove": False,
                  "monitorPath": [],
                  "autoCopy": False,
                  "copyPath": zb.joinPath(program.DATA_PATH, "复制"),
                  })


def addonDelete():
    pass

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


class SetPasswordMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleLabel = TitleLabel("设置程序密码锁", self)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText("在此处输入密码！")
        self.lineEdit.setNewToolTip("在此处输入密码！")
        self.lineEdit.setText(setting.read("password"))
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.lineEdit)
        self.widget.setMinimumSize(300, 100)

        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.connect(self.yesButtonClicked)

    def yesButtonClicked(self):
        setting.save("password", self.lineEdit.text())


class EmptySplashScreen(QWidget):
    """ Splash screen """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        parent.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        if obj is self.parent():
            if e.type() == QEvent.Resize:
                self.setFixedSize(e.size())

        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)

        # draw background
        c = 32 if isDarkTheme() else 255
        painter.setBrush(QColor(c, c, c))
        painter.drawRect(self.rect())


class EnterPasswordMessageBox(MessageBoxBase):
    def __init__(self, parent=None, splashScreen=None, page=None):
        super().__init__(parent)
        self.splashScreen = splashScreen
        self.page = page

        self.titleLabel = TitleLabel("请输入Seewo安全密码！", self)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText("在此处输入密码！")
        self.lineEdit.setNewToolTip("在此处输入密码！")
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.lineEdit)
        self.widget.setMinimumSize(300, 100)

        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.connect(self.yesButtonClicked)
        self.cancelButton.clicked.connect(self.closeButtonClicked)

    def yesButtonClicked(self):

        if self.lineEdit.text() == setting.read("password"):

            self.page.enterPassWordMessageBox = None
            self.splashScreen.close()
            self.splashScreen.deleteLater()

            del self.splashScreen
        else:
            self.closeButtonClicked()

    def closeButtonClicked(self):
        self.splashScreen.close()
        self.splashScreen.deleteLater()

        del self.splashScreen
        self.window().hide()
        self.page.enterPassWordMessageBox = None
        self.deleteLater()


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
            self.yesSignal.emit()
            self.deleteLater()
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
    setHistoryText = pyqtSignal(str)
    copySignal = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CLIPPING_TOOL)
        self.setTitle("Seewo工具箱")

        self.copy_stat = {}

        self.card1 = zbw.GrayCard("程序安全锁", self)

        self.passwordButton = PrimaryPushButton("设置安全密码", self, FIF.VPN)
        self.passwordButton.clicked.connect(self.passwordButtonClicked)

        self.card1.addWidget(self.passwordButton)

        self.card2 = zbw.GrayCard("自动弹窗", self)

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

        self.card2.addWidget(self.setMessageButton)
        self.card2.addWidget(self.testMessageButton)
        self.card2.addWidget(self.messageCheckBox, 0, Qt.AlignCenter)
        self.card2.addWidget(self.moveCheckBox, 0, Qt.AlignCenter)
        self.card2.addWidget(self.canCloseCheckBox, 0, Qt.AlignCenter)

        self.card3 = zbw.GrayCard("文件复制", self)

        self.detectButton = PrimaryPushButton("监视盘符", self, FIF.FOLDER)
        self.detectButton.clicked.connect(self.detectButtonClicked)

        self.showButton = PushButton("打开复制目录", self, FIF.FOLDER)
        self.showButton.clicked.connect(lambda: zb.showFile(setting.read("copyPath")))

        self.label1 = BodyLabel("自动复制", self)

        self.autoCopyButton = SwitchButton(self)
        self.autoCopyButton.setChecked(setting.read("autoCopy"))
        self.autoCopyButton.checkedChanged.connect(self.autoCopyButtonClicked)

        self.card3.addWidget(self.detectButton)
        self.card3.addWidget(self.showButton)
        self.card3.addWidget(self.label1, 0, Qt.AlignCenter)
        self.card3.addWidget(self.autoCopyButton, 0, Qt.AlignCenter)

        self.label2 = StrongBodyLabel(f"复制路径：{setting.read("copyPath") or "无"}", self)

        self.fileChooser = zbw.FileChooser(self)
        self.fileChooser.setMode("folder")
        self.fileChooser.setDescription("复制路径")
        self.fileChooser.setOnlyOne(True)
        self.fileChooser.setDefaultPath(setting.read("copyPath"))
        self.fileChooser.fileChoosedSignal.connect(self.fileChoosed)

        self.statusLabel = StrongBodyLabel("当前状态：空闲。", self)
        self.historyLabel = BodyLabel("", self)
        self.historyLabel.setWordWrap(True)
        self.historyLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.historyLabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)
        self.vBoxLayout.addWidget(self.card3)
        self.vBoxLayout.addWidget(self.label2)
        self.vBoxLayout.addWidget(self.fileChooser, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.statusLabel)
        self.vBoxLayout.addWidget(self.historyLabel)

        if setting.read("messageEnabled"):
            program.THREAD_POOL.submit(self._waitAndShowMessage)
            self.showMessageSignal.connect(self.showMessage)
        program.THREAD_POOL.submit(self.autoCopy)

        setting.connect(self.set)
        self.setHistoryText.connect(self.addHistory)

        self.copySignal.connect(self.copyFile)

        self.enterPassWordMessageBox = None

        self.window().showSignal.connect(self.onWindowShow)

        self.onWindowShow()

    def onWindowShow(self):
        if not setting.read("password"):
            return
        if self.enterPassWordMessageBox:
            return
        self.splashScreen = EmptySplashScreen(self.window())
        self.splashScreen.setFixedSize(self.window().size())
        self.splashScreen.show()
        self.enterPassWordMessageBox = EnterPasswordMessageBox(self.window(), self.splashScreen, self)
        self.enterPassWordMessageBox.show()
        self.enterPassWordMessageBox.widget.raise_()

    def addHistory(self, text: str):
        full_text = f"{time.strftime("%Y-%m-%d %H:%M:%S")} {text}\n" + self.historyLabel.text()
        self.historyLabel.setText(full_text)

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

    def passwordButtonClicked(self):
        messageBox = SetPasswordMessageBox(self.window())
        messageBox.show()

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
                logging.error(f"获取盘符 {drive_letter} 的硬盘名称失败: {traceback.format_exc()}")
            return None

        while True:
            time.sleep(1)
            if setting.read("autoCopy") and setting.read("copyPath") and zb.isDir(setting.read("copyPath")):
                self.statusLabel.setText("当前状态：监视中...")
                for name in setting.read("monitorPath"):
                    path = name + r":/"
                    if zb.existPath(path):
                        if self.copy_stat.get(name):
                            continue
                        disc_name = get_disk_name(name) or "UnknownDisk"
                        target_path = zb.joinPath(setting.read("copyPath"), name, disc_name)
                        try:
                            logging.info(f"正在复制{path}到{target_path}！")
                            self.copySignal.emit(name, path, target_path)
                        except:
                            logging.warning(f"复制{path}到{setting.read("copyPath")}失败，报错信息：{traceback.format_exc()}！")

                    else:
                        self.copy_stat[name] = False
            else:
                self.statusLabel.setText("当前状态：空闲。")

    def copyFile(self, name, src, dst):
        card = progressCenter.addTask(True, True, False, False, False)
        card.setTitle(f"复制")
        card.setContent(f"正在复制{name}到{dst}...")
        card.start()
        program.THREAD_POOL.submit(self._copyFile, name, src, dst, card)

    def _copyFile(self, name, src, dst, card):
        self.copy_stat[name] = True
        self.setHistoryText.emit(f"正在复制{name}盘...")
        self.statusLabel.setText(f"当前状态：正在复制{name}盘...")
        try:
            zb.copyPath(src, dst)
            card.setContentSignal.emit(f"复制{src}到{dst}成功！")
            card.finish(True)
        except:
            card.finish(False)
            card.setContentSignal.emit(f"复制{src}到{dst}成功！")
            logging.warning(f"复制{src}到{dst}失败，报错信息：{traceback.format_exc()}！")
        self.setHistoryText.emit(f"复制{name}盘到{dst}成功！")
        self.statusLabel.setText(f"当前状态：复制{name}盘成功！")
