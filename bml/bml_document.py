import lxml


class BmlDocument:
    bml_source: str = None
    depth: int = 0
    element_count: int = 0
    attribute_count: int = 0
    script_element_line_number: int = 0
    script_element_found: bool = False
    encoding: str = ""
    major_version: int = 0
    minor_version: int = 0

    def load(self, stream):
        return
