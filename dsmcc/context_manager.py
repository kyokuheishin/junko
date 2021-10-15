from abc import ABC, ABCMeta, abstractclassmethod, abstractmethod
from typing import Match
from dsmcc.dsmcc_manager import NaiveDsmccManager
from util import arib_exceptions, singleton
import re


@singleton
class NameSpaceStateContextManager:

    dsmcc: NaiveDsmccManager

    def __init__(self) -> None:
        self._aribdc = AribdcState()
        self._unlink = UnlinkState()
        self._linked = LinkedState()
        self._current_state = self._aribdc
        pass

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, val):
        if self._current_state != val:
            print(
                f"Info name space stated has changed. Before {self._current_state.__class__} Now {val.__class__}")
        self._current_state = val

    @property
    def is_aribdc(self):
        return self._current_state == self._aribdc

    @is_aribdc.setter
    def is_aribdc(self, val):
        if val:
            self._current_state = self._aribdc
        return

    @property
    def is_linked(self):
        return self._current_state == self._linked

    @is_linked.setter
    def is_linked(self, val):
        if val:
            self._current_state = self._linked

    @property
    def is_unlink(self):
        return self._current_state == self._unlink

    @is_unlink.setter
    def is_unlink(self, val):
        if val:
            self._current_state = self._unlink

    @property
    def current_component_tag(self):
        return self._current_state._current_component_tag.lower() if self._current_state._current_component_tag else None

    @current_component_tag.setter
    def current_component_tag(self, val):
        self._current_state._current_component_tag = val

    @property
    def current_module_id(self):
        return self._current_state._current_module_id

    @current_module_id.setter
    def current_module_id(self, val):
        self._current_state._current_module_id = val

    @property
    def current_resource_name(self):
        return self._current_state._current_resource_name.lower() if self._current_state._current_resource_name else None

    @property
    def current_uri(self):
        return self._current_state._current_uri

    @property
    def base_uri(self):
        return self._current_state._base_uri

    @property
    def active_document_name(self):
        if self.is_aribdc:
            name = f"/{self.current_component_tag}/{self.current_module_id}"
            if self.current_resource_name != "" and self.current_resource_name:
                name += f"/{self.current_resource_name}"
                return name
            elif self.current_uri != "" and self.current_uri:
                # TODO: Implements the part of reading the name of active document from web
                return ""

    def get_stream(self, path: str):
        return

    def launch_document(self, path: str):
        try:
            stream = self.current_state.launch_document(path)
        except Exception as e:
            print(e.args)
        else:
            return stream

    def launch_document_restricted(self, path: str):
        try:
            stream = self.current_state.launch_document_restricted(path)
        except Exception as e:
            print(e.args)
        else:
            return stream

    def get_resource(self, decoder: function, path: str, arg):
        if not path or path == "" or path.strip() == "":
            return None

        stream = self.get_stream(path)

        if stream:
            result = decoder(stream, arg)

        return result

    def bitmap_resource_reader(self, stream, arg):
        # TODO: Implement the function of readign bitmap resource
        pass

    def get_resource_as_bitmap(self, path):
        return self.get_resource(self.bitmap_resource_reader, path, None)

    def get_absoulte_component_path(self, path: str):
        m: Match = re.match(r"([0-9A-Fa-f]{2})")
        if m:
            return f"/{m.group(0).lower()}"
        else:
            return f"/{self.current_component_tag}"

    def get_absolute_module_path(self, path: str):
        if not path or path == "":
            return None

        path = path.strip()
        path = re.sub(r'^~/', "/"+self._current_component_tag+"/", path)

        if "/" not in path:
            path = f"/{self._current_component_tag}/{path}"

        m = re.match(r"([0-9A-Fa-f]{2})/([0-9A-Fa-f]{4})$")
        if m:
            self._current_component_tag = m.group(1)
            self._current_module_id = m.group(2)
            return path

        return None

    def get_absolute_res_path(self, path: str):
        pass

    def update_current_state(self, path: str):
        self.get_absolute_path(path)
        self._base_uri = None
        self._current_uri = None

    def get_web_memory_stream(self, uri: str):
        pass

    def get_active_document_as_stream(self):
        if self.is_aribdc:
            return self.dsmcc.open_read(self._current_component_tag, self._current_module_id, self._current_resource_name)
        else:
            # TODO: Implements the part of reading contents from web
            pass


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

    def get_dsmcc_stream(self, path: str):
        if not self.dsmcc:
            raise arib_exceptions.NameSpaceDsmccNotFoundError(
                "Dsmcc not found.")

        if self.get_absolute_path(path):
            return self.dsmcc.open_read(self.current_component_tag, self.current_module_id, self.current_resource_name)
        else:
            return None

    def get_absolute_path(self, path: str):
        if not path or path == "":
            return None

        path = path.strip()
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


class AribdcState(NameSpaceState):
    def get_stream(self, path):
        return self.get_dsmcc_stream(path)

    def launch_document(self, path):
        super().launch_document(path)
        # TODO: Complete the part of launching document from web
        stream = self.get_dsmcc_stream(path)
        if stream:
            self.update_current_state(path)

        return stream

    def launch_document_restricted(self, path):
        super().launch_document_restricted(path)
        # TODO: Complete the part of launching document from web
        return None


class WebStateTemplate(NameSpaceState):
    def get_stream(self, path):
        return super().get_stream(path)


class UnlinkState(WebStateTemplate):
    def get_stream(self, path):
        return super().get_stream(path)


class LinkedState(WebStateTemplate):
    def get_stream(self, path):
        return super().get_stream(path)
