from log import *
import urllib.parse
import requests, lxml, bs4, os
from DownloadKit import DownloadKit
from file import existPath, joinPath, isFile, isDir, splitPath, addRepeatSuffix, renamePath


def joinUrl(*urls):
    """
    拼接网址
    @param urls: 网址
    @return: 拼接结果
    """
    data: str = ""
    for i in urls:
        data = urllib.parse.urljoin(data, i)
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
    return os.path.basename(urllib.parse.urlparse(url).path)


def singleDownload(url: str, path: str, replace: bool = False):
    """
    下载文件
    @param url: 下载链接
    @param path: 下载后完整目录/文件名
    @param replace: 是否替换
    @return:
    """
    try:
        if existPath(path):
            if isFile(path) and not replace:
                logging.warning(f"由于文件{path}已存在，自动跳过单线程下载！")
                return False
            elif isDir(path):
                path = joinPath(path, getFileNameFromUrl(url))
        logging.info(f"正在单线程下载文件{url}到{path}！")
        response = requests.get(url, stream=True)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logging.info(f"已将文件{url}单线程下载到到{path}！")
        return existPath(path)
    except Exception as ex:
        logging.error(f"但下载文件{url}到{path}失败，报错信息：{ex}！")


downloadKit = DownloadKit(roads=32, file_exists="overwrite")


class MultiDownload:
    def __init__(self, url: str, path: str, wait: bool = True, replace: bool = False, suffix: str = "", header=None):
        """
        多线程下载，务必要通过self.result单独监视结果成功并在成功后运行self.finish()方法
        @param url: 下载链接
        @param path: 下载后完整目录/文件名
        @param wait: 是否等待
        @param replace: 是否替换
        @param suffix: 临时后缀名
        @param header: 请求头
        """
        self.path = path
        self.__quit = False
        if existPath(self.path):
            if isFile(self.path) and not replace:
                logging.warning(f"由于文件{self.path}已存在，自动跳过下载！")
                self.__quit = True
                return
            elif isDir(self.path):
                self.path = joinPath(self.path, getFileNameFromUrl(url))
        self.suffixPath = self.path + suffix
        if existPath(self.suffixPath):
            if isFile(self.suffixPath):
                if replace:
                    self.suffixPath = addRepeatSuffix(self.suffixPath)
                else:
                    self.__quit = True
                    logging.warning(f"由于文件{self.path}已在下载中，自动跳过下载！")
                    return
        logging.info(f"开始使用DownloadKit下载{url}到{self.path}")
        self.downloadKit = downloadKit
        self.file = self.downloadKit.add(url,
                                         splitPath(self.path, 3),
                                         splitPath(self.suffixPath, 0),
                                         splitPath(self.suffixPath, 2),
                                         headers=header, allow_redirects=True, stream=True, timeout=15)
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
        @return: success成功，downloading下载中，skipped已跳过，failed失败
        """
        if self.__quit:
            return "skipped"
        elif self.file.result == "success":
            if existPath(self.suffixPath):
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

    def finish(self):
        """
        完成下载时调用
        """
        if self.result == "success":
            renamePath(self.suffixPath,self.path)
            del self