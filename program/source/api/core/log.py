import logging as __log
from sys import stderr
logging = __log.getLogger(__name__)
logging.setLevel(__log.DEBUG)

handler1 = __log.StreamHandler(stderr)
handler1.setFormatter(__log.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

logging.addHandler(handler1)
