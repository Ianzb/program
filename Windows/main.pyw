from PyQt5 import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.components.widgets.menu import *
from qframelesswindow import *

from zb import *

weight = 450
height = 350

saveSetting(abs_cache, os.getpid())


# 删除最大化按钮
class TitleBar(StandardTitleBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.maxBtn.setParent(None)
        self._isDoubleClickEnabled = False


# 头像绘制
class AvatarWidget(NavigationWidget):
    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)

    def paintEvent(self, e):
        avatar = QImage("zb.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        paint1 = QPainter(self)
        paint1.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        paint1.setPen(Qt.NoPen)
        if self.isPressed:
            paint1.setOpacity(0.7)
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            paint1.setBrush(QColor(c, c, c, 10))
            paint1.drawRoundedRect(self.rect(), 5, 5)
        paint1.setBrush(QBrush(avatar))
        paint1.translate(8, 6)
        paint1.drawEllipse(0, 0, 24, 24)
        paint1.translate(-8, -6)
        if not self.isCompacted:
            paint1.setPen(Qt.white if isDarkTheme() else Qt.black)
            font = QFont("Segoe UI")
            font.setPixelSize(14)
            paint1.setFont(font)
            paint1.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, "Ianzb")


# 多线程操作
class newThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    def run(self):
        mode = self.mode
        if mode == 1:
            MyThread(lambda: clearRubbish())
            MyThread(lambda: clearCache())
            clearDesk(readSetting("sort"))
            if readSetting("wechat") != "":
                clearWechat(readSetting("wechat"), readSetting("sort"))
            clearFile(readSetting("sort"))
            self.signal.emit("完成")
        if mode == 2:
            cmd("taskkill /f /im explorer.exe")
            self.signal.emit("完成")
            cmd("start C:/windows/explorer.exe")
        if mode == 3:
            self.signal.emit("开始")
            link = "https://ianzb.github.io/program/Windows/"
            res = requests.get(urlJoin(link, "index.html"))
            res.encoding = "UTF-8"
            soup = bs4.BeautifulSoup(res.text, "lxml")
            data = soup.find_all(name="div", class_="download", text=re.compile("."))
            for i in range(len(data)): data[i] = data[i].text.strip()
            self.signal.emit("总共" + str(len(data)))
            for i in range(len(data)):
                self.signal.emit(data[i])
                download(urlJoin(link, data[i]))
            self.signal.emit("完成")
        if mode == 4:
            for i in range(len(lib_list)):
                self.signal.emit(str(i))
                pipInstall(lib_list[i])
            self.signal.emit("完成")
        if mode == 5:
            str1 = getMc()
            self.signal.emit(str1)

        if mode == 8:
            while True:
                time.sleep(0.1)
                if readSetting("show") == "1":
                    saveSetting("show", "0")
                    self.signal.emit("展示")


class tab1(QFrame, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("功能")
        self.pushButton1 = PrimaryPushButton("一键整理+清理", self)
        self.pushButton1.clicked.connect(self.btn11)
        self.pushButton1.move(0, 0)
        self.pushButton1.resize(300, 35)
        if readSetting("sort") == "":
            self.pushButton1.setEnabled(False)
        self.toolButton1 = ToolButton(FIF.FOLDER, self)
        self.toolButton1.clicked.connect(self.btn12)
        self.toolButton1.move(300, 0)
        self.toolButton1.resize(100, 35)
        self.pushButton2 = PushButton("重启文件资源管理器", self, FIF.SYNC)
        self.pushButton2.clicked.connect(self.btn20)
        self.pushButton2.move(0, 35)
        self.pushButton2.resize(200, 35)
        self.pushButton3 = PushButton("查看MC最新版本", self, FIF.CHECKBOX)
        self.pushButton3.clicked.connect(self.btn50)
        self.pushButton3.move(200, 35)
        self.pushButton3.resize(200, 35)

    def btn10(self, content="提示内容"):
        self.stateTooltip.setState(True)
        self.stateTooltip.setContent(content)
        w.show()
        self.pushButton1.setEnabled(True)

    def btn11(self):
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
        self.pushButton1.setEnabled(False)
        self.stateTooltip = StateToolTip("正在整理文件", "请耐心等待", self)
        self.stateTooltip.move(143, 264)
        self.stateTooltip.show()
        self.thread = newThread(1)
        self.thread.signal.connect(lambda: self.btn10("整理完毕"))
        self.thread.start()

    def btn12(self):
        if readSetting("sort") == "" or readSetting("wechat") == "":
            return
        os.startfile(readSetting("sort"))

    def btn20(self):
        self.pushButton2.setEnabled(False)
        self.thread = newThread(2)
        self.thread.signal.connect(self.btn21)
        self.thread.start()

    def btn21(self, msg):
        self.pushButton2.setEnabled(True)

    def btn50(self):
        self.pushButton3.setEnabled(False)
        self.thread = newThread(5)
        self.thread.signal.connect(self.btn51)
        self.thread.start()

    def btn51(self, msg):
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
        self.pushButton3.setEnabled(True)


class tab3(QFrame, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("设置")
        self.pushButton1 = PushButton("选择整理文件目录", self, FIF.FOLDER_ADD)
        self.pushButton1.clicked.connect(self.btn10)
        self.pushButton1.move(0, 0)
        self.pushButton1.resize(200, 35)
        self.pushButton2 = PushButton("选择微信文件目录", self, FIF.FOLDER_ADD)
        self.pushButton2.clicked.connect(self.btn11)
        self.pushButton2.move(200, 0)
        self.pushButton2.resize(200, 35)
        self.pushButton3 = PushButton("创建桌面快捷方式", self, FIF.ADD)
        self.pushButton3.clicked.connect(self.btn20)
        self.pushButton3.move(0, 35)
        self.pushButton3.resize(200, 35)
        self.pushButton4 = PushButton("添加至开始菜单列表", self, FIF.ADD)
        self.pushButton4.clicked.connect(self.btn21)
        self.pushButton4.move(200, 35)
        self.pushButton4.resize(200, 35)
        self.pushButton5 = PushButton("打开程序安装目录", self, FIF.LINK)
        self.pushButton5.clicked.connect(self.btn30)
        self.pushButton5.move(0, 70)
        self.pushButton5.resize(200, 35)
        self.pushButton6 = PushButton("查看程序运行日志", self, FIF.LINK)
        self.pushButton6.clicked.connect(self.btn31)
        self.pushButton6.move(200, 70)
        self.pushButton6.resize(200, 35)
        self.pushButton7 = PushButton("安装运行库", self, FIF.DOWNLOAD)
        self.pushButton7.clicked.connect(self.btn40)
        self.pushButton7.move(0, 280)
        self.pushButton7.resize(200, 35)
        self.pushButton8 = PrimaryPushButton("检查更新", self, FIF.DOWNLOAD)
        self.pushButton8.clicked.connect(self.btn42)
        self.pushButton8.move(200, 280)
        self.pushButton8.resize(200, 35)
        self.progressBar = ProgressBar(self)
        self.progressBar.move(0, 245)
        self.progressBar.setGeometry(0, 245, 400, 20)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setHidden(True)
        self.label = QLabel(self)
        self.label.move(0, 245)
        self.label.resize(400, 35)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("等线", 10))
        self.label.setHidden(True)
        self.label.setText("")

        self.checkBox = CheckBox("开机自启动", self)
        self.checkBox.clicked.connect(self.btn60)
        self.checkBox.move(0, 105)
        self.checkBox.resize(200, 35)
        if readSetting("startupdate") == "1":
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)

    def btn10(self):
        path = readSetting("sort")
        get = QFileDialog.getExistingDirectory(self, "选择整理文件目录", path)
        if not os.path.exists(get):
            return
        saveSetting("sort", str(get))

    def btn11(self):
        path = readSetting("wechat")
        get = QFileDialog.getExistingDirectory(self, "选择微信WeChat Files文件夹目录", path)
        if not os.path.exists(get):
            return
        saveSetting("wechat", str(get))

    def btn20(self):
        createLink(name="zb小程序", path=join(abs_path, "main.pyw"), to=abs_desktop, icon=join(abs_path, "logo.ico"))

    def btn21(self):
        addToStartMenu()

    def btn30(self):
        os.startfile(abs_path)

    def btn31(self):
        cmd("start NotePad.exe " + join(user_path, "zb/zb.log"))

    def btn40(self):
        self.label.setHidden(False)
        self.pushButton7.setEnabled(False)
        self.pushButton8.setEnabled(False)
        self.progressBar.setHidden(False)
        self.progressBar.setValue(0)
        self.thread = newThread(4)
        self.thread.signal.connect(self.btn41)
        self.thread.start()

    def btn41(self, msg):
        self.number = len(lib_list)
        if msg == "完成":
            self.progressBar.setValue(0)
            self.progressBar.setHidden(True)
            self.label.setHidden(True)
            InfoBar.success(
                title="提示",
                content="运行库安装成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            self.pushButton7.setEnabled(True)
            self.pushButton8.setEnabled(True)
            return
        if int(msg) == 0:
            self.count = 0
        self.count += 1
        self.label.setText("正在安装 " + lib_list[int(msg)] + " " + str(int(100 / self.number * self.count)) + "%")
        self.progressBar.setValue(int(100 / self.number * self.count))

    def btn42(self):
        if ":\编程\program" in abs_path:
            InfoBar.warning(
                title="警告",
                content="开发者目录禁止更新！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP_LEFT,
                duration=2000,
                parent=self
            )
            return
        self.label.setHidden(False)
        self.label.setText("正在连接至服务器")
        self.pushButton7.setEnabled(False)
        self.pushButton8.setEnabled(False)
        self.progressBar.setHidden(False)
        self.progressBar.setValue(0)
        self.thread = newThread(3)
        self.thread.signal.connect(self.btn43)
        self.thread.start()

    def btn43(self, msg):
        if msg == "开始":
            self.label.setText("正在连接至服务器")
            self.count = 0
            self.number = 20
        if msg == "完成":
            self.progressBar.setValue(0)
            self.progressBar.setHidden(True)
            self.label.setHidden(True)
            self.pushButton10 = PrimaryPushButton("重新运行", self, FIF.SYNC)
            self.pushButton10.clicked.connect(self.btn70)
            self.infoBar = InfoBar(
                icon=InfoBarIcon.INFORMATION,
                title="提示",
                content="更新成功，重新运行后生效！",
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            self.infoBar.addWidget(self.pushButton10)
            self.infoBar.show()
            self.pushButton7.setEnabled(True)
            self.pushButton8.setEnabled(True)
            return
        if "总共" in msg:
            self.number = int(msg[2:]) + 1
        self.count += 1
        if self.count != 1:
            self.label.setText("正在更新 " + msg + " " + str(int(100 / self.number * (self.count - 1))) + "%")
        self.progressBar.setValue(int(100 / self.number * (self.count - 1)))

    def btn60(self):
        if self.checkBox.isChecked():
            saveSetting("startupdate", "1")
            autoRun(switch="open", zdynames=os.path.basename(join(abs_path, "start.pyw")), current_file="zb小程序Qt")
        else:
            saveSetting("startupdate", "0")
            autoRun(switch="close", zdynames=os.path.basename(join(abs_path, "start.pyw")), current_file="zb小程序Qt")

    def btn70(self):
        cmd("main.pyw")
        sys.exit()


class Tray(QSystemTrayIcon):
    def __init__(self, UI):
        super(Tray, self).__init__()
        self.window = UI
        self.menu = RoundMenu()
        self.menu.addAction(Action(FIF.HOME, "打开", triggered=lambda: self.window.show()))
        # self.menu.addSeparator()
        self.menu.addAction(Action(FIF.ALIGNMENT, "整理", triggered=lambda: self.window.tab1.btn11()))
        self.menu.addAction(Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open("https://ianzb.github.io/program/")))
        self.menu.addAction(Action(FIF.CLOSE, "退出", triggered=lambda: sys.exit()))
        self.setIcon(QIcon("logo.ico"))
        self.setToolTip("zb小程序 " + version)
        self.activated.connect(self.clickedIcon)
        self.show()

    def clickedIcon(self, reason):
        if reason == 3:
            self.trayClickedEvent()
        elif reason == 1:
            self.contextMenuEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == QtCore.Qt.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def triggered(self):
        self.deleteLater()
        qApp.quit()

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), ani=True, aniType=MenuAnimationType.PULL_UP)


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        setThemeColor("#0078D4")
        self.setTitleBar(TitleBar(self))
        self.titleBar.raise_()
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, True)
        self.stackWidget = QStackedWidget(self)
        self.tab1 = tab1()
        self.settingtab = tab3(self)
        self.initLayout()
        self.initNavigation()
        self.initWindow()
        self.tray = Tray(self)
        self.thread = newThread(8)
        self.thread.signal.connect(self.ifShow)
        self.thread.start()
        self.old_hook = sys.excepthook
        sys.excepthook = self.catchExceptions

    def catchExceptions(self, ty, value, trace):
        traceback_format = traceback.format_exception(ty, value, trace)
        traceback_string = "".join(traceback_format)
        self.old_hook(ty, value, trace)
        import tkinter.messagebox
        tkinter.messagebox.showerror("错误", "zb小程序 发生严重错误，程序已关闭！\n报错信息为：\n" + str(traceback_string))
        logging.fatal("zb小程序 发生严重错误，程序已关闭！报错信息为：" + str(traceback_string))
        sys.exit()

    def ifShow(self, msg):
        if msg == "展示":
            self.show()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)
        self.addSubInterface(self.tab1, FIF.HOME, "功能", NavigationItemPosition.TOP)
        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=AvatarWidget(),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM
        )
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settingtab, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationInterface.setCurrentItem("功能")

    def initWindow(self):
        self.resize(weight, height)
        self.setFixedSize(weight, height)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon("logo.png"))
        self.setWindowTitle("zb小程序 " + version)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.windowEffect.setMicaEffect(self.winId())
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - weight // 2, h // 2 - height // 2)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text
        )

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        message = MessageBox("zb小程序", "是否打开 zb小程序 官网？", self)
        if message.exec():
            webbrowser.open("https://ianzb.github.io/program/")
        else:
            message = None

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.hide()

    def closeEvent(self, QCloseEvent):
        QCloseEvent.ignore()
        self.hide()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.processEvents()
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    w = Window()
    w.show()
    logging.info("启动成功")
    if readSetting("startfirst") == "1":
        w.hide()
        logging.info("当前为开机自启动，程序将自动隐藏至托盘")
        saveSetting("startfirst", "0")
    app.exec_()