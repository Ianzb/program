from .program import *


class SettingFunctions(QObject):
    """
    设置相关函数
    """
    DEFAULT_SETTING = {"theme": "Theme.AUTO",
                       "themeColor": "default",
                       "autoHide": True,
                       "downloadPath": zb.DOWNLOAD_PATH(),
                       "showWindow": False,
                       "micaEffect": True,
                       "showTray": True,
                       "hideWhenClose": True,
                       }
    changeSignal = pyqtSignal(str)
    errorState = False  # 错误信息

    def __init__(self):
        super().__init__()
        program.THREAD_POOL.submit(self.checkFileChange)
        self.__read()

    def get(self, name: str):
        """
        读取设置
        @param name: 选项名称
        @return: 选项内容
        """
        return self.read(name)

    def read(self, name: str):
        """
        读取设置
        @param name: 选项名称
        @return: 选项内容
        """
        return self.last_setting.get(name, self.DEFAULT_SETTING[name])

    def __read(self):
        if not zb.existPath(program.SETTING_FILE_PATH):
            with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.DEFAULT_SETTING, indent=2, ensure_ascii=False))
        try:
            with open(program.SETTING_FILE_PATH, "r", encoding="utf-8") as file:
                self.last_setting = json.load(file)
        except Exception as ex:
            self.last_setting = deepcopy(self.DEFAULT_SETTING)
            self.reset()
            self.errorState = True
            logging.error(f"设置文件数据错误，已自动恢复至默认选项，错误信息：{ex}！")

    def set(self, name: str, data):
        """
        保存设置
        @param name: 选项名称
        @param data: 选项数据
        """
        self.save(name, data)

    def save(self, name: str, data):
        """
        保存设置
        @param name: 选项名称
        @param data: 选项数据
        """
        logging.debug(f"保存设置{name}：{data}")
        self.last_setting[name] = data
        self.changeEvent(name)
        self.__save()

    def __save(self):
        with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.last_setting, indent=2, ensure_ascii=False))
        self.last_timestamp = os.path.getmtime(program.SETTING_FILE_PATH)

    def reset(self, name=None):
        """
        重置设置
        @param name: 选项名称
        """
        if name:
            self.save(name, self.DEFAULT_SETTING[name])
            self.changeEvent(name)
        else:
            logging.info("开始重置程序设置！")
            l = self.__compare(self.DEFAULT_SETTING, self.last_setting)
            self.last_setting = deepcopy(self.DEFAULT_SETTING)
            self.__save()
            for i in l:
                self.changeEvent(i)
            logging.info("程序设置重置完成！")

    def add(self, name: str, data):
        """
        添加设置项
        @param name: 选项名称
        @param data: 默认数据
        """
        self.DEFAULT_SETTING[name] = data
        if name not in self.last_setting.keys():
            self.save(name, data)

    def adds(self, data: dict):
        """
        批量添加设置项
        @param data: 数据
        """
        for k, v in data.items():
            self.add(k, v)

    def changeEvent(self, name: str):
        """
        修改设置项事件
        @param name: 名称
        """
        logging.info(f"设置项{name}发生更改，已同步！")
        self.changeSignal.emit(name)

    def signalConnect(self, func):
        """
        连接信号，用于动态重载设置
        @param func: 函数名
        """
        self.changeSignal.connect(func)

    def checkFileChange(self):
        """
        检查设置文件是否被修改
        """
        from time import sleep
        self.last_timestamp = os.path.getmtime(program.SETTING_FILE_PATH)
        while True:
            sleep(0.5)
            try:
                current_timestamp = os.path.getmtime(program.SETTING_FILE_PATH)
                if current_timestamp != self.last_timestamp:
                    self.last_timestamp = current_timestamp
                    with open(program.SETTING_FILE_PATH, "r", encoding="utf-8") as file:
                        self.current_setting = json.load(file)
                    l = self.__compare(self.current_setting, self.last_setting)
                    self.last_setting = self.current_setting
                    for i in l:
                        self.changeEvent(i)
            except Exception as ex:
                logging.error(f"设置文件数据数据错误，错误信息：{ex}！")

    def __compare(self, old: dict, new: dict):
        keys = []
        for k in old.keys():
            if k in new.keys() and old[k] != new[k]:
                keys.append(k)
            elif k not in new.keys():
                keys.append(k)
        for k in new.keys():
            if k not in old.keys():
                keys.append(k)
        return sorted(list(set(keys)))


setting = SettingFunctions()
