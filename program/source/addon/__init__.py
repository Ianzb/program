import logging
import subprocess
import traceback
import importlib
import time
from concurrent.futures import ThreadPoolExecutor

import functools
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qtpy import *
from qfluentwidgets import *
from qfluentwidgets.components.material import *
from qfluentwidgets import FluentIcon as FIF

import zbToolLib as zb
import zbWidgetLib as zbw
from zbWidgetLib import ZBF
from qtpy import *

import aenum

sys.path.append(os.path.dirname(sys.argv[0]))


class AddonSettingProxy:
    """
    包装主程序的 setting 对象，对插件透明地在内部使用 addon_id 命名空间存取数据。
    支持的方法：get/read/set/save/add/adds/reset/signalConnect/changeSignal
    """

    def __init__(self, base_setting, addon_id=None):
        self._base = base_setting
        self._addon_id = addon_id
        if hasattr(base_setting, 'changeSignal'):
            self.changeSignal = getattr(base_setting, 'changeSignal')

    def set_addon_id(self, addon_id):
        self._addon_id = addon_id

    def get(self, name):
        return self.read(name)

    def read(self, name):
        try:
            if self._addon_id:
                return self._base.read(name, addon_id=self._addon_id)
        except TypeError:
            pass
        return self._base.read(name)

    def save(self, name, data):
        try:
            if self._addon_id:
                return self._base.save(name, data, addon_id=self._addon_id)
        except TypeError:
            pass
        return self._base.save(name, data)

    def set(self, name, data):
        return self.save(name, data)

    def add(self, name, data):
        try:
            if self._addon_id:
                return self._base.add(name, data, addon_id=self._addon_id)
        except TypeError:
            pass
        return self._base.add(name, data)

    def adds(self, data: dict):
        try:
            if self._addon_id:
                return self._base.adds(data, addon_id=self._addon_id)
        except TypeError:
            pass
        return self._base.adds(data)

    def reset(self, name=None):
        try:
            if self._addon_id:
                return self._base.reset(name, addon_id=self._addon_id)
        except TypeError:
            pass
        return self._base.reset(name)

    def signalConnect(self, func):
        try:
            if hasattr(self._base, 'signalConnect'):
                return self._base.signalConnect(func)
        except Exception:
            if hasattr(self, 'changeSignal'):
                try:
                    self.changeSignal.connect(func)
                except Exception:
                    logging.debug(f"AddonSettingProxy.bind signal failed: {traceback.format_exc()}")


class AddonBase:
    def __init__(self):
        self.program = None
        self.log = None
        self.setting = None
        self.addonInfo = None

    def set(self, __program, __setting, __window, __progress_center, __addon_info):
        self.program = __program
        try:
            addon_id = None
            if isinstance(__addon_info, dict):
                addon_id = __addon_info.get('id')
            proxy = AddonSettingProxy(__setting, addon_id=addon_id)
            self.setting = proxy
        except Exception:
            logging.debug(f"创建 AddonSettingProxy 失败：{traceback.format_exc()}")
            self.setting = __setting
        self.window = __window
        self.progressCenter = __progress_center
        self.addonInfo = __addon_info

    def getAddonPath(self):
        return zb.joinPath(self.program.ADDON_PATH, self.addonInfo.get("id"))

    def addIcon(self, name: str, path: str = ""):
        if not hasattr(ZBF, name):
            aenum.extend_enum(ZBF, name, zb.joinPath(self.getAddonPath(), path, name))

    def addIcons(self, path: str):
        for i in zb.walkFile(zb.joinPath(self.getAddonPath(), path), True):
            name = "_".join(zb.getFileName(i).split("_")[:-1])
            self.addIcon(name, path)
