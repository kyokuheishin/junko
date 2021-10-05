from abc import ABCMeta, abstractclassmethod, abstractmethod
from util import singleton
import re


class NameSpaceState:
    __metaclass__ = ABCMeta

    def __init__(self, current_component_tag="40", current_module_id="0000", current_resource_name="startup.bml", current_uri=None, base_uri=None) -> None:
        self._current_component_tag: str = current_component_tag
        self._current_module_id: str = current_module_id
        self._current_resource_name: str = current_resource_name
        self._current_uri: str = current_uri
        self._base_uri: str = base_uri
        pass

    @abstractmethod
    def get_stream(self, path):
        pass

    @abstractmethod
    def launch_document(self, path):
        pass

    @abstractmethod
    def launch_document_restricted(self, path):
        pass

    @property
    def current_component_tag(self):
        return self._current_component_tag.lower() if self._current_component_tag else None

    @current_component_tag.setter
    def current_component_tag(self, val):
        self._current_component_tag = val

    @property
    def current_resource_name(self):
        return self._current_resource_name.lower() if self._current_resource_name else None

    @property
    def current_uri(self):
        return self._current_uri

    @property
    def base_uri(self):
        return self._base_uri

    def get_absolute_path(self, arg: str):
        if not arg or arg == "":
            return None

        path = arg.strip()
        path = re.sub(r'^~/', "/"+self._current_component_tag+"/", path)

        #case: "/<component>/<module>"
        m = re.match(r"^/([0-9A-Fa-f]{2})/([0-9A-Fa-f]{4})/?$", path)
        if m:
            self._current_component_tag = m.group(1)
            self._current_module_id = m.group(2)
            self._current_resource_name = None
            return f"/{self._current_component_tag}/{self._current_module_id}"

        #case: "/<component>/<module>/<resource>"
        m = re.match(r"^/([0-9A-Fa-f]{2})/([0-9A-Fa-f]{4})/(.+)$", path)
        if m:
            self._current_component_tag = m.group(1)
            self._current_module_id = m.group(2)
            self._current_resource_name = m.group(3)
            return f"/{self._current_component_tag}/{self._current_module_id}/{self._current_resource_name}"

        #case: "<module>"
        m = re.match(r"^([0-9A-Fa-f]{4})$", path)
        if m:
            self._current_module_id = m.group(1)
            self._current_resource_name = None
            return f"/{self._current_component_tag}/{self._current_module_id}"

        #case: "/<module>/<resource>"
        m = re.match(r"^/?([0-9A-Fa-f]{4})/(.+)$", path)
        if m:
            self._current_module_id = m.group(1)
            self._current_resource_name = m.group(2)
            return f"/{self._current_component_tag}/{self._current_module_id}/{self._current_resource_name}"

        #case: "<resource>"
        m = re.match(r"^([^/]+)$", path)
        if m:
            self._current_resource_name = m.group(1)
            return f"/{self._current_component_tag}/{self._current_module_id}/{self._current_resource_name}"

        #case: "aribdc"
        m = re.match(
            r"^arib-dc://-1.-1.-1/([0-9A-Fa-f]{2})/([0-9A-Fa-f]{4})/(.*)$", path)
        if m:
            self._current_component_tag = m.group(1)
            self._current_module_id = m.group(2)
            self._current_resource_name = m.group(3)
            return f"/{self._current_component_tag}/{self._current_module_id}/{self._current_resource_name}"
        return None

    def update_current_state(self, path: str):
        self.get_absolute_path(path)
        self._base_uri = None
        self._current_uri = None


@singleton
class ContextManager:
    pass
