from log import *
from file import existPath, joinPath, isFile, isDir, splitPath, addRepeatSuffix, movePath, _dirPathToSelfPath
from info import REQUEST_HEADER


def joinUrl(*urls):
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


def getUrl(url: str, header=None, timeout: int | tuple = (5, 10), times: int = 5):
    """
    可重试的get请求
    @param url: 链接
    @param header: 请求头
    @param timeout: 超时
    @param times: 重试次数
    @return:
    """
    import requests
    for i in range(times):
        try:
            response = requests.get(url, headers=header, stream=True, timeout=timeout)
            return response
        except Exception as ex:
            logging.warning(f"第{i + 1}次Get请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Get请求{url}失败！")


def postUrl(url: str, json: dict, header=None, timeout: int | tuple = (5, 10), times: int = 5):
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
    for i in range(times):
        try:
            response = requests.post(url, headers=header, json=json, timeout=timeout)
            return response
        except Exception as ex:
            logging.warning(f"第{i + 1}次Post请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Post请求{url}失败！")


def getFileNameFromUrl(url: str):
    """
    从链接获取文件名
    @param url: 链接
    @return:
    """
    from urllib.parse import urlparse
    import os
    return os.path.basename(urlparse(url).path)


def singleDownload(url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
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
        if isDir(path):
            path = joinPath(path, getFileNameFromUrl(url))
        if isFile(path) and not exist:
            logging.warning(f"由于文件{path}已存在，自动跳过单线程下载！")
            return False
        if exist and not force:
            path = addRepeatSuffix(path)
        logging.info(f"正在单线程下载文件{url}到{path}！")
        response = requests.get(url, headers=header, stream=True)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logging.info(f"已将文件{url}单线程下载到到{path}！")
        return path
    except Exception as ex:
        logging.error(f"但下载文件{url}到{path}失败，报错信息：{ex}！")


from DownloadKit import DownloadKit
from system import EasyThread

downloadKit = DownloadKit(roads=32, file_exists="overwrite")


class MultiDownload:
    def __init__(self, url: str, path: str, wait: bool = True, replace: bool = False, suffix: str = "", header: dict = REQUEST_HEADER):
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
        self.__quit = False
        self.__finished = False
        if isFile(self.path) and not replace:
            logging.warning(f"由于文件{self.path}已存在，自动跳过下载！")
            self.__quit = True
            return
        elif isDir(self.path):
            self.path = joinPath(self.path, getFileNameFromUrl(url))
        self.suffixPath = self.path + "." + suffix
        if isFile(self.suffixPath):
            if not replace:
                self.__quit = True
                logging.warning(f"由于文件{self.path}已在下载中，自动跳过下载！")
                return
        logging.info(f"开始使用DownloadKit下载{url}到{self.path}")
        self.downloadKit = downloadKit
        print(splitPath(self.suffixPath, 2))
        self.file = self.downloadKit.add(url,
                                         splitPath(self.path, 3),
                                         splitPath(self.suffixPath, 1),
                                         splitPath(self.suffixPath, 2)[1:],
                                         headers=header, split=True, allow_redirects=True, stream=True, timeout=15)
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
    def finish(self):
        """
        获得下载结果
        @return: success成功（只返回一次），downloading下载中，skipped已跳过，failed失败，finished已结束
        """
        if self.__finished:
            return "finished"
        if self.__quit:
            return "skipped"
        elif self.file.result == "success":
            if existPath(self.suffixPath):
                self.resultPath = movePath(self.suffixPath, self.path, self.replace)
                logging.info(f"成功使用DownloadKit下载{self.url}到{self.resultPath}！")
                self.__finished = True
                return "success"
            else:
                return "failed"
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
        self.file.cancel()
        self.file.session.close()
        self.downloadKit.cancel()
