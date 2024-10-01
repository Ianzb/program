from .program import *
from .setting import *

handler2 = logging.FileHandler(program.LOGGING_FILE_PATH)
handler2.setLevel(logging.DEBUG)
handler2.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

logging.addHandler(handler2)
