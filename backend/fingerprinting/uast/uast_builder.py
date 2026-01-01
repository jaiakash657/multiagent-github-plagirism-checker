from fingerprinting.uast.uast_nodes import UASTNode, UASTNodeType


NODE_MAP = {
    # loops
    "for_statement": UASTNodeType.LOOP,
    "while_statement": UASTNodeType.LOOP,
    "do_statement": UASTNodeType.LOOP,

    # branches
    "if_statement": UASTNodeType.BRANCH,
    "switch_statement": UASTNodeType.BRANCH,

    # calls
    "call_expression": UASTNodeType.CALL,
    "method_invocation": UASTNodeType.CALL,

    # assignments
    "assignment_expression": UASTNodeType.ASSIGN,

    # return
    "return_statement": UASTNodeType.RETURN,
}


class UASTBuilder:
    @staticmethod
    def build(tree):
        root = UASTNode(UASTNodeType.ENTRY)
        UASTBuilder._walk(tree.root_node, root)
        return root

    @staticmethod
    def _walk(ast_node, parent: UASTNode):
        if ast_node is None:
            return

        node_type = NODE_MAP.get(ast_node.type)

        if node_type:
            u_node = UASTNode(node_type)
            parent.add_child(u_node)
            parent = u_node

        for child in ast_node.children:
            UASTBuilder._walk(child, parent)
