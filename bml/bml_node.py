class BmlNode:
    def create_all_bml_nodes(self, node, js_engine):
        js_engine.disable()
        self.create_bml_node(node)
        js_engine.enable()

    def create_bml_node(self, node):
        p_node = self.factory(node)

        if not p_node:
            return
