import logging as log_import
from sys import stderr
logging = log_import.getLogger(__name__)
logging.setLevel(log_import.DEBUG)

handler1 = log_import.StreamHandler(stderr)
handler1.setFormatter(log_import.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

logging.addHandler(handler1)
