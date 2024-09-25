import logging as __log
import sys

logging = __log.getLogger(__name__)
logging.setLevel(__log.DEBUG)

handler1 = __log.StreamHandler(sys.stderr)
handler1.setFormatter(__log.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)d]:%(message)s"))

logging.addHandler(handler1)
