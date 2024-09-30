import logging

from setuptools.errors import FileError

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


def isSamePath(path1: str, path2: str):
    """
    判断路径是否相同
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
    判断路径是否为文件
    @param path: 路径
    @return: 是否为文件
    """
    return os.path.isfile(path) if existPath(path) else False


def isDir(path: str):
    """
    判断路径是否为目录
    @param path: 路径
    @return: 是否为目录
    """
    return os.path.isdir(path) if existPath(path) else False


def renamePath(old: str, new: str):
    """
    重命名路径
    @param old: 旧路径
    @param new: 新路径
    @return:
    """
    os.rename(old, new)
    return existPath(new)


def deleteFile(path: str, trash: bool = False, force: bool = False):
    """
    删除文件
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
    删除目录
    @param path: 目录路径
    @param trash: 是否删除到回收站
    @param force: 是否强制删除，优先级低于回收站
    @return: 是否删除成功
    """
    if not existPath(path):
        logging.warning(f"文件夹{path}不存在，无法删除！")
        return False
    try:
        if trash:
            send2trash.send2trash(path)
        elif force:
            easyCmd(f'rmdir /S /Q "{path}"', True)
        else:
            shutil.rmtree(path)
    except Exception as ex:
        logging.error(f"删除文件夹{path}失败，错误信息为{ex}，回收站删除模式为{trash}，强制删除模式为{force}。")
    return existPath(path)


def deletePath(path: str, trash: bool = False, force: bool = False):
    """
    删除文件或目录
    @param path: 文件或目录路径
    @param trash: 是否删除到回收站
    @param force: 是否强制删除，优先级低于回收站
    @return:
    """
    if isFile(path):
        deleteFile(path, trash, force)
    elif isDir(path):
        deleteDir(path, trash, force)


def splitPath(path: str, mode: int | str = 0):
    """
    分割路径信息
    @param path: 文件路径
    @param mode: 模式：0 文件完整名称 1 文件名称（无扩展名） 2 文件扩展名（有.） 3 文件所在目录
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
    创建目录
    @param path: 目录路径
    """
    if not existPath(path):
        os.makedirs(path)


def fileSize(path: str):
    """
    获取文件大小
    @param path: 文件路径
    @return: 文件大小
    """
    if isFile(path):
        return os.path.getsize(path)
    elif isDir(path):
        return sum([fileSize(joinPath(path, file)) for file in walkFile(path)])


def fileHash(path: str, mode: str = "md5"):
    """
    获取文件哈希值
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


def walkFile(path: str, mode: int = 0):
    """
    遍历目录
    @param path: 目录路径
    @param mode: 模式：0 包含所有层级文件 1 仅包含次级文件
    @return: 文件名列表
    """
    l1 = []
    if existPath(path):
        if mode == 0:
            if isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for file_name in file_lst:
                        l1.append(joinPath(path, file_name))
        if mode == 1:
            for i in os.listdir(path):
                if isFile(joinPath(path, i)):
                    l1.append(joinPath(path, i))
    return sorted(l1)


def walkDir(path: str, mode: int = 0):
    """
    遍历子文件夹
    @param path: 目录路径
    @param mode: 模式：0 包含所有层级文件夹 1 仅包含次级文件夹
    @return: 目录名列表
    """
    l1 = []
    if existPath(path):
        if mode == 0:
            if isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for dir_name in dir_lst:
                        l1.append(joinPath(path, dir_name))
        if mode == 1:
            for i in os.listdir(path):
                if isDir(joinPath(path, i)):
                    l1.append(joinPath(path, i))
    return sorted(l1)


def walkPath(path: str, mode: int = 0):
    """
    遍历子文件和子文件夹
    @param path: 目录路径
    @param mode: 模式：0 包含所有层级文件夹 1 仅包含次级文件夹
    @return: 目录名列表
    """
    l1 = []
    if existPath(path):
        if mode == 0:
            if isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for name in dir_lst + file_lst:
                        l1.append(joinPath(path, name))
        if mode == 1:
            for i in os.listdir(path):
                l1.append(joinPath(path, i))
    return sorted(l1)


def setOnlyRead(path: str, enable: bool):
    """
    只读权限
    @param path: 文件路径
    @param enable: 启用/禁用
    """
    from stat import S_IREAD, S_IWRITE
    if isFile(path):
        if enable:
            os.chmod(path, S_IREAD)
        else:
            os.chmod(path, S_IWRITE)


def addRepeatSuffix(path: str):
    """
    添加重复后缀（用于复制文件的时候解决名称重复问题）
    @param path: 新文件本身路径
    @return: 新文件本身路径
    """
    if isFile(path):
        i = 1
        while existPath(joinPath(splitPath(path, 3), splitPath(path, 1) + " (" + str(i) + ")" + splitPath(path, 2))):
            i += 1
        path = joinPath(splitPath(path, 3), splitPath(path, 1) + " (" + str(i) + ")" + splitPath(path, 2))
    elif isDir(path):
        i = 1
        while existPath(path + " (" + str(i) + ")"):
            i += 1
        path = path + " (" + str(i) + ")"
    return path


def _dirPathToSelfPath(old: str, new: str):
    """
    新文件夹所在路径转文件本身路径，用于复制文件等操作时，将传入的作为复制后文件所在位置的路径替换为复制后文件自身的路径
    @param old: 旧文件（夹）自身路径
    @param new: 新文件（夹）所在路径
    @return: 新文件本身路径
    """
    if isFile(new) or "." in splitPath(new, 0):
        pass
    else:
        new = joinPath(new, splitPath(old, 0))
    return new


def copyPath(old: str, new: str, replace: bool = False):
    """
    复制文件
    @param old: 旧文件（夹）自身路径
    @param new: 新文件（夹）所在或本身路径
    @param replace: 文件重复时是否替换，关闭时将在复制后位置添加序号
    @return: 是否成功
    """
    if not existPath(old):
        logging.error(f"文件{old}不存在，无法复制！")
        return False
    new = _dirPathToSelfPath(old, new)
    if existPath(new) and replace:
        logging.warning(f"文件{new}已存在，将尝试以{old}替换！")
    if not replace:
        new = addRepeatSuffix(new)
    if isFile(old):
        try:
            createDir(splitPath(new, 3))
            shutil.copy2(old, new)
        except Exception as ex:
            logging.error(f"复制文件失败，错误信息：{ex}。")
            return False
    elif isDir(old):
        try:
            shutil.copytree(old, new)
        except Exception as ex:
            logging.error(f"复制文件夹失败，错误信息：{ex}。")
            return False
    return new if existPath(new) else False


def movePath(old: str, new: str, replace: bool = False):
    """
    移动文件（夹）
    @param old: 旧文件（夹）自身路径
    @param new: 新文件（夹）所在或本身路径
    @param replace: 文件重复时是否替换，关闭时将在复制后位置添加序号
    """
    if not existPath(old):
        logging.error(f"文件{old}不存在，无法移动！")
        return False
    new = copyPath(old, new, replace)
    if new:
        deletePath(old)
    return new if existPath(new) and not existPath(old) else False


def clearDir(path: str):
    """
    清空文件夹（无法删除则跳过）
    @param path: 路径
    """
    if isDir(path):
        for i in walkPath(path, 1):
            deletePath(i)


def showFile(path: str):
    """
    在文件资源管理器中打开目录
    @param path: 路径
    """
    if isFile(path):
        easyCmd(f'explorer /select,"{path}"')
    else:
        easyCmd(f'explorer "{path}"')


def extractZip(path: str, goal: str, delete: bool = False):
    """
    解压zip文件
    @param path: zip文件路径
    @param goal: 解压到的目录路径
    @param delete: 解压后删除
    """
    import zipfile
    if existPath(path):
        try:
            file = zipfile.ZipFile(path)
            file.extractall(goal)
            file.close()
            if delete:
                deleteFile(path)
            logging.debug(f"{path}解压成功！")
        except Exception as ex:
            logging.warning(f"{path}解压失败{ex}！")
