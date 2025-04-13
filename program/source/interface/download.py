import time

from .widget import *


class DownloadInfoCard(SmallInfoCard):
    downloadSignal = pyqtSignal(bool)
    setProgressSignal = pyqtSignal(int)

    def __init__(self, url: str, path: str, parent=None, replace: bool = False):
        """
        下载信息卡片
        @param url: 下载链接
        @param path: 下载目录
        @param parent: 父组件
        @param replace: 是否替换
        """
        super().__init__(parent)
        self.setTitle(zb.splitPath(zb.joinPath(path, zb.getFileNameFromUrl(url)) if zb.isDir(path) else path))
        self.setText(f"文件链接：{url}", 0)
        self.setText(f"目标位置：{zb.joinPath(path, zb.getFileNameFromUrl(url)) if zb.isDir(path) else path}", 1)
        self.titleLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.contentLabel1.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.contentLabel2.deleteLater()

        self.image.deleteLater()
        self.mainButton.deleteLater()

        self.url = url
        self.path = path
        self.replace = replace

        self.progressBar = ProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setFixedWidth(200)
        self.progressLabel = BodyLabel("加载中...", self)

        self.folderButton = ToolButton(FIF.FOLDER, self)
        setToolTip(self.folderButton, "打开下载目录")
        self.folderButton.clicked.connect(lambda: zb.showFile(zb.joinPath(self.path, zb.getFileNameFromUrl(self.url)) if zb.isDir(self.path) else self.path))
        self.folderButton.hide()

        self.deleteButton = ToolButton(FIF.DELETE, self)
        setToolTip(self.deleteButton, "删除下载文件")
        self.deleteButton.clicked.connect(self.deleteDownload)
        self.deleteButton.hide()

        self.closeButton = ToolButton(FIF.CLOSE, self)
        setToolTip(self.closeButton, "关闭下载任务")
        self.closeButton.clicked.connect(self.closeDownload)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.progressLabel, 0, Qt.AlignCenter | Qt.AlignBottom)
        self.vBoxLayout.addWidget(self.progressBar, 0, Qt.AlignCenter | Qt.AlignTop)
        self.vBoxLayout.setSpacing(8)

        self.hBoxLayout.addLayout(self.vBoxLayout, 0)
        self.hBoxLayout.addWidget(self.folderButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.deleteButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.closeButton, 0, Qt.AlignRight)
        self.hBoxLayout.setSpacing(8)
        self.hBoxLayout.setContentsMargins(16, 0, 16, 0)

        program.THREAD_POOL.submit(self.startDownload)

        self.setProgressSignal.connect(self.setProgress)

    def closeDownload(self):
        self.d.cancel()
        self.setProgressSignal.disconnect(self.setProgress)
        self.window().downloadPage.cardGroup.removeCard(self.url)
        self.downloadSignal.emit(False)
        self.deleteLater()

    def deleteDownload(self):
        path = self.d.resultPath
        zb.deleteFile(path, True)
        logging.info(f"已删除下载的{path}文件！")

    def startDownload(self):
        self.d = zb.downloadManager.download(self.url, self.path, False, self.replace, zb.REQUEST_HEADER)
        while True:
            if not self.d.isFinished():
                self.setProgressSignal.emit(int(self.d.progress()))
            else:
                self.progressLabel.setText("下载完成")
                self.downloadSignal.emit(True)
                self.folderButton.show()
                match self.d.result():
                    case "cancel":
                        self.setProgressSignal.emit(0)
                        self.progressLabel.setText("已取消")
                        self.downloadSignal.emit(False)
                        break
                    case "skip":
                        self.setProgressSignal.emit(0)
                        self.progressLabel.setText("已跳过")
                        self.downloadSignal.emit(False)
                        break
                    case "fail":
                        self.setProgressSignal.emit(0)
                        self.progressLabel.setText("下载失败")
                        self.downloadSignal.emit(False)
                        break
                    case "success":
                        self.setProgressSignal.emit(100)
                        self.progressLabel.setText("下载完成")
                        self.downloadSignal.emit(True)
                        self.folderButton.show()
                        self.deleteButton.show()
                        break
            time.sleep(0.25)

    def setProgress(self, percent: int):
        print(percent)
        self.progressBar.setValue(percent)
        self.progressLabel.setText(f"{percent}%")


class DownloadPage(BasicPage):
    title = "下载"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setViewportMargins(0, 70, 0, 0)
        self.setIcon(FIF.DOWNLOAD)

        self.lineEdit = AcrylicSearchLineEdit(self)
        self.lineEdit.setPlaceholderText("下载链接")
        setToolTip(self.lineEdit, "请输入任意网络下载链接")
        self.lineEdit.setMaxLength(1000)
        self.lineEdit.textChanged.connect(self.lineEditChanged)
        self.lineEdit.returnPressed.connect(self.downloadButtonClicked)
        self.lineEdit.searchButton.setIcon(FIF.DOWNLOAD)
        self.lineEdit.searchButton.clicked.connect(self.downloadButtonClicked)
        self.lineEdit.searchButton.setEnabled(False)

        self.card = GrayCard("自定义下载", self)
        self.card.addWidget(self.lineEdit)

        self.cardGroup = CardGroup("下载列表", self)

        self.vBoxLayout.addWidget(self.card)
        self.vBoxLayout.addWidget(self.cardGroup)

    def lineEditChanged(self):
        self.lineEdit.searchButton.setEnabled(bool(self.lineEdit.text()))

    def downloadButtonClicked(self):
        if not self.lineEdit.text() or not zb.isUrl(self.lineEdit.text()):
            return
        self.startDownload(self.lineEdit.text(), zb.joinPath(setting.read("downloadPath"), zb.getFileNameFromUrl(self.lineEdit.text())))

    def startDownload(self, url: str, path: str, replace: bool = False):
        """

        @param url: 下载链接
        @param path: 下载路径
        @param wait: 是否等待
        @param replace: 是否替换
        @return: 下载状态事件
        """
        d = DownloadInfoCard(url, path, self, replace)
        self.cardGroup.addCard(d, url + str(time.time()))
        return d.downloadSignal
