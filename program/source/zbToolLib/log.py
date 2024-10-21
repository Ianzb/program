import logging
from sys import stderr
Log = logging.getLogger(__name__)
Log.setLevel(logging.DEBUG)

handler1 = logging.StreamHandler(stderr)
handler1.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

Log.addHandler(handler1)
