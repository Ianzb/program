import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.widget.custom import *

try:
    from program.source.widget.custom import *
except:
    pass
from .mc_ui import *
