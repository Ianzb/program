from .info import *
from .data import *
from .file import *
from .web import *
from .system import *


class ZbToolLib(Data, File, Info, System, Web):
    pass


log.info("程序api初始化成功！")
