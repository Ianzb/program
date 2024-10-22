from .log import *


class Data:
    def clearCharacters(self, text: str, mode: str | list | tuple = "escape+space"):
        """
        移除字符串中的指定类型字符
        @param text: 字符串
        @param mode: 处理模式，可传入字符串或列表或元组，“escape”表示常见转义字符，“space”表示空格，“slash”表示斜杠，“illegalPath”表示文件系统中禁止存在的字符，字符串使用“+”拼接多种选项，列表中依次填写选项。
        @return: 字符串
        """
        from re import sub
        if isinstance(mode, str):
            mode: list = mode.split("+")
        if "escape" in mode:
            text = sub(r"[\n\v\r\t]", "", text)
        if "space" in mode:
            text = text.replace(" ", "")
        if "slash" in mode:
            text = text.replace("/", "").replace("\\", "")
        if "illegalPath" in mode:
            text = sub(r'[*?"<>|]', "", text)
        return text

    def compareVersionCode(self, version1: str, version2: str):
        """
        比较版本号大小，仅支持如1.0.0的不含字符的版本号
        @param version1: 版本号1
        @param version2: 版本号2
        @return: 返回大的版本号
        """
        list1: list = version1.split(".")
        list2: list = version2.split(".")
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

    def sortVersionCode(self, version: list, reverse: bool = False, repeat: bool = False):
        """
        版本号列表排序
        @param version: 版本号列表
        @param reverse: 是否降序
        @param repeat: 是否允许重复版本
        @return: 排序
        """
        if not repeat:
            version = list(set(version))
        version.sort(key=lambda x: tuple(int(v) for v in x.split(".")), reverse=reverse)
        return version

    def numberAddUnit(self, value: int):
        """
        数字加单位
        @param value: 值
        @return: 字符串
        """
        units = ["", "万", "亿", "兆"]
        size = 10000.0
        for i in range(len(units)):
            if (value / size) < 1:
                return f"{value:.{i}f}{units[i]}"
            value = value / size
        return f"{value:.3f}兆"
