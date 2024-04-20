import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.custom import *

try:
    from program.source.custom import *
except:
    pass
from .mc_ui import *
