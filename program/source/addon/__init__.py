from ..zbWidgetLib import *

sys.path.append(os.path.dirname(sys.argv[0]))


class AddonBase:
    def __init__(self):
        self.program = None
        self.log = None
        self.setting = None

    def set(self, __program, __setting, __window):
        self.program = __program
        self.setting = __setting
        self.window = __window
