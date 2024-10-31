import time

from .widget import *


class DownloadInfoCard(SettingCard):
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
        super().__init__(FIF.DOWNLOAD, f.splitPath(f.joinPath(path, f.getFileNameFromUrl(url)) if f.isDir(path) else path), f"文件链接：{url}\n目标位置：{f.joinPath(path, f.getFileNameFromUrl(url)) if f.isDir(path) else path}", parent)
        self.contentLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

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
        self.folderButton.clicked.connect(lambda: f.showFile(f.joinPath(self.path, f.getFileNameFromUrl(self.url)) if f.isDir(self.path) else self.path))
        self.folderButton.hide()

        self.closeButton = ToolButton(FIF.DELETE, self)
        setToolTip(self.closeButton, "关闭下载")
        self.closeButton.clicked.connect(self.closeDownload)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.progressLabel, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.progressBar, 0, Qt.AlignCenter)

        self.hBoxLayout.addLayout(self.vBoxLayout, 0)
        self.hBoxLayout.addWidget(self.folderButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.closeButton, 0, Qt.AlignRight)
        self.hBoxLayout.setSpacing(8)
        self.hBoxLayout.setContentsMargins(16, 0, 16, 0)

        program.THREAD_POOL.submit(self.startDownload)

        self.setProgressSignal.connect(self.setProgress)

    def closeDownload(self):
        self.d.stop()
        self.setProgressSignal.disconnect(self.setProgress)
        self.window().downloadPage.cardGroup.cardLayout.removeWidget(self)
        self.downloadSignal.emit(False)
        self.deleteLater()

    def startDownload(self):
        self.d = MultiDownload(self.url, self.path, False, self.replace, ".downloading", f.REQUEST_HEADER)
        while True:
            match self.d.result:
                case "downloading":

                    if self.d.rate == 100:
                        self.progressBar.setValue(100)
                        self.progressLabel.setText("下载完成")
                        self.downloadSignal.emit(True)
                        self.folderButton.show()
                        break
                    else:
                        self.setProgressSignal.emit(self.d.rate)

                case "skipped":
                    self.setProgressSignal.emit(0)
                    self.progressLabel.setText("已取消")
                    self.downloadSignal.emit(False)
                    break
                case "failed":
                    self.setProgressSignal.emit(0)
                    self.progressLabel.setText("下载失败")
                    self.downloadSignal.emit(False)
                    break
                case "finished":
                    self.setProgressSignal.emit(100)
                    self.progressLabel.setText("下载完成")
                    self.downloadSignal.emit(True)
                    self.folderButton.show()
                    break
            time.sleep(0.25)

    def setProgress(self, percent: int):
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
        self.lineEdit.setMaxLength(50)
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
        if not self.lineEdit.text() or not f.isUrl(self.lineEdit.text()):
            return
        self.startDownload(self.lineEdit.text(), f.joinPath(setting.read("downloadPath"), f.getFileNameFromUrl(self.lineEdit.text())), True)

    def startDownload(self, url: str, path: str, replace: bool = False):
        """

        @param url: 下载链接
        @param path: 下载路径
        @param wait: 是否等待
        @param replace: 是否替换
        @return: 下载状态事件
        """
        d = DownloadInfoCard(url, path, self, replace)
        self.cardGroup.addWidget(d)
        return d.downloadSignal
