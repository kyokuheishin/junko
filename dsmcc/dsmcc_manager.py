from abc import ABCMeta, abstractclassmethod


class NaiveDsmccManger:
    __metaclass__ = ABCMeta

    @abstractclassmethod
    def open_read(self) -> bytearray:
        pass

    @abstractclassmethod
    def get_module(self):
        pass
