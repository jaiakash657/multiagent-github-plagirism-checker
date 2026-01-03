from fingerprinting.uast.uast_nodes import UASTNode, UASTNodeType


NODE_MAP = {
    # structure
    "class_definition": UASTNodeType.CLASS,
    "function_definition": UASTNodeType.FUNCTION,
    "method_definition": UASTNodeType.FUNCTION,

    # loops
    "for_statement": UASTNodeType.LOOP,
    "while_statement": UASTNodeType.LOOP,
    "do_statement": UASTNodeType.LOOP,

    # branches
    "if_statement": UASTNodeType.BRANCH,
    "switch_statement": UASTNodeType.MULTI_BRANCH,

    # calls
    "call_expression": UASTNodeType.CALL,
    "method_invocation": UASTNodeType.CALL,

    # assignments
    "assignment_expression": UASTNodeType.ASSIGN,

    # return
    "return_statement": UASTNodeType.RETURN,
}


class UASTBuilder:
    MAX_DEPTH = 20

    @staticmethod
    def build(tree):
        root = UASTNode(UASTNodeType.ENTRY)
        UASTBuilder._walk(tree.root_node, root, 0)
        return root

    @staticmethod
    def _walk(ast_node, parent: UASTNode, depth: int):
        if ast_node is None or depth > UASTBuilder.MAX_DEPTH:
            return

        node_type = NODE_MAP.get(ast_node.type)
        current_parent = parent

        if node_type:
            u_node = UASTNode(node_type)
            parent.add_child(u_node)
            current_parent = u_node

        for child in ast_node.children:
            UASTBuilder._walk(child, current_parent, depth + 1)
