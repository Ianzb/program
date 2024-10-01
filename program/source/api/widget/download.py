from base import *
from thread import *


class DownloadWidget(QWidget):
    """
    下载文件ui接口
    """

    def __init__(self, url: str, path: str, parent=None):
        """
        下载文件ui接口
        @param url: 链接
        @param path: 文件完整路径或所在路径
        @param parent: 父组件
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.path = path
        self.url = url
        self.resultPath = ""

        if isDir(self.path):
            self.path = joinPath(self.path, getFileNameFromUrl(self.url))

        self.multiDownloadThread = MultiDownloadThread(self.url, self.path)
        self.multiDownloadThread.signalFinished.connect(self.downloadFinished)
        self.multiDownloadThread.signalRate.connect(self.downloading)
        self.multiDownloadThread.signalPath.connect(self.setResultPath)
        threadPool.start(self.multiDownloadThread)

        self.progressBar = ProgressBar(self.parent)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载文件{splitPath(self.path, 0)}...", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()
        self.infoBar.closeButton.clicked.connect(self.thread1.cancel)

    def downloading(self, msg):
        try:
            self.progressBar.setValue(msg)
        except:
            return

    def downloadFinished(self, msg):
        if msg == "skipped":
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "下载错误", f"文件{splitPath(self.path, 0)}已取消下载！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
        elif msg == "failed":
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "下载错误", f"文件{splitPath(self.path, 0)}下载失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
        elif msg == "finished":
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载成功", f"文件{splitPath(self.path, 0)}下载成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
        self.progressBar.deleteLater()

    def setResultPath(self, msg):
        self.resultPath = msg
