import urllib.parse
import requests, lxml, bs4
from winerror import ERROR_SERIAL_NO_DEVICE


def joinUrl(*args):
    """
    拼接网址。
    @param args: 网址
    @return: 拼接结果
    """
    data: str = ""
    for i in args:
        data = urllib.parse.urljoin(data, i)
    return data


def getUrl(url: str, header=None, timeout: int | tuple = (5, 10), times: int = 5):
    """
    可重试的get请求。
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
        except:
            continue


def postUrl(url: str, json: dict, header=None, timeout: int | tuple = (5, 10), times: int = 5):
    """
    可重试的post请求。
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
        except:
            continue
