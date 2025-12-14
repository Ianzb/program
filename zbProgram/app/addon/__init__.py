import logging
import subprocess
import traceback
import importlib
import time
from concurrent.futures import ThreadPoolExecutor

import functools
from qtpy import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qfluentwidgets import *
from qfluentwidgets.components.material import *
from qfluentwidgets import FluentIcon as FIF

import zbToolLib as zb
import zbWidgetLib as zbw
from zbWidgetLib import ZBF
from qtpy import *

import aenum

try:
    pyqtSignal = Signal
except NameError:
    Signal = pyqtSignal

sys.path.append(os.path.dirname(sys.argv[0]))


class AddonSettingProxy(QObject):
    """
    包装主程序的 setting 对象，对插件透明地在内部使用路径方式存取数据。
    支持的方法：get/read/set/save/add/adds/reset/connect/changeSignal
    """
    changeSignal = pyqtSignal(str)
    changeSignalWithoutAddonPath = pyqtSignal(str)

    def __init__(self, setting, addon_id: str = None):
        super().__init__()
        self.setting = setting
        self._addon_id = addon_id
        self.setting.connect(self.changeEvent)
        self.setting.connect(self.changeEvent2)

    def set_addon_id(self, addon_id):
        self._addon_id = addon_id

    def _get_full_path(self, name, use_addon_path=True):
        """
        获取完整路径
        @param name: 设置名称
        @param use_addon_path: 是否使用插件路径
        @return: 完整路径
        """
        if use_addon_path and self._addon_id:
            return f"addonSettings/{self._addon_id}/{name}"
        else:
            return name

    def get(self, name, use_addon_path=True):
        """
        读取设置
        @param name: 设置名称
        @param use_addon_path: 是否优先从插件路径查找，默认为True
        @return: 设置值
        """
        return self.read(name, use_addon_path)

    def read(self, name, use_addon_path=True):
        """
        读取设置
        @param name: 设置名称
        @param use_addon_path: 是否优先从插件路径查找，默认为True
        @return: 设置值
        """
        if use_addon_path and self._addon_id:
            # 优先从插件路径查找
            addon_path = f"addonSettings/{self._addon_id}/{name}"
            value = self.setting.read(addon_path)
            if value is not None:
                return value

        # 如果插件路径未找到或未使用插件路径，从根目录查找
        return self.setting.read(name)

    def save(self, name, data, use_addon_path=True):
        """
        保存设置
        @param name: 设置名称
        @param data: 设置值
        @param use_addon_path: 是否保存到插件路径，默认为True
        @return: None
        """
        if use_addon_path and self._addon_id:
            path = f"addonSettings/{self._addon_id}/{name}"
        else:
            path = name

        self.setting.save(path, data)

    def set(self, name, data, use_addon_path=True):
        """
        设置值（save的别名）
        @param name: 设置名称
        @param data: 设置值
        @param use_addon_path: 是否保存到插件路径，默认为True
        @return: None
        """
        return self.save(name, data, use_addon_path)

    def add(self, name, data, use_addon_path=True):
        """
        添加设置项
        @param name: 设置名称
        @param data: 默认值
        @param use_addon_path: 是否添加到插件路径，默认为True
        @return: None
        """
        if use_addon_path and self._addon_id:
            path = f"addonSettings/{self._addon_id}/{name}"
        else:
            path = name

        self.setting.add(path, data)

    def adds(self, data: dict, use_addon_path=True):
        """
        批量添加设置项
        @param data: 设置字典
        @param use_addon_path: 是否添加到插件路径，默认为True
        @return: None
        """
        for name, value in data.items():
            self.add(name, value, use_addon_path)

    def reset(self, name=None, use_addon_path=True):
        """
        重置设置
        @param name: 设置名称，为None时重置所有相关设置
        @param use_addon_path: 是否重置插件路径的设置，默认为True
        @return: None
        """
        if name is None:
            # 重置所有相关设置
            if use_addon_path and self._addon_id:
                # 重置插件命名空间下的所有设置
                base_path = f"addonSettings/{self._addon_id}"
                paths = self.setting.list_paths(base_path)
                for path in paths:
                    full_path = f"{base_path}/{path}" if base_path else path
                    self.setting.reset(full_path)
            else:
                # 重置全局设置（谨慎使用）
                self.setting.reset()
        else:
            # 重置特定设置
            if use_addon_path and self._addon_id:
                path = f"addonSettings/{self._addon_id}/{name}"
            else:
                path = name

            self.setting.reset(path)

    def delete(self, name, use_addon_path=True):
        """
        删除设置项
        @param name: 设置名称
        @param use_addon_path: 是否删除插件路径的设置，默认为True
        @return: 是否成功删除
        """
        if use_addon_path and self._addon_id:
            path = f"addonSettings/{self._addon_id}/{name}"
        else:
            path = name

        return self.setting.delete(path)

    def list_settings(self, use_addon_path=True):
        """
        列出所有相关设置
        @param use_addon_path: 是否列出插件路径的设置，默认为True
        @return: 设置路径列表
        """
        if use_addon_path and self._addon_id:
            base_path = f"addonSettings/{self._addon_id}"
            return self.setting.list_paths(base_path)
        else:
            # 列出所有全局设置（排除插件设置）
            all_paths = self.setting.list_paths()
            return [path for path in all_paths]

    def connect(self, func, use_addon_path=True):
        """
        连接信号，用于动态重载设置
        @param func: 函数名
        """
        if use_addon_path:
            self.changeSignal.connect(func)
        else:
            self.changeSignalWithoutAddonPath.connect(func)

    def disconnect(self, func):
        """
        取消连接信号，用于动态重载设置
        @param func: 函数名
        """
        try:
            self.changeSignal.disconnect(func)
        except:
            self.changeSignalWithoutAddonPath.disconnect(func)

    def changeEvent(self, key: str):
        if key.startswith(f"addonSettings/{self._addon_id}/"):
            key = key.replace(f"addonSettings/{self._addon_id}/", "", 1)
        self.changeSignal.emit(key)

    def changeEvent2(self, key: str):
        self.changeSignalWithoutAddonPath.emit(key)


class AddonBase:
    def __init__(self):
        self.program = None
        self.log = None
        self.setting = None
        self.addon_info = None
        self.window = None
        self.progress_center = None

    def set(self, program, setting, window, progress_center, addon_info):
        self.program = program
        self.window = window
        self.progress_center = progress_center
        self.addon_info = addon_info

        if addon_info.get("api_version", 0) <= 5:
            self.progressCenter = progress_center
            self.addonInfo = addon_info

        try:
            addon_id = addon_info.get("id")
            self.setting = AddonSettingProxy(setting, addon_id)
        except Exception:
            logging.error(f"创建 AddonSettingProxy 失败：{traceback.format_exc()}")
            self.setting = setting

    @property
    def addon_path(self):
        return zb.joinPath(self.program.ADDON_PATH, self.addon_info.get("id"))

    def getAddonPath(self):
        return self.addon_path

    def addonPath(self):
        return self.addon_path
