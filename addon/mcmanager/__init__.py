import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.zbWidgetLib import *

try:
    from program.source.zbWidgetLib import *
except:
    pass


def init(p, l, s, window):
    global program, Log, setting
    program = p
    Log = l
    setting = s

from .mc_ui import *
