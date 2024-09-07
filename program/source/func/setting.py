from .logging import *


class SettingFunctions:
    """
    设置相关函数
    """

    def __init__(self):
        self.DEFAULT_SETTING = {"theme": "Theme.AUTO",
                                "themeColor": "#0078D4",
                                "autoHide": True,
                                "downloadPath": program.DOWNLOAD_PATH,
                                "showWindow": False,
                                "micaEffect": True,
                                "showTray": True,
                                "hideWhenClose": True,
                                }
        self.file = open(program.SETTING_FILE_PATH, "a+t", encoding="utf-8")
        self.__read()

    def read(self, name: str):
        """
        读取设置
        @param name: 选项名称
        @return: 选项内容
        """
        logging.debug(f"读取设置{name}")
        try:
            return self.settings[name]
        except:
            self.settings[name] = self.DEFAULT_SETTING[name]
            self.__save()
            return self.DEFAULT_SETTING[name]

    def __read(self):
        self.file.seek(0)
        try:
            self.settings = json.loads(self.file.read())
        except:
            self.settings = self.DEFAULT_SETTING
            self.__save()

    def save(self, name: str, data):
        """
        保存设置
        @param name: 选项名称
        @param data: 选项数据
        """
        logging.debug(f"保存设置{name}：{data}")
        self.settings[name] = data
        self.__save()

    def __save(self):
        self.file.seek(0)
        self.file.truncate()
        self.file.write(json.dumps(self.settings))
        self.file.flush()

    def reset(self, name=None):
        """
        重置设置
        @param name: 选项名称
        """
        if name:
            self.save(name, self.DEFAULT_SETTING[name])
        else:
            self.settings = self.DEFAULT_SETTING
            self.__save()
            program.restart()

    def add(self, name: str, data):
        """
        添加设置项
        @param name: 选项名称
        @param data: 默认数据
        """
        self.DEFAULT_SETTING[name] = data
        if name not in self.settings.keys():
            self.save(name, data)

    def adds(self, data: dict):
        """
        批量添加设置项
        @param data: 数据
        """
        for k, v in data.items():
            self.add(k, v)


setting = SettingFunctions()
