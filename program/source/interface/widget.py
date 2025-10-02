from ..program import *
import webbrowser


class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, window):
        super(Tray, self).__init__(QIcon(program.ICON))
        self.window = window

        self.setIcon(QIcon(program.ICON))
        self.setToolTip(program.TITLE)
        self.activated.connect(self.iconClicked)

        self.action1 = Action(FIF.HOME, "打开", triggered=self.window.show)
        self.action2 = Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program.URL))
        self.action3 = Action(FIF.SYNC, "重启", triggered=program.restart)
        self.action4 = Action(FIF.CLOSE, "退出", triggered=program.close)

        self.menu = AcrylicMenu(parent=self.window)

        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

    def showTrayMessage(self, title, msg):
        super().showMessage(title, msg, QIcon(program.ICON))

    def iconClicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
            self.contextMenuEvent()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick or QSystemTrayIcon.ActivationReason.MiddleClick:
            self.trayClickedEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == Qt.WindowState.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), aniType=MenuAnimationType.PULL_UP)
        self.menu.show()


class TaskCard(CardWidget):

    def __init__(self, parent=None, use_indeterminate: bool = True, has_image: bool = True):
        """
        普通信息卡片（搜索列表展示）
        :param use_indeterminate: 如果为 True，初始使用 IndeterminateProgressBar（若可用）
        :param has_image: 是否显示左侧图片
        """
        super().__init__(parent)

        self.wid = str(self)
        self.use_indeterminate = bool(use_indeterminate)
        self.has_image = bool(has_image)

        self.setMinimumWidth(100)
        self.setMinimumHeight(40)

        if self.has_image:
            self.image = zbw.WebImage(self)
            self.image.setFixedSize(25, 25)

        self.titleLabel = BodyLabel(self)

        self.contentLabel = CaptionLabel(self)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.contentLabel.setAlignment(Qt.AlignLeft)
        self.contentLabel.setWordWrap(True)

        self.titleLabel.setSelectable()
        self.contentLabel.setSelectable()

        self.startButton = ToolButton(FIF.PLAY, self)
        self.pauseButton = ToolButton(FIF.PAUSE, self)
        self.resumeButton = ToolButton(FIF.PAUSE_BOLD, self)
        self.stopButton = ToolButton(FIF.CLOSE, self)

        self.pauseButton.hide()
        self.resumeButton.hide()
        self.stopButton.hide()

        self._det_bar = ProgressBar(self)
        self._det_bar.setRange(0, 100)
        self._det_bar.setValue(0)

        self._ind_bar = IndeterminateProgressBar(self)

        self.progressBar = self._ind_bar if self.use_indeterminate else self._det_bar

        self.progressLabel = BodyLabel("0%", self)
        self.progressLabel.setTextColor("#606060", "#d2d2d2")
        self.progressLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.progressLabel.setHidden(self.use_indeterminate)

        self.leftLayout = QVBoxLayout()
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.leftLayout.setSpacing(0)
        self.leftLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)

        self.centerLayout = QVBoxLayout()
        self.centerLayout.setContentsMargins(0, 0, 0, 0)
        self.centerLayout.setSpacing(6)
        self.centerLayout.addWidget(self.contentLabel)

        self.progressLayout = QHBoxLayout()
        self.progressLayout.setContentsMargins(0, 0, 0, 0)
        self.progressLayout.setSpacing(8)
        self.progressLayout.addWidget(self._det_bar)
        self.progressLayout.addWidget(self._ind_bar)
        self.progressLayout.addWidget(self.progressLabel)
        self.progressLayout.setAlignment(Qt.AlignVCenter)

        self._det_bar.setHidden(self.use_indeterminate)
        self._ind_bar.setVisible(self.use_indeterminate)

        self.centerLayout.addLayout(self.progressLayout)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(16, 11, 11, 11)
        self.hBoxLayout.setSpacing(6)

        if self.has_image:
            self.hBoxLayout.addWidget(self.image)

        self.hBoxLayout.addLayout(self.leftLayout)
        self.hBoxLayout.addLayout(self.centerLayout, 1)

        self.hBoxLayout.addStretch(0)
        self.hBoxLayout.addWidget(self.startButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.pauseButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.resumeButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.stopButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(8)

    def start(self):
        self.startButton.hide()

    def setTitle(self, text: str):
        """
        设置标题
        :param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        :param path: 路径
        :param url: 链接
        """
        if self.has_image:
            self.image.setImg(path, url, program.THREAD_POOL)

    def setText(self, text: str):
        """
        设置文本
        :param text: 文本
        """
        self.contentLabel.setText(text)
        self.contentLabel.adjustSize()

    def setContent(self, text: str):
        """
        设置文本
        :param text: 文本
        """
        self.setText(text)

    def setProgress(self, percent: int):
        """
        更新进度条百分比（仅在确定模式下显示）
        :param percent: 0-100
        """
        self._det_bar.setValue(percent)
        self.progressLabel.setText(f"{int(percent)}%")

    def setIndeterminate(self, flag: bool):
        """
        设置随机进度条
        :param flag: 是否
        :return:
        """
        if self.use_indeterminate == flag:
            return

        self._det_bar.setHidden(flag)
        self._ind_bar.setVisible(flag)

        self.progressBar = self._ind_bar if flag else self._det_bar
        self.use_indeterminate = flag
        self.progressLabel.setHidden(flag)


class ProgressCenter(FlyoutViewBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSpacing(8)
        self.vBoxLayout.setContentsMargins(14, 12, 14, 8)

        self.titleLayout = QHBoxLayout(self)

        self.titleLabel = StrongBodyLabel("任务中心", self)

        self.clearButton = PushButton("清除已完成的项目", self)
        self.clearButton.setFixedSize(130, 24)
        self.clearButton.setFont(QFont("SimHei", 10))

        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addWidget(self.clearButton)

        self.scrollArea = zbw.BetterScrollArea(self)
        self.scrollArea.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.vBoxLayout.setSpacing(8)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.cardGroup = zbw.CardGroup(self, show_title=False)
        self.cardGroup.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollArea.vBoxLayout.addWidget(self.cardGroup)

        self.vBoxLayout.addLayout(self.titleLayout)
        self.vBoxLayout.addWidget(self.scrollArea, 1)

        self.setMinimumSize(400, 300)
        self.setMaximumSize(400, 600)

    def addTask(self, use_indeterminate: bool = True, has_image: bool = True):
        card = TaskCard(self.cardGroup, use_indeterminate, has_image)
        self.cardGroup.addCard(card, card.wid)
        return card
