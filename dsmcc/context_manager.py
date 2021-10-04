from abc import ABCMeta, abstractclassmethod
from util import singleton


class NameSpaceState:
    __metaclass__ = ABCMeta


@singleton
class ContextManager:
    pass
