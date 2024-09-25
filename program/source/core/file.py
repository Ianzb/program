import logging

from log import *
import os, sys, shutil, send2trash
from system import easyCmd


def fileSizeAddUnit(value: int):
    """
    文件比特大小加单位（1024进制）。
    @param value: 值
    @return: 字符串
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return f"{value:.2f}{units[i]}"
        value = value / size
    return f"{value:.2f}BB"


def formatPathString(path: str):
    """
    格式化路径
    @param path: 路径
    @return: 格式化结果
    """
    return os.path.normpath(path)


def joinPath(*paths):
    """
    拼接路径。
    @param paths: 多个字符串参数
    @return:
    """
    return formatPathString(os.path.join("", *paths))


def isSameFile(path1: str, path2: str):
    """
    判断路径是否相同。
    @param path1: 路径1
    @param path2: 路径2
    @return: 是否相同
    """
    return os.path.samefile(path1, path2) if existPath(path1) and existPath(path2) else False


def existPath(path: str):
    """
    判断路径是否存在。
    @param path: 路径
    @return: 是否存在
    """
    return os.path.exists(path)


def isFile(path: str):
    """
    判断路径是否为文件。
    @param path: 路径
    @return: 是否为文件
    """
    return os.path.isfile(path) if existPath(path) else False


def isDir(path: str):
    """
    判断路径是否为目录。
    @param path: 路径
    @return: 是否为目录
    """
    return os.path.isdir(path) if existPath(path) else False


def deleteFile(path: str, trash: bool = False, force: bool = False):
    """
    删除文件。
    @param path: 文件路径
    @param trash: 是否删除到回收站
    @param force: 是否强制删除，优先级低于回收站
    @return:
    """
    if not existPath(path):
        logging.warning(f"文件{path}不存在，无法删除！")
        return
    try:
        if trash:
            send2trash.send2trash(path)
        elif force:
            easyCmd(f'del /F /Q /S "{path}"', True)
        else:
            os.remove(path)
    except Exception as ex:
        logging.error(f"删除文件{path}失败，错误信息为{ex}，回收站删除模式为{trash}，强制删除模式为{force}。")


def deleteDir(path: str, trash: bool = False, force: bool = False):
    """
    删除目录。
    @param path: 目录路径
    @param trash: 是否删除到回收站
    @param force: 是否强制删除，优先级低于回收站
    @return:
    """
    if not existPath(path):
        logging.warning(f"文件夹{path}不存在，无法删除！")
        return
    try:
        if trash:
            send2trash.send2trash(path)
        elif force:
            easyCmd(f'rmdir /S /Q "{path}"', True)
        else:
            shutil.rmtree(path)
    except Exception as ex:
        logging.error(f"删除文件夹{path}失败，错误信息为{ex}，回收站删除模式为{trash}，强制删除模式为{force}。")


def delete(path: str, trash: bool = False, force: bool = False):
    """
    删除文件或目录。
    @param path: 文件或目录路径
    @param trash: 是否删除到回收站
    @param force: 是否强制删除，优先级低于回收站
    @return:
    """
    if isFile(path):
        deleteFile(path, trash, force)
    elif isDir(path):
        deleteDir(path, trash, force)


def getFileHash(path: str, mode: str = "md5"):
    """
    获取文件哈希值。
    @param path: 文件路径
    @param mode: 哈希算法，支持md5、sha1、sha256
    @return: 哈希值
    """
    if not isFile(path):
        logging.warning(f"文件{path}不存在，无法获取哈希值。")
        return None
    if mode == "md5":
        from hashlib import md5
        return md5(open(path, 'rb').read()).hexdigest()
    elif mode == "sha1":
        from hashlib import sha1
        return sha1(open(path, 'rb').read()).hexdigest()
    elif mode == "sha256":
        from hashlib import sha256
        return sha256(open(path, 'rb').read()).hexdigest()


def splitPath(path: str, mode: int | str = 0):
    """
    分割路径信息。
    @param path: 文件路径
    @param mode: 模式：0 文件完整名称 1 文件名称 2 文件扩展名 3 文件所在目录
    @return: 文件名信息
    """
    if isinstance(mode, str):
        mode = int(mode)
    if mode == 0:
        return os.path.basename(path)
    elif mode == 1:
        return os.path.splitext(os.path.basename(path))[0]
    elif mode == 2:
        return os.path.splitext(os.path.basename(path))[1]
    elif mode == 3:
        return os.path.dirname(path)


def createDir(path: str):
    """
    创建目录。
    @param path: 目录路径
    """
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        logging.warning(f"目录{path}已存在，无需创建。")


def getFileSize(path: str):
    """
    获取文件大小。
    @param path: 文件路径
    @return: 文件大小
    """
    return os.path.getsize(path)
