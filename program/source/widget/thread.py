from .base import *
threadPool = QThreadPool()


class SingleDownloadThread(QRunnable,QObject):
    signal = pyqtSignal(object)
    def __init__(self, url: str, path: str):
        """
        单线程下载线程
        :param url: 链接
        :param path: 保存路径
        """
        super().__init__()
        self.url = url
        self.path = path

    def run(self):
        path = singleDownload(self.url, self.path, True, True, REQUEST_HEADER)
        self.signal.emit(path)


class MultiDownloadThread(QRunnable,QObject):
    signalFinished = pyqtSignal(object)
    signalRate = pyqtSignal(object)
    signalPath = pyqtSignal(object)
    def __init__(self, url: str, path: str):
        """
        多线程下载线程
        :param url: 链接
        :param path: 保存路径
        """
        super().__init__()
        self.url = url
        self.path = path


    def run(self):
        from time import sleep
        d = MultiDownload(self.url, self.path, False, True, ".downloading", REQUEST_HEADER)
        while True:
            sleep(0.1)
            if d.result != "downloading":
                self.signalFinished.emit(d.result)
                if d.result=="finished":
                    self.signalPath.emit(d.resultPath)
                break
            self.signalRate.emit(d.rate)