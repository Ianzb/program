from .log import *
from .file import File
from .info import Info


class Web:
    def isUrl(self, url: str):
        """
        判断是否是网址
        @param url: 网址字符串
        @return: 布尔值
        """
        return url.startswith("http://") or url.startswith("https://")

    def joinUrl(self, *urls):
        """
        拼接网址
        @param urls: 网址
        @return: 拼接结果
        """
        from urllib.parse import urljoin
        data: str = ""
        for i in urls:
            data = urljoin(data, i)
        return data

    def getUrl(self, url: str, header=None, timeout: int | tuple = (5, 10), times: int = 5):
        """
        可重试的get请求
        @param url: 链接
        @param header: 请求头
        @param timeout: 超时
        @param times: 重试次数
        @return:
        """
        import requests
        Log.info(f"正在Get请求{url}的信息！")
        for i in range(times):
            try:
                response = requests.get(url, headers=header, stream=True, timeout=timeout)
                return response
            except Exception as ex:
                Log.warning(f"第{i + 1}次Get请求{url}失败，错误信息为{ex}，正在重试中！")
                continue
        Log.error(f"Get请求{url}失败！")

    def postUrl(self, url: str, json: dict, header=None, timeout: int | tuple = (5, 10), times: int = 5):
        """
        可重试的post请求
        @param url: 链接
        @param json: 发送数据
        @param header: 请求头
        @param timeout: 超时
        @param times: 重试次数
        @return:
        """
        import requests
        Log.info(f"正在Post请求{url}的信息！")

        for i in range(times):
            try:
                response = requests.post(url, headers=header, json=json, timeout=timeout)
                return response
            except Exception as ex:
                Log.warning(f"第{i + 1}次Post请求{url}失败，错误信息为{ex}，正在重试中！")
                continue
        Log.error(f"Post请求{url}失败！")

    def getFileNameFromUrl(self, url: str):
        """
        从链接获取文件名
        @param url: 链接
        @return:
        """
        from urllib.parse import urlparse
        import os
        return os.path.basename(urlparse(url).path)

    def singleDownload(self, url: str, path: str, exist: bool = True, force: bool = False, header: dict = Info.REQUEST_HEADER):
        """
        下载文件
        @param url: 下载链接
        @param path: 下载后完整目录/文件名
        @param exist: 是否在已有文件的情况下下载（False时force无效）
        @param force: 是否强制下载（替换已有文件）
        @param header: 请求头
        @return:
        """
        import requests
        try:
            if File().isDir(path):
                path = File().joinPath(path, self.getFileNameFromUrl(url))
            if File().isFile(path) and not exist:
                Log.warning(f"由于文件{path}已存在，自动跳过单线程下载！")
                return False
            if exist and not force:
                path = File().addRepeatSuffix(path)
            Log.info(f"正在单线程下载文件{url}到{path}！")
            response = requests.get(url, headers=header, stream=True)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            Log.info(f"已将文件{url}单线程下载到到{path}！")
            return path
        except Exception as ex:
            Log.error(f"单线程下载文件{url}到{path}失败，报错信息：{ex}！")
            return False


# 对DownloadKit进行魔改
from DownloadKit.mission import Mission


def _set_auto_finish(self, func):
    """设置一个任务为自动完成状态
    :param func: 完成时调用的函数
    :return: None
    """
    self._auto_finish = func


def _set_done(self, result, info):
    """设置一个任务为done状态
    :param result: 结果：'success'、'skipped'、'canceled'、False、None
    :param info: 任务信息
    :return: None
    """
    if result == 'skipped':
        self.set_states(result=result, info=info, state=self._DONE)

    elif result == 'canceled' or result is False:
        self.recorder.clear()
        self.set_states(result=result, info=info, state=self._DONE)

    elif result == 'success':
        self.recorder.record()
        if self.size and self.path.stat().st_size < self.size:
            self.del_file()
            self.set_states(False, '下载失败', self._DONE)
        else:
            self._auto_finish()
            self.set_states('success', info, self._DONE)


Mission._set_auto_finish = _set_auto_finish
Mission._set_done = _set_done

from DownloadKit import DownloadKit

downloadKit = DownloadKit(roads=32, file_exists="overwrite")


class MultiDownload:
    def __init__(self, url: str, path: str, wait: bool = True, replace: bool = False, suffix: str = "", header: dict = Info.REQUEST_HEADER):
        """
        多线程下载，下载完成后需要确认self.result为success方可完成下载，通过self.resultPath获取结果路径
        @param url: 下载链接
        @param path: 下载后完整目录/文件名
        @param wait: 是否等待
        @param replace: 是否替换
        @param suffix: 临时后缀名
        @param header: 请求头
        """
        if suffix and suffix.startswith("."):
            suffix = suffix[1:]
        self.resultPath = None
        self.url = url
        self.path = path
        self.replace = replace
        self.__finished = False

        if File().isDir(self.path):
            self.path = File().joinPath(self.path, Web().getFileNameFromUrl(self.url))
        self.suffixPath = self.path + "." + suffix
        if File().isFile(self.suffixPath):
            self.suffixPath = File().addRepeatSuffix(self.suffixPath)

        Log.info(f"开始使用DownloadKit下载{self.url}到{self.path}！")
        self.downloadKit = downloadKit
        self.file = self.downloadKit.add(self.url,
                                         File().splitPath(self.path, 3),
                                         File().splitPath(self.suffixPath, 1),
                                         File().splitPath(self.suffixPath, 2)[1:],
                                         headers=header, split=True, allow_redirects=True, stream=True, timeout=15)
        self.file._set_auto_finish(self._finish)
        if wait:
            self.file.wait()

    @property
    def rate(self):
        """
        获得下载进度
        @return: 数字
        """
        return int(self.file.rate) if self.file.rate else 0

    @property
    def result(self):
        """
        获得下载结果
        @return: downloading下载中，skipped已跳过，failed失败，finished已结束
        """
        if self.__finished:
            return self.__finished
        elif self.file.result is None:
            return "downloading"
        elif self.file.result == "skipped":
            return "skipped"
        elif not self.file.result:
            return "failed"
        else:
            return "failed"

    def stop(self):
        """
        停止下载
        """
        if self.result == "downloading":
            self.file.cancel()
            self.file.session.close()
            self.downloadKit.cancel()
        else:
            Log.warning(f"使用DownloadKit下载{self.url}的状态为{self.result}，无法停止！")

    def _finish(self):
        """
        下载完成后的回调函数，无需手动调用。
        """
        self.resultPath = File().movePath(self.suffixPath, self.path, self.replace)
        if not self.resultPath:
            Log.warning(f"使用DownloadKit下载{self.url}到{self.path}失败：无法移动下载临时文件至正式目录！")
            self.__finished = "failed"
            return
        Log.info(f"成功使用DownloadKit下载{self.url}到{self.resultPath}！")
        self.__finished = "finished"
