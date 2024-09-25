from log import *
import urllib.parse
import requests, lxml, bs4
from winerror import ERROR_SERIAL_NO_DEVICE


def joinUrl(*urls):
    """
    拼接网址。
    @param urls: 网址
    @return: 拼接结果
    """
    data: str = ""
    for i in urls:
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
        except Exception as ex:
            logging.warning(f"第{i + 1}次Get请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Get请求{url}失败！")


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
        except Exception as ex:
            logging.warning(f"第{i + 1}次Post请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Post请求{url}失败！")
