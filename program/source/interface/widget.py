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
    startSignal = pyqtSignal()
    pauseSignal = pyqtSignal()
    resumeSignal = pyqtSignal()
    stopSignal = pyqtSignal()

    def __init__(self, parent=None, progress_center=None, card_group: zbw.CardGroup = None, use_indeterminate: bool = True, has_image: bool = True, can_pause: bool = True):
        """
        普通信息卡片（搜索列表展示）
        :param parent: 父组件
        :param progress_center: 所属 ProgressCenter
        :param card_group: 所属 CardGroup
        :param use_indeterminate: 如果为 True，初始使用 IndeterminateProgressBar（若可用）
        :param has_image: 是否显示左侧图片
        :param can_pause: 是否可以暂停

        """
        super().__init__(parent)

        self.stat = "init"  # init, running, paused, stopped, finished, error

        self.wid = str(self)
        self.use_indeterminate = bool(use_indeterminate)
        self.has_image = bool(has_image)
        self.cardGroup = card_group
        self.progressCenter = progress_center
        self.can_pause = can_pause

        self.setMinimumWidth(100)
        self.setMinimumHeight(40)

        if self.has_image:
            self.image = zbw.WebImage(self)
            self.image.setFixedSize(20, 20)

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

        self.startSignal = self.startButton.clicked
        self.pauseSignal = self.pauseButton.clicked
        self.resumeSignal = self.resumeButton.clicked
        self.stopSignal = self.stopButton.clicked

        self.startSignal.connect(self.start)
        if self.can_pause:
            self.pauseSignal.connect(self.pause)
            self.resumeSignal.connect(self.resume)
        self.stopSignal.connect(self.stop)

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
        self.stat = "running"
        self.startButton.hide()
        if self.can_pause:
            self.pauseButton.show()
            self.resumeButton.hide()
        self.stopButton.show()

    def pause(self):
        self.stat = "paused"
        self.startButton.hide()
        if self.can_pause:
            self.pauseButton.hide()
            self.resumeButton.show()
        self.stopButton.show()

    def resume(self):
        self.stat = "running"
        self.startButton.hide()
        if self.can_pause:
            self.resumeButton.hide()
            self.pauseButton.show()
        self.stopButton.show()

    def finish(self):
        self.stat = "finished"
        self.startButton.hide()
        if self.can_pause:
            self.resumeButton.hide()
            self.pauseButton.hide()
        self.stopButton.show()

    def stop(self):
        self.stat = "stopped"

        self.cardGroup.removeCard(self.wid)
        self.progressCenter.count()

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

    def setDescription(self, text: str):
        """
        设置文本
        :param text: 文本
        """
        self.setText(text)

    def setIcon(self, icon: str | FluentIconBase):
        """
        设置图标
        :param icon: 图标
        """
        self.image.setImg(icon)
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

    def __init__(self, window=None):
        super().__init__()
        self.window = window

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSpacing(8)
        self.vBoxLayout.setContentsMargins(14, 12, 14, 8)

        self.titleLayout = QHBoxLayout(self)

        self.titleLabel = StrongBodyLabel("任务中心", self)

        self.emptyLabel = BodyLabel("当前无任务", self)
        self.emptyLabel.setTextColor("#909090", "#707070")
        self.emptyLabel.setAlignment(Qt.AlignCenter)

        self.clearButton = PushButton("清除已完成的项目", self)
        self.clearButton.setFixedSize(130, 24)
        self.clearButton.setFont(QFont("SimHei", 10))
        self.clearButton.clicked.connect(self.clear)

        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addWidget(self.clearButton)

        self.scrollArea = zbw.BetterScrollArea(self)
        self.scrollArea.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.vBoxLayout.setSpacing(8)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scrollArea.hide()

        self.cardGroup = zbw.CardGroup(self, show_title=False)
        self.cardGroup.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollArea.vBoxLayout.addWidget(self.cardGroup)

        self.vBoxLayout.addLayout(self.titleLayout)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addWidget(self.emptyLabel, 1)

        self.setMinimumSize(400, 100)
        self.setMaximumSize(400, 600)

        self.infoBadge = None

    def clear(self):
        for wid, widget in self.cardGroup._cardMap.items():
            if widget.stat in ("finished", "stopped"):
                self.cardGroup.removeCard(wid)
        self.count()

    def addTask(self, show_center: bool = False, use_indeterminate: bool = True, has_image: bool = True, can_pause: bool = True):
        card = TaskCard(self.cardGroup, self, self.cardGroup, use_indeterminate, has_image, can_pause)
        self.cardGroup.addCard(card, card.wid)
        self.count()
        if show_center:
            self.show()
        return card

    def count(self):
        count = self.cardGroup.count()
        if not self.infoBadge:
            self.infoBadge = InfoBadge.attension(count, self.window.titleBar, self.window.progressCenterButton, position=InfoBadgePosition.CENTER)
        self.infoBadge.setText(str(count))
        self.infoBadge.setVisible(bool(count))

        self.emptyLabel.setHidden(bool(count))
        self.scrollArea.setVisible(bool(count))
        if count:
            self.window.progressCenterButton.setIcon(None)
        else:
            self.window.progressCenterButton.setIcon(ZBF.apps_list)


class InfoBadgePosition(Enum):
    """ Info badge position """
    TOP_RIGHT = 0
    BOTTOM_RIGHT = 1
    RIGHT = 2
    TOP_LEFT = 3
    BOTTOM_LEFT = 4
    LEFT = 5
    NAVIGATION_ITEM = 6
    CENTER = 7


@InfoBadgeManager.register(InfoBadgePosition.CENTER)
class BottomCenterInfoBadgeManager(InfoBadgeManager):
    """ Bottom left info badge manager """

    def position(self):
        x = self.target.geometry().center().x() - self.badge.width() // 2
        y = self.target.geometry().center().y() - self.badge.height() // 2
        return QPoint(x, y)
