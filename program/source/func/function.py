from .setting import *


class ProcessFunctions:
    """
    数据处理函数
    """

    def clearString(self, data: str) -> str:
        """
        清理字符串\n\r空格符号
        @param data: 源字符串
        @return: 处理结果
        """
        data = data.replace(r"\n", "").replace(r"\r", "").replace(r"\t", "").strip()
        return data

    def removeIllegalPath(self, path: str, mode: int = 0) -> str:
        """
        去除路径中的非法字符
        @param path: 路径
        @param mode: 模式：0 全部替换 1 不替换斜杠
        @return: 去除非法字符后的字符串
        """
        import re
        if mode == 0:
            return re.sub(r'[\\\/:*?"<>|]', "", path)
        elif mode == 1:
            return re.sub(r'[*?"<>|]', "", path)

    def compareVersion(self, version1: str, version2: str) -> str:
        """
        比较版本号大小
        @param version1: 版本号1
        @param version2: 版本号2
        @return: 返回大的版本号
        """
        list1 = version1.split(".")
        list2 = version2.split(".")
        for i in range(len(list1)) if len(list1) < len(list2) else range(len(list2)):
            if int(list1[i]) == int(list2[i]):
                pass
            elif int(list1[i]) < int(list2[i]):
                return version2
            else:
                return version1
        if len(list1) >= len(list2):
            return version1
        else:
            return version2

    def sortVersion(self, version: list, reverse: bool = False, clear_repeat: bool = True) -> list:
        """
        版本号列表排序
        @param version: 版本号列表
        @param reverse: 是否逆序
        @param clear_repeat: 是否清除重复版本
        @return: 排序
        """
        if clear_repeat:
            version = list(set(version))
        version.sort(key=lambda x: tuple(int(v) for v in x.split(".")), reverse=reverse)
        return version

    def urlJoin(self, *args):
        """
        拼接网址
        @param args: 网址
        @return: 拼接结果
        """
        import urllib.parse
        data = ""
        for i in range(len(args)):
            data = urllib.parse.urljoin(data, args[i])
        return data

    def cmd(self, command: str, pause: bool = False) -> str:
        """
        简单的使用cmd
        @param command: 命令
        @param pause: 是否等待并返回输出结果
        @return: 输出结果
        """
        logging.debug(f"cmd执行命令{command}")
        value = os.popen(command)
        if pause:
            return value.read()

    def requestGet(self, url: str, header=None, timeout=(5, 10), is_text: bool = True, try_times: int = 5):
        """
        可重试的get请求
        @param url: 链接
        @param header: 请求头
        @param timeout: 超时
        @param is_text: 文本
        @param try_times: 重试次数
        @return:
        """
        logging.info(f"正在发送Get请求到{url}")
        for i in range(try_times):
            try:
                response = requests.get(url, headers=header, stream=True, timeout=timeout)
                if is_text:
                    response.encoding = "utf-8"
                    response = response.text
                else:
                    response = response.content
                return response
            except:
                continue

    def requestPost(self, url: str, json: dict, header=None, timeout=(5, 10), try_times: int = 5):
        """
        可重试的post请求
        @param url: 链接
        @param json: 发送数据
        @param header: 请求头
        @param timeout: 超时
        @param try_times: 重试次数
        @return:
        """
        logging.info(f"正在发送Post请求到{url}")
        for i in range(try_times):
            try:
                response = requests.post(url, headers=header, json=json, timeout=timeout)
                return response
            except:
                continue

    def numberAddUnit(self, value: int) -> str:
        """
        数字加单位
        @param value: 值
        @return: 字符串
        """
        units = ["", "万", "亿", "兆"]
        size = 10000.0
        for i in range(len(units)):
            if (value / size) < 1:
                return f"%.{i}f%s" % (value, units[i])
            value = value / size

    def fileSizeAddUnit(self, value: int) -> str:
        """
        文件比特大小加单位
        @param value: 值
        @return: 字符串
        """
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size


class FileFunctions(ProcessFunctions):
    """
    文件处理函数
    """

    def __init__(self):
        super().__init__()

    def formatPath(self, path: str) -> str:
        """
        格式化路径
        @param path: 路径
        @return: 格式化结果
        """
        path = os.path.normpath(path).replace("//", r"\ "[:-1]).replace("\\ "[:-1], r"\ "[:-1])
        return path

    def pathJoin(self, *data) -> str:
        """
        拼接路径
        @param data: 多个字符串参数
        @return: 拼接后的字符串
        """
        path = ""
        for i in data:
            path = os.path.join(path, str(i))
        return self.formatPath(path)

    def isSameFile(self, path1: str, path2: str) -> bool:
        """
        判断路径是否相同
        @param path1: 路径1
        @param path2: 路径2
        @return: 是否相同
        """

        return self.formatPath(path1) == self.formatPath(path2)

    def existPath(self, path: str) -> bool:
        """
        文件是否存在
        @param path: 文件路径
        @return: bool
        """
        return os.path.exists(path)

    def isFile(self, path: str) -> bool:
        """
        文件是否为文件
        @param path: 文件路径
        @return: bool
        """
        if not self.existPath(path):
            return False
        return os.path.isfile(path)

    def isDir(self, path: str) -> bool:
        """
        文件是否为目录
        @param path: 文件路径
        @return: bool
        """
        if not self.existPath(path):
            return False
        return os.path.isdir(path)

    def setOnlyRead(self, path: str, enable: bool):
        """
        只读权限
        @param path: 文件路径
        @param enable: 启用/禁用
        """
        from stat import S_IREAD, S_IWRITE
        if self.isFile(path):
            if enable:
                os.chmod(path, S_IREAD)
            else:
                os.chmod(path, S_IWRITE)

    def delete(self, path: str, trash: bool = False, force: bool = False):
        """
        删除文件/目录
        @param path: 文件路径
        @param trash: 是否发送到回收站
        @param force: 是否使用命令行强制删除
        """
        try:
            if trash:
                if self.existPath(path):
                    send2trash(path)
            else:
                if self.isFile(path):
                    self.setOnlyRead(path, False)
                    os.remove(path)
                elif self.isDir(path):
                    shutil.rmtree(path)
        except Exception as ex:
            if self.isFile(path):
                self.cmd(f'del /F /Q "{path}"', True)
            elif self.isDir(path):
                self.cmd(f'rmdir /S /Q "{path}"', True)
            logging.warning(f"文件{path}无法删除{ex}")

    def getMD5(self, path: str) -> str:
        """
        获取文件MD5值
        @param path: 文件路径
        @return: MD5值
        """
        from hashlib import md5
        if self.isFile(path):
            data = open(path, "rb").read()
            return md5(data).hexdigest()

    def getSha1(self, path: str) -> str:
        """
        获取文件sha1值
        @param path: 文件路径
        @return: sha1值
        """
        from hashlib import sha1
        if self.isFile(path):
            data = open(path, "rb").read()
            return sha1(data).hexdigest()

    def splitPath(self, path: str, mode: int = 0) -> str:
        """
        分割路径信息
        @param path: 文件路径
        @param mode: 模式：0 文件完整名称 1 文件名称 2 文件扩展名 3 文件所在目录
        @return: 文件名信息
        """
        if mode == 0:
            return os.path.basename(path)
        if mode == 1:
            return os.path.splitext(os.path.basename(path))[0]
        if mode == 2:
            return os.path.splitext(os.path.basename(path))[1]
        if mode == 3:
            return os.path.dirname(path)

    def makeDir(self, path: str):
        """
        创建文件夹
        @param path: 文件路径
        """
        if not self.existPath(path):
            os.makedirs(path)

    def getSize(self, path: str) -> int:
        """
        获取文件/夹大小
        @param path: 文件路径
        @return: 文件大小
        """
        if self.isFile(path):
            return os.path.getsize(path)
        elif self.isDir(path):
            return sum([self.getSize(self.pathJoin(path, file)) for file in self.walkFile(path)])

    def walkDir(self, path: str, mode=0) -> list:
        """
        遍历子文件夹
        @param path: 文件夹路径
        @param mode: 模式：0 包含所有层级文件夹 1 仅包含次级文件夹
        @return: 文件夹路径列表
        """
        list1 = []
        if self.existPath(path):
            if mode == 0:
                if self.isDir(path):
                    paths = os.walk(path)
                    for path, dir_lst, file_lst in paths:
                        for dir_name in dir_lst:
                            list1.append(self.pathJoin(path, dir_name))
            if mode == 1:
                for i in os.listdir(path):
                    if self.isDir(self.pathJoin(path, i)):
                        list1.append(self.pathJoin(path, i))
            if not list1:
                list1 = []
        return list1

    def walkFile(self, path: str, mode=0) -> list:
        """
        遍历子文件
        @param path: 文件夹路径
        @param mode: 模式：0 包含所有层级文件 1 仅包含次级文件
        @return: 文件路径列表
        """
        list1 = []
        if self.existPath(path):
            if mode == 0:
                paths = os.walk(path)
                if self.isDir(path):
                    for path, dir_lst, file_lst in paths:
                        for file_name in file_lst:
                            list1.append(self.pathJoin(path, file_name))
            if mode == 1:
                for i in os.listdir(path):
                    if self.isFile(self.pathJoin(path, i)):
                        list1.append(self.pathJoin(path, i))
            if not list1:
                list1 = []
        return list1

    def copyFile(self, old: str, new: str):
        """
        复制文件
        @param old: 旧文件（夹）路径
        @param new: 新文件（夹）路径
        """
        if self.isFile(old):
            if self.isDir(new) or "." not in new:
                self.makeDir(new)
                new = self.pathJoin(new, self.splitPath(old))
            if self.existPath(new):
                i = 1
                while self.existPath(self.pathJoin(self.splitPath(new, 3), self.splitPath(new, 1) + " (" + str(i) + ")" + self.splitPath(new, 2))):
                    i = i + 1
                new = self.pathJoin(self.splitPath(new, 3), self.splitPath(new, 1) + " (" + str(i) + ")" + self.splitPath(new, 2))
            try:
                shutil.copy(self.pathJoin(old), self.pathJoin(new))
            except:
                self.setOnlyRead(old, False)
                shutil.copy(self.pathJoin(old), self.pathJoin(new))
        if self.isDir(old):
            if self.existPath(new):
                i = 1
                while self.existPath(new + " (" + str(i) + ")"):
                    i = i + 1
                new = new + " (" + str(i) + ")"
            try:
                shutil.copytree(self.pathJoin(old), self.pathJoin(new))
            except:
                try:
                    for i in self.walkFile(old):
                        self.setOnlyRead(i, False)
                    shutil.copytree(self.pathJoin(old), self.pathJoin(new))
                except:
                    pass

    def moveFile(self, old: str, new: str):
        """
        移动文件
        @param old: 旧文件（夹）路径
        @param new: 新文件（夹）路径
        """
        self.copyFile(old, new)
        if self.existPath(old):
            self.delete(old)

    def clearDir(self, path: str):
        """
        清空文件夹（无法删除则跳过）
        @param path: 路径
        """
        if self.isDir(path):
            for i in self.walkDir(path, 1):
                self.delete(i)
            for i in self.walkFile(path, 1):
                self.delete(i)

    def clearProgramCache(self):
        """
        清理本软件缓存
        """
        try:
            logging.reset()
            self.clearDir(f.pathJoin(program.DATA_PATH, "cache"))
        except:
            pass

    def showFile(self, path: str):
        """
        在文件资源管理器中打开目录
        @param path: 路径
        """
        if path and self.existPath(path):
            if f.isDir(path):
                os.startfile(path)
            else:
                f.cmd(f"explorer /select,{path}")

    def extractZip(self, path: str, goal: str, delete=False):
        """
        解压zip文件
        @param path: zip文件路径
        @param goal: 解压到的目录路径
        @param delete: 解压后删除
        """
        import zipfile
        if self.existPath(path):
            try:
                file = zipfile.ZipFile(path)
                file.extractall(goal)
                file.close()
                if delete:
                    self.delete(path)
                logging.debug(f"{path}解压成功")
            except Exception as ex:
                logging.warning(f"{path}解压失败{ex}")


class ProgramFunctions(FileFunctions):
    """
    应用函数
    """

    def __init__(self):
        super().__init__()

    def downloadFile(self, link: str, path: str):
        """
        下载文件
        @param link: 文件链接
        @param path: 下载路径
        """
        try:
            path = os.path.abspath(path)
            data = self.requestGet(link, program.REQUEST_HEADER, is_text=False, try_times=2)
            self.makeDir(self.splitPath(path, 3))
            with open(path, "wb") as file:
                file.write(data)
            logging.debug(f"文件{link}下载成功")
        except Exception as ex:
            logging.warning(f"文件{link}下载失败{ex}")

    def addToStartup(self, mode: bool = True):
        """
        添加开机自启动
        @param mode: True添加/False删除
        """
        import win32api, win32con
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_ALL_ACCESS)
        try:
            if mode:
                win32api.RegSetValueEx(key, program.NAME, 0, win32con.REG_SZ, f"{program.MAIN_FILE_PATH} startup")
                win32api.RegCloseKey(key)
                logging.debug("启动项添加成功")
            else:
                win32api.RegDeleteValue(key, program.NAME)
                win32api.RegCloseKey(key)
                logging.debug("启动项删除成功")
        except Exception as ex:
            logging.warning(f"启动项编辑失败{ex}")

    def checkStartup(self):
        """
        检查开机自启动
        @return: 是否
        """
        import win32api, win32con
        try:
            key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, win32con.KEY_READ)
            win32api.RegQueryValueEx(key, program.NAME)
            win32api.RegCloseKey(key)
            return True
        except win32api.error:
            return False

    def getNewestVersion(self) -> str:
        """
        获取程序最新版本
        @return: 程序最新版本
        """
        response = self.requestGet(program.UPDATE_URL, program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)["version"]
        logging.info(f"程序最新版本：{data}")
        return data

    def getAddonDict(self) -> dict:
        """
        获取插件字典
        @return: 字典
        """
        response = self.requestGet(program.ADDON_URL, program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)
        logging.debug("插件信息获取成功")
        return data

    def getAddonInfo(self, url: str) -> dict:
        """
        获取指定插件信息
        @param url: 链接
        @return: 信息
        """
        if not url.endswith("/"):
            url += "/"
        response = self.requestGet(self.urlJoin(url, "addon.json"), program.REQUEST_HEADER, (15, 30))
        data = json.loads(response)
        data["url"] = url
        logging.debug(f"插件{data["name"]}信息获取成功")
        return data

    def downloadAddon(self, data: dict):
        """
        下载插件
        @param data: 插件信息
        """
        self.makeDir(self.pathJoin(program.ADDON_PATH, data["id"]))
        if "__init__.py" not in data["file"]:
            open(self.pathJoin(program.ADDON_PATH, data["id"], "__init__.py"), "w", encoding="utf-8").close()
        if "addon.json" not in data["file"]:
            data["file"].append("addon.json")
        for i in data["file"]:
            if self.splitPath(self.pathJoin(program.ADDON_PATH, data["id"], i), 2) == ".zip":
                self.downloadFile(self.urlJoin(data["url"], i), self.pathJoin(program.ADDON_PATH, i).replace("init.py", "__init__.py"))
                f.extractZip(self.pathJoin(program.ADDON_PATH, i), program.ADDON_PATH, True)
            else:
                self.downloadFile(self.urlJoin(data["url"], i), self.pathJoin(program.ADDON_PATH, data["id"], i).replace("init.py", "__init__.py"))
        logging.debug(f"插件{data["name"]}下载成功")

    def importAddon(self, path: str):
        """
        导入本体插件
        @param path: 目录
        """
        self.extractZip(path, program.cache(self.splitPath(path)))
        if self.existPath(self.pathJoin(program.cache(self.splitPath(path)), "addon.json")):
            with open(self.pathJoin(program.cache(self.splitPath(path)), "addon.json"), "r", encoding="utf-8") as file:
                data = json.loads(file.read())
            self.extractZip(path, self.pathJoin(program.ADDON_PATH, data[id]))
        else:
            for i in self.walkDir(program.cache(self.splitPath(path))):
                if self.existPath(self.pathJoin(i, "addon.json")):
                    with open(self.pathJoin(i, "addon.json"), "r", encoding="utf-8") as file:
                        data = json.loads(file.read())
                    break
            self.extractZip(path, program.ADDON_PATH)
        self.delete(program.cache(self.splitPath(path)))
        return data

    def getInstalledAddonInfo(self) -> dict:
        """
        获取本地插件信息
        @return: 信息
        """
        data = {}
        for i in f.walkDir(program.ADDON_PATH, 1):
            if f.existPath(f.pathJoin(i, "addon.json")):
                with open(f.pathJoin(i, "addon.json"), encoding="utf-8") as file:
                    data[f.splitPath(i)] = json.loads(file.read())
        return data


class DownloadFile:
    def __init__(self, link: str, path: str, wait: bool = True, suffix: str = "", header=None):
        """
        下载
        @param link: 链接
        @param path: 路径
        @param wait: 是否等待
        @param suffix: 临时后缀名
        @param header: 请求头
        """
        suffix = suffix.removeprefix(".")
        if f.isDir(path):
            path = f.pathJoin(path, link.split("/")[-1])
        if f.existPath(path):
            i = 1
            while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))) or f.existPath(
                    f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2) + ("." if suffix else "") + suffix)):
                i = i + 1
            path = f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))
        self.path = path + ("." if suffix else "") + suffix
        logging.info(f"开始使用DownloadKit下载{link}到{self.path}")
        self.d = DownloadKit(f.splitPath(path, 3))
        self.file = self.d.add(link, rename=f.splitPath(path, 0), suffix=suffix, headers=header, allow_redirects=True, file_exists="skip")
        if wait:
            self.file.wait()

    def rate(self):
        return int(self.file.rate) if self.file.rate else 0

    def result(self):
        if self.file.result == "success":
            return True
        elif self.file.result == None:
            return None
        elif self.file.result == "skipped":
            return False

    def stop(self):
        self.file.cancel()
        self.file.session.close()
        self.d.cancel()

    def delete(self):
        self.file.del_file()


f = ProgramFunctions()
