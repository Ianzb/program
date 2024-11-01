from ..zbWidgetLib import *

sys.path.append(os.path.dirname(sys.argv[0]))

del log


class AddonBase:
    def __init__(self):
        self.program = None
        self.log = None
        self.setting = None

    def set(self, __program, __log, __setting, __window):
        self.program = __program
        self.log = __log
        self.setting = __setting
        self.window = __window
