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

    def get(self, name: str, addon_id: str = None):
        """
        读取设置
        如果传入 addon_id，则优先从对应插件的顶级键下读取。
        @param name: 选项名称
        @param addon_id: 可选，插件 id
        @return: 选项内容
        """
        return self.read(name, addon_id=addon_id)

    def read(self, name: str, addon_id: str = None):
        """
        读取设置
        @param name: 选项名称
        @param addon_id: 可选，插件 id；如果提供则优先在该插件的命名空间中查找
        @return: 选项内容
        """
        # 先尝试插件命名空间
        try:
            if addon_id:
                addon_section = self.last_setting.get(addon_id)
                if isinstance(addon_section, dict) and name in addon_section:
                    return addon_section.get(name)
        except Exception:
            logging.debug(f"读取插件设置时出错 addon_id={addon_id}, name={name}：{traceback.format_exc()}")

        # 再尝试全局设置（已保存到文件中的顶级键）
        if name in self.last_setting:
            return self.last_setting.get(name)

        # 最后返回默认设置
        return self.DEFAULT_SETTING.get(name)

    def __read(self):
        if not zb.existPath(program.SETTING_FILE_PATH):
            with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.DEFAULT_SETTING, indent=2, ensure_ascii=False))
        try:
            with open(program.SETTING_FILE_PATH, "r", encoding="utf-8") as file:
                self.last_setting = json.load(file)
        except:
            self.last_setting = deepcopy(self.DEFAULT_SETTING)
            self.reset()
            self.errorState = True
            logging.error(f"设置文件数据错误，已自动恢复至默认选项，错误信息：{traceback.format_exc()}！")

    def set(self, name: str, data, addon_id: str = None):
        """
        保存设置；若提供 addon_id，则保存到以 addon_id 为顶级键的字典中。
        @param name: 选项名称
        @param data: 选项数据
        @param addon_id: 可选，插件 id
        """
        self.save(name, data, addon_id=addon_id)

    def save(self, name: str, data, addon_id: str = None):
        """
        保存设置
        @param name: 选项名称
        @param data: 选项数据
        @param addon_id: 可选，插件 id
        """
        logging.debug(f"保存设置{name}：{data} (addon_id={addon_id})")
        if addon_id:
            # 确保插件顶级键存在且为 dict
            if addon_id not in self.last_setting or not isinstance(self.last_setting.get(addon_id), dict):
                self.last_setting[addon_id] = {}
            self.last_setting[addon_id][name] = data
        else:
            self.last_setting[name] = data
        # 触发变更事件并写入文件
        try:
            self.changeEvent(name)
        except Exception:
            logging.debug(f"触发 changeEvent 失败：{traceback.format_exc()}")
        self.__save()

    def __save(self):
        with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.last_setting, indent=2, ensure_ascii=False))
        self.last_timestamp = os.path.getmtime(program.SETTING_FILE_PATH)

    def reset(self, name=None, addon_id: str = None):
        """
        重置设置
        @param name: 选项名称
        @param addon_id: 可选，插件 id；若提供则仅重置该插件命名空间内的键
        """
        if name:
            # 仅重置单个键
            if addon_id:
                # 确保插件命名空间存在
                if addon_id not in self.last_setting or not isinstance(self.last_setting.get(addon_id), dict):
                    self.last_setting[addon_id] = {}
                # 如果 DEFAULT_SETTING 中存在默认值，则写入默认值；否则删除该键（避免写入 None）
                if name in self.DEFAULT_SETTING.get(addon_id, {}):
                    self.save(name, self.DEFAULT_SETTING.get(addon_id).get(name), addon_id=addon_id)
                # 触发变更事件
                try:
                    self.changeEvent(name)
                except Exception:
                    logging.debug(f"触发 changeEvent 失败：{traceback.format_exc()}")
            else:
                # 全局键按原逻辑重置为默认（可能为 None）
                self.save(name, self.DEFAULT_SETTING.get(name))
                try:
                    self.changeEvent(name)
                except Exception:
                    logging.debug(f"触发 changeEvent 失败：{traceback.format_exc()}")
        else:
            logging.info("开始重置程序设置！")
            l = self.__compare(self.DEFAULT_SETTING, self.last_setting)
            self.last_setting = deepcopy(self.DEFAULT_SETTING)
            self.__save()
            for i in l:
                self.changeEvent(i)
            logging.info("程序设置重置完成！")

    def add(self, name: str, data, addon_id: str = None):
        """
        添加设置项
        @param name: 选项名称
        @param data: 默认数据
        @param addon_id: 可选，插件 id；若提供则把默认值放在插件命名空间下
        """
        if addon_id:
            # 在插件空间中添加默认值（但不覆盖已有的）
            if addon_id not in self.last_setting or not isinstance(self.last_setting.get(addon_id), dict):
                self.last_setting[addon_id] = {}
            if name not in self.last_setting[addon_id].keys():
                self.last_setting[addon_id][name] = data
                self.__save()
            if addon_id not in self.DEFAULT_SETTING.keys():
                self.DEFAULT_SETTING[addon_id] = {}
            self.DEFAULT_SETTING[addon_id][name] = data
        else:
            self.DEFAULT_SETTING[name] = data
            if name not in self.last_setting.keys():
                self.save(name, data)

    def adds(self, data: dict, addon_id: str = None):
        """
        批量添加设置项
        @param data: 数据
        @param addon_id: 可选，插件 id
        """
        for k, v in data.items():
            self.add(k, v, addon_id=addon_id)

    def changeEvent(self, name: str):
        """
        修改设置项事件
        @param name: 名称
        """
        logging.info(f"设置项{name}发生更改，已同步！")
        try:
            self.changeSignal.emit(name)
        except Exception:
            logging.debug(f"emit changeSignal 失败：{traceback.format_exc()}")

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
            except:
                logging.error(f"设置文件数据数据错误，错误信息：{traceback.format_exc()}！")

    def __compare(self, old: dict, new: dict):
        """
        递归比较两个 dict，返回发生变化的最内层键名列表（不带插件 id 前缀）。
        """
        keys = []

        for k in old.keys():
            if k in new.keys():
                if isinstance(old[k], dict) and isinstance(new[k], dict):
                    inner = self.__compare(old[k], new[k])
                    keys.extend(inner)
                else:
                    if old[k] != new[k]:
                        keys.append(k)
            else:
                if isinstance(old[k], dict):
                    keys.extend(list(self.__gather_keys(old[k])))
                else:
                    keys.append(k)

        for k in new.keys():
            if k not in old.keys():
                if isinstance(new[k], dict):
                    keys.extend(list(self.__gather_keys(new[k])))
                else:
                    keys.append(k)

        return sorted(list(set(keys)))

    def __gather_keys(self, d: dict):
        """收集嵌套 dict 的所有最内层键名"""
        for k, v in d.items():
            if isinstance(v, dict):
                yield from self.__gather_keys(v)
            else:
                yield k


setting = SettingFunctions()
