from .setting import *


class Manager(QObject):
    def __init__(self):
        super().__init__()

    @classmethod
    def register(cls, name, value):
        setattr(cls, name, value)


manager = Manager()
