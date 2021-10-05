from abc import ABCMeta, abstractclassmethod, abstractmethod
from pathlib import Path


class NaiveDsmccManager:
    __metaclass__ = ABCMeta

    @abstractmethod
    def open_read(self, component_tag, module_id, resorce_name) -> bytearray:
        pass

    @abstractmethod
    def get_module(self, component_tag, module_id):
        pass


class FileDsmccManager(NaiveDsmccManager):

    def __init__(self, path) -> None:
        super().__init__()
        if not Path(path).exists():
            raise FileNotFoundError(f'Root path {path} not found.')
        self.root_path = path

    def open_read(self, component_tag, module_id, resource_name) -> bytes:

        self.get_module(component_tag, module_id)
        resource_path = Path(
            f'{self.root_path}/{component_tag}/{module_id}/{resource_name}')

        if resource_path.exists():
            with resource_path.open('rb') as f:
                return f.read()
        else:
            raise FileNotFoundError(
                f'{component_tag}/{module_id}/{resource_name} not found.')

    def get_module(self, component_tag, module_id):

        if not Path(f'{self.root_path}/{component_tag}/{module_id}').exists():
            raise FileNotFoundError(f'{component_tag}/{module_id} not found.')
        return
