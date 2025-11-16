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
                       "windowEffect": "Mica",
                       "showTray": True,
                       "hideWhenClose": True,
                       "addonSettings": {},
                       }
    changeSignal = pyqtSignal(str)
    errorState = False  # 错误信息

    def __init__(self):
        super().__init__()
        program.THREAD_POOL.submit(self.checkFileChange)

        if not zb.existPath(program.SETTING_FILE_PATH):
            with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.DEFAULT_SETTING, indent=4, ensure_ascii=False))
        try:
            with open(program.SETTING_FILE_PATH, "r", encoding="utf-8") as file:
                self.last_setting = json.load(file)
        except:
            self.last_setting = deepcopy(self.DEFAULT_SETTING)
            self.reset()
            self.errorState = True
            logging.error(f"设置文件数据错误，已自动恢复至默认选项，错误信息：{traceback.format_exc()}！")

    def _get_by_path(self, data_dict: dict, path: str):
        """
        通过路径获取字典中的值
        @param data_dict: 数据字典
        @param path: 路径，使用 "/" 分隔
        @return: 值或 None
        """
        keys = path.strip("/").split("/")
        current = data_dict
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _set_by_path(self, data_dict: dict, path: str, value):
        """
        通过路径设置字典中的值
        @param data_dict: 数据字典
        @param path: 路径，使用 "/" 分隔
        @param value: 要设置的值
        """
        keys = path.strip("/").split("/")
        current = data_dict
        # 遍历到倒数第二个键，确保路径存在
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        # 设置最后一个键的值
        current[keys[-1]] = value

    def _delete_by_path(self, data_dict: dict, path: str):
        """
        通过路径删除字典中的键
        @param data_dict: 数据字典
        @param path: 路径，使用 "/" 分隔
        @return: 是否成功删除
        """
        keys = path.strip("/").split("/")
        current = data_dict
        # 遍历到倒数第二个键
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                return False
            current = current[key]
        # 删除最后一个键
        if keys[-1] in current:
            del current[keys[-1]]
            return True
        return False

    def _path_exists(self, data_dict: dict, path: str):
        """
        检查路径是否存在
        @param data_dict: 数据字典
        @param path: 路径，使用 "/" 分隔
        @return: 是否存在
        """
        return self._get_by_path(data_dict, path) is not None

    def get(self, path: str):
        """
        读取设置
        @param path: 设置路径
        @return: 选项内容
        """
        return self.read(path)

    def read(self, path: str):
        """
        读取设置
        @param path: 设置路径
        @return: 选项内容
        """
        # 先从当前设置中读取
        current_value = self._get_by_path(self.last_setting, path)
        if current_value is not None:
            return current_value

        # 如果当前设置中没有，从默认设置中读取
        default_value = self._get_by_path(self.DEFAULT_SETTING, path)
        return default_value

    def set(self, path: str, data):
        """
        保存设置
        @param path: 设置路径
        @param data: 选项数据
        """
        self.save(path, data)

    def save(self, path: str, data):
        """
        保存设置
        @param path: 设置路径
        @param data: 选项数据
        """
        logging.debug(f"保存设置 {path}：{data}")

        # 设置值
        self._set_by_path(self.last_setting, path, data)

        # 触发变更事件并写入文件
        try:
            self.changeEvent(path)
        except Exception:
            logging.debug(f"触发 changeEvent 失败：{traceback.format_exc()}")
        self.__save()

    def __save(self):
        with open(program.SETTING_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.last_setting, indent=4, ensure_ascii=False))
        self.last_timestamp = os.path.getmtime(program.SETTING_FILE_PATH)

    def reset(self, path: str = None):
        """
        重置设置
        @param path: 设置路径，如为 None 则重置所有设置
        """
        if path:
            # 重置单个路径
            default_value = self._get_by_path(self.DEFAULT_SETTING, path)
            if default_value is not None:
                self.save(path, default_value)
            else:
                # 如果默认值中没有该路径，则删除该设置
                self._delete_by_path(self.last_setting, path)
                self.__save()
                self.changeEvent(path)
        else:
            logging.info("开始重置程序设置！")
            changed_paths = self.__compare(self.DEFAULT_SETTING, self.last_setting)
            self.last_setting = deepcopy(self.DEFAULT_SETTING)
            self.__save()
            for path in changed_paths:
                self.changeEvent(path)
            logging.info("程序设置重置完成！")

    def add(self, path: str, default_data):
        """
        添加设置项
        @param path: 设置路径
        @param default_data: 默认数据
        """
        # 在默认设置中添加
        self._set_by_path(self.DEFAULT_SETTING, path, default_data)

        # 如果当前设置中没有该路径，则添加默认值
        if not self._path_exists(self.last_setting, path):
            self._set_by_path(self.last_setting, path, default_data)
            self.__save()

    def adds(self, defaults: dict):
        """
        批量添加设置项
        @param defaults: 字典，键为路径，值为默认数据
        """
        for path, default_data in defaults.items():
            self.add(path, default_data)

    def delete(self, path: str):
        """
        删除设置项
        @param path: 设置路径
        @return: 是否成功删除
        """
        success = self._delete_by_path(self.last_setting, path)
        if success:
            self.__save()
            self.changeEvent(path)
        return success

    def list_paths(self, base_path: str = ""):
        """
        列出指定路径下的所有设置路径
        @param base_path: 基础路径
        @return: 路径列表
        """
        data = self._get_by_path(self.last_setting, base_path) if base_path else self.last_setting
        if not isinstance(data, dict):
            return []

        paths = []
        self._collect_paths(data, base_path, paths)
        return paths

    def _collect_paths(self, data: dict, current_path: str, paths: list):
        """
        递归收集所有路径
        """
        for key, value in data.items():
            new_path = f"{current_path}/{key}" if current_path else key
            if isinstance(value, dict):
                self._collect_paths(value, new_path, paths)
            else:
                paths.append(new_path)

    def changeEvent(self, path: str):
        """
        修改设置项事件
        @param path: 设置路径
        """
        logging.info(f"设置项 {path} 发生更改，已同步！")
        try:
            self.changeSignal.emit(path)
        except Exception:
            logging.debug(f"emit changeSignal 失败：{traceback.format_exc()}")

    def connect(self, func):
        """
        连接信号，用于动态重载设置
        @param func: 函数名
        """
        self.changeSignal.connect(func)

    def disconnect(self, func):
        """
        取消连接信号，用于动态重载设置
        @param func: 函数名
        """
        self.changeSignal.disconnect(func)

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
                    changed_paths = self.__compare(self.current_setting, self.last_setting)
                    self.last_setting = self.current_setting
                    for path in changed_paths:
                        self.changeEvent(path)
            except:
                logging.error(f"设置文件数据数据错误，错误信息：{traceback.format_exc()}！")

    def __compare(self, old: dict, new: dict, current_path: str = ""):
        """
        递归比较两个 dict，返回发生变化的路径列表
        """
        changed_paths = []
        all_keys = set(old.keys()) | set(new.keys())

        for key in all_keys:
            path = f"{current_path}/{key}" if current_path else key

            if key in old and key in new:
                if isinstance(old[key], dict) and isinstance(new[key], dict):
                    # 递归比较子字典
                    changed_paths.extend(self.__compare(old[key], new[key], path))
                elif old[key] != new[key]:
                    # 值发生变化
                    changed_paths.append(path)
            elif key in old and key not in new:
                # 键被删除
                changed_paths.append(path)
            elif key not in old and key in new:
                # 新增键
                changed_paths.append(path)

        return changed_paths


setting = SettingFunctions()
