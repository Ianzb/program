from PyQt5 import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets.menu import *
from qframelesswindow import *
from Windows.zb import *
from .gallery_interface import GalleryInterface


class mainInterface(GalleryInterface):

    def __init__(self, parent=None):
        super().__init__(
            title=program_name,
            subtitle="主页",
            parent=parent
        )
        self.setObjectName("主页")

        self.pushButton1_1 = PrimaryPushButton("开始整理+清理", self)
        self.pushButton1_1.clicked.connect(self.btn1_1)
        if readSetting("sort") == "":
            self.pushButton1_1.setEnabled(False)
        self.toolButton1_2 = ToolButton(FIF.FOLDER, self)
        self.toolButton1_2.clicked.connect(self.btn1_2)
        self.pushButton1_3 = PushButton("设置整理目录", self, FIF.FOLDER_ADD)
        self.pushButton1_3.clicked.connect(self.btn1_3)
        self.pushButton1_4 = PushButton("设置微信目录", self, FIF.FOLDER_ADD)
        self.pushButton1_4.clicked.connect(self.btn1_4)
        self.addExampleCard(
            title=self.tr("一键整理+清理"),
            widget=[self.pushButton1_1, self.toolButton1_2, self.pushButton1_3, self.pushButton1_4],
        )
        self.pushButton2_1 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.pushButton2_1.clicked.connect(self.btn2_1)
        self.addExampleCard(
            title=self.tr("快捷功能"),
            widget=[self.pushButton2_1],
        )
        self.pushButton3_1 = PushButton("查看MC最新版本", self, FIF.CHECKBOX)
        self.pushButton3_1.clicked.connect(self.btn3_1)
        self.addExampleCard(
            title=self.tr("游戏功能"),
            widget=[self.pushButton3_1],
        )

    def btn1_1(self):
        if readSetting("sort") == "":
            InfoBar.warning(
                title="警告",
                content="当前未设置整理文件目录，无法整理！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )

            return
        if readSetting("wechat") == "":
            self.infoBar = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title="提示",
                content="当前未设置微信文件目录，无法整理微信文件！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
            self.infoBar.show()
        self.pushButton1_1.setEnabled(False)
        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        self.thread = newThread(1)
        self.thread.signal.connect(lambda: self.btn1_1_2("整理完毕"))
        self.thread.start()

    def btn1_1_2(self, content="提示内容"):
        self.stateTooltip.setState(True)
        self.stateTooltip.setContent(content)
        self.pushButton1_1.setEnabled(True)

    def btn1_2(self):
        if readSetting("sort") == "" or readSetting("wechat") == "":
            return
        os.startfile(readSetting("sort"))

    def btn1_3(self):
        path = readSetting("sort")
        get = QFileDialog.getExistingDirectory(self, "选择整理文件目录", path)
        if not os.path.exists(get):
            return
        saveSetting("sort", str(get))

    def btn1_4(self):
        path = readSetting("wechat")
        get = QFileDialog.getExistingDirectory(self, "选择微信WeChat Files文件夹目录", path)
        if not os.path.exists(get):
            return
        saveSetting("wechat", str(get))

    def btn2_1(self):
        self.pushButton2_1.setEnabled(False)
        self.thread = newThread(2)
        self.thread.signal.connect(self.btn2_1_2)
        self.thread.start()

    def btn2_1_2(self, msg):
        self.pushButton2_1.setEnabled(True)

    def btn3_1(self):
        self.pushButton3_1.setEnabled(False)
        self.thread = newThread(5)
        self.thread.signal.connect(self.btn3_1_2)
        self.thread.start()

    def btn3_1_2(self, msg):
        self.infoBar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="MC最新版本",
            content=msg,
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=10000,
            parent=self
        )
        self.infoBar.show()
        self.pushButton3_1.setEnabled(True)
