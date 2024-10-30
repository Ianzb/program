import logging
from sys import stderr

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

handler1 = logging.StreamHandler(stderr)
handler1.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

log.addHandler(handler1)
