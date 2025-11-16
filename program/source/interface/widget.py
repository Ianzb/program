import time

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
    finishSignal = pyqtSignal(bool)
    cancelSignal = pyqtSignal()
    setProgressSignal = pyqtSignal(int)
    setTitleSignal = pyqtSignal(str)
    setContentSignal = pyqtSignal(str)

    def __init__(self, parent=None, progress_center=None, card_group: zbw.CardGroup = None, use_indeterminate: bool = True, has_image: bool = True, can_pause: bool = True, can_stop: bool = False):
        """
        普通信息卡片（搜索列表展示）
        :param parent: 父组件
        :param progress_center: 所属 ProgressCenter
        :param card_group: 所属 CardGroup
        :param use_indeterminate: 如果为 True，初始使用 IndeterminateProgressBar（若可用）
        :param has_image: 是否显示左侧图片
        :param can_pause: 是否可以暂停
        :param can_stop: 是否可以停止
        """
        super().__init__(parent)

        self.stat = "init"  # init, running, paused, stopped, finished, error

        self.wid = str(self)
        self.use_indeterminate = bool(use_indeterminate)
        self.has_image = bool(has_image)
        self.cardGroup = card_group
        self.progressCenter = progress_center
        self.can_pause = can_pause
        self.can_stop = can_stop

        self.setFixedWidth(372)

        if self.has_image:
            self.image = zbw.WebImage(self)
            self.image.setFixedSize(20, 20)

        self.titleLabel = BodyLabel(self)
        self.titleLabel.setSelectable()

        self.contentLabel = CaptionLabel(self)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.contentLabel.setAlignment(Qt.AlignLeft)
        self.contentLabel.setSelectable()

        self.startButton = ToolButton(FIF.PLAY, self)
        self.pauseButton = ToolButton(FIF.PAUSE, self)
        self.resumeButton = ToolButton(FIF.PAUSE_BOLD, self)
        self.stopButton = ToolButton(FIF.CLOSE, self)

        self.startButton.clicked.connect(self.start)
        if self.can_pause:
            self.pauseButton.clicked.connect(self.pause)
            self.resumeButton.clicked.connect(self.resume)
        self.stopButton.clicked.connect(self.stop)

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

        self.setProgressSignal.connect(self.setProgress)

        self.setTitleSignal.connect(self.setTitle)
        self.setContentSignal.connect(self.setContent)

    def start(self):
        self.stat = "running"
        self.startButton.hide()
        if self.can_pause:
            self.pauseButton.show()
            self.resumeButton.hide()
        if self.can_stop:
            self.stopButton.show()
        self.startSignal.emit()

    def pause(self):
        self.stat = "paused"
        self.startButton.hide()
        if self.can_pause:
            self.pauseButton.hide()
            self.resumeButton.show()
            if self.can_stop:
                self.stopButton.show()
        self.pauseSignal.emit()

    def resume(self):
        self.stat = "running"
        self.startButton.hide()
        if self.can_pause:
            self.resumeButton.hide()
            self.pauseButton.show()
        if self.can_stop:
            self.stopButton.show()
        self.resumeSignal.emit()

    def finish(self, success: bool = True):
        self.stat = "finished"
        self.startButton.hide()
        if self.can_pause:
            self.resumeButton.hide()
            self.pauseButton.hide()
        self.stopButton.show()
        if self.use_indeterminate:
            self.setProgress(100)
            self.setIndeterminate(False)
            self.progressLabel.hide()
        self.finishSignal.emit(success)

    def cancel(self):
        self.stat = "cancelled"
        self.startButton.hide()
        if self.can_pause:
            self.resumeButton.hide()
            self.pauseButton.hide()
        self.stopButton.show()
        if self.use_indeterminate:
            self.setProgress(0)
            self.setIndeterminate(False)
            self.progressLabel.hide()
        self.cancelSignal.emit()

    def stop(self):
        if self.stat in ["finished", "cancelled"]:
            self.cardGroup.removeCard(self.wid)
            self.cardGroup.update()
            self.progressCenter.count()
        else:
            self.cancel()

    def setTitle(self, text: str):
        """
        设置标题
        :param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, img: str | FluentIconBase, url: str = None):
        """
        设置图片
        :param path: 路径
        :param url: 链接
        """
        if self.has_image:
            self.image.setImg(img, url, program.THREAD_POOL)

    def setIcon(self, img: str | FluentIconBase, url: str = None):
        """
        设置图片
        :param path: 路径
        :param url: 链接
        """
        self.setImg(img, url)

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


class DownloadTaskCard(TaskCard):
    downloadFinishedSignal = pyqtSignal(bool, str)

    def __init__(self, parent=None, progress_center=None, card_group: zbw.CardGroup = None, url: str = None, path: str = None, exist: bool = False, force: bool = False):
        super().__init__(parent, progress_center, card_group, False, True, True, True)
        self.url = url
        self.path = path
        self.exist = exist
        self.force = force
        self.download = None
        if self.force:
            self.path = zb.getRepeatFileName(self.path)

        self.setImg(FIF.DOWNLOAD)
        self.setTitle("下载")
        self.setContent(f"下载中...")

        self.setNewToolTip(f"链接：{self.url}\n保存至：{self.path}")

        self.openFileButton = ToolButton(FIF.PLAY, self)
        self.openFileButton.setNewToolTip("打开文件")
        self.openFileButton.hide()
        self.hBoxLayout.insertWidget(5, self.openFileButton, Qt.AlignRight)

        self.showFileButton = ToolButton(FIF.FOLDER, self)
        self.showFileButton.setNewToolTip("打开文件所在位置")
        self.showFileButton.hide()
        self.hBoxLayout.insertWidget(6, self.showFileButton, Qt.AlignRight)

        self.startSignal.connect(self.startDownload)
        self.pauseSignal.connect(self.pauseDownload)
        self.resumeSignal.connect(self.resumeDownload)
        self.cancelSignal.connect(self.cancelDownload)

        self.start()

        self.downloadFinishedSignal.connect(self.downloadFinished)

    @zb.threadPoolDecorator(program.THREAD_POOL)
    def startDownload(self):
        self.download = zb.downloadManager.download(self.url, self.path, self.exist, self.force, zb.REQUEST_HEADER)
        while True:
            if self.download.isFinished():
                match self.download.stat():
                    case "cancelled":
                        self.setProgressSignal.emit(0)
                        self.setContentSignal.emit("下载取消！")
                        self.finish(False)
                        self.downloadFinishedSignal.emit(False, "")
                        break
                    case "failed":
                        self.setProgressSignal.emit(0)
                        self.setContentSignal.emit("下载失败！")
                        self.finish(False)
                        self.downloadFinishedSignal.emit(False, "")
                        break
                    case "success":
                        self.setProgressSignal.emit(100)
                        self.setContentSignal.emit("下载完成！")
                        self.finish(True)
                        self.downloadFinishedSignal.emit(True, self.download.outputPath())
                        break
            else:
                self.setProgressSignal.emit(int(self.download.progress()))
            time.sleep(0.2)

    def pauseDownload(self):
        if self.download:
            self.download.pause()

    def resumeDownload(self):
        if self.download:
            self.download.resume()

    def cancelDownload(self):
        if self.download:
            self.download.cancel()

    def downloadFinished(self, stat: bool, path: str):
        if stat:
            self.openFileButton.clicked.connect(lambda: zb.startFile(path))
            self.openFileButton.show()
            self.showFileButton.clicked.connect(lambda: zb.showFile(path))
            self.showFileButton.show()


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
        self.scrollArea.vBoxLayout.setSpacing(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.hide()

        self.cardGroup = zbw.CardGroup(self, show_title=False)
        self.cardGroup.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollArea.vBoxLayout.addWidget(self.cardGroup, 1)

        self.vBoxLayout.addLayout(self.titleLayout)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addWidget(self.emptyLabel, 1)

        self.setMinimumSize(400, 100)
        self.setMaximumSize(400, 500)

        self.infoBadge = None

        self._adjustSize()

    def _adjustSize(self):
        content_height = self.cardGroup.height()
        self.scrollArea.setMaximumHeight(min(content_height, 500))
        if self.window.progressCenterFlyout:
            self.window.progressCenterFlyout.setFixedHeight(min(max(content_height + 52, 100), 500))
        self.setFixedHeight(min(max(content_height + 52, 100), 500))

    def clear(self):
        import copy
        for wid, widget in copy.copy(self.cardGroup._cardMap).items():
            if widget.stat in ["finished", "cancelled"]:
                self.cardGroup.removeCard(wid)
        self.cardGroup.adjustSize()
        self.count()

    def addTask(self, show_center: bool = False, use_indeterminate: bool = True, has_image: bool = True, can_pause: bool = True, can_stop: bool = True):
        """
        新增任务
        :param show_center: 是否自动展示任务中心
        :param use_indeterminate: 是否使用随机进度条
        :param has_image: 是否有图片
        :param can_pause: 是否可以暂停
        :param can_stop: 是否可以停止
        :return:
        """
        card = TaskCard(self.cardGroup, self, self.cardGroup, use_indeterminate, has_image, can_pause, can_stop)
        self.cardGroup.addCard(card, card.wid)
        self.cardGroup.adjustSize()
        self.count()
        if show_center:
            if not self.isVisible() and self.window.isVisible() and not self.window.isMinimized():
                self.window.showProgressCenter()
        return card

    def downloadTask(self, url: str, path: str, exist: bool = False, force: bool = False, show_center: bool = True):
        """
        新增下载任务
        :param url: 链接
        :param path: 路径
        :param exist: 存在时是否下载
        :param force: 是否强制下载
        :param show_center: 是否自动展示任务中心
        :return:
        """
        card = DownloadTaskCard(self.cardGroup, self, self.cardGroup, url, path, exist, force)
        self.cardGroup.addCard(card, card.wid)
        self.cardGroup.adjustSize()
        self.count()
        if show_center:
            if not self.isVisible() and self.window.isVisible() and not self.window.isMinimized():
                self.window.showProgressCenter()
        return card

    def count(self):
        count = self.cardGroup.count()
        if not self.infoBadge:
            self.infoBadge = InfoBadge.attension(count, self.window.titleBar, self.window.progressCenterButton, position=NewInfoBadgePosition.CENTER)
        self.infoBadge.setText(str(count))
        self.infoBadge.setVisible(bool(count))
        self.infoBadge.adjustSize()
        self.infoBadge.move(self.infoBadge.manager.position())

        self.emptyLabel.setHidden(bool(count))
        self.scrollArea.setVisible(bool(count))
        if count:
            self.window.progressCenterButton.setIcon(None)
        else:
            self.window.progressCenterButton.setIcon(ZBF.apps_list)

        self.cardGroup.adjustSize()
        self._adjustSize()
        if self.isVisible():
            self.window.showProgressCenter(NewFlyoutAnimationType.FADE_IN)


class NewInfoBadgePosition(Enum):
    """ Info badge position """
    CENTER = 7


@InfoBadgeManager.register(NewInfoBadgePosition.CENTER)
class BottomCenterInfoBadgeManager(InfoBadgeManager):
    """ Bottom left info badge manager """

    def position(self):
        x = self.target.geometry().center().x() - self.badge.width() // 2
        y = self.target.geometry().center().y() - self.badge.height() // 2
        return QPoint(x, y)


class NewFlyoutAnimationType(Enum):
    """ Flyout animation type """
    FADE_IN = 4
    FIXED_NONE = 6


@FlyoutAnimationManager.register(NewFlyoutAnimationType.FADE_IN)
class FadeInFlyoutAnimationManager(FlyoutAnimationManager):
    """ Fade in flyout animation manager """

    def position(self, target: QWidget):
        """ return the top left position relative to the target """
        w = self.flyout
        pos = target.mapToGlobal(QPoint(0, target.height()))
        x = pos.x() + target.width() // 2 - w.sizeHint().width() // 2
        y = pos.y() - w.layout().contentsMargins().top() + 8
        return QPoint(x, y)

    def exec(self, pos: QPoint):
        self.flyout.move(self._adjustPosition(pos))
        self.aniGroup.removeAnimation(self.slideAni)
        self.aniGroup.start()


@FlyoutAnimationManager.register(NewFlyoutAnimationType.FIXED_NONE)
class DummyFlyoutAnimationManager(FlyoutAnimationManager):
    """ Dummy flyout animation manager """

    def exec(self, pos: QPoint):
        """ start animation """
        self.flyout.move(self._adjustPosition(pos))

    def position(self, target: QWidget):
        """ return the top left position relative to the target """
        w = self.flyout
        pos = target.mapToGlobal(QPoint(0, target.height()))
        x = pos.x() + target.width() // 2 - w.sizeHint().width() // 2
        y = pos.y() - w.layout().contentsMargins().top() + 8
        return QPoint(x, y)


class ErrorMessageBox(zbw.ScrollMessageBox):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)
        self.contentLabel.setSelectable()
        self.cancelButton.setText("关闭")
        self.yesButton.hide()
        self.yesButton.deleteLater()

        self.reportButton = PrimaryPushButton("反馈", self, FIF.FEEDBACK)
        self.reportButton.clicked.connect(lambda: webbrowser.open(zb.joinUrl(program.GITHUB_URL, "issues/new")))

        self.restartButton = PrimaryPushButton("重启", self, FIF.SYNC)
        self.restartButton.clicked.connect(program.restart)
        self.buttonLayout.insertWidget(0, self.reportButton, 2)
        self.buttonLayout.insertWidget(1, self.restartButton, 2)
