from fingerprinting.uast.uast_nodes import UASTNode, UASTNodeType

# ------------------------------------------------------
# Tree-sitter → UAST normalization map
# Supports backend + frontend (JS / JSX / TS)
# ------------------------------------------------------
NODE_MAP = {
    # ==================================================
    # Python / Java / C-like languages
    # ==================================================
    "class_definition": UASTNodeType.CLASS,
    "function_definition": UASTNodeType.FUNCTION,
    "method_definition": UASTNodeType.FUNCTION,

    # ==================================================
    # JavaScript / TypeScript functions
    # ==================================================
    "function_declaration": UASTNodeType.FUNCTION,
    "arrow_function": UASTNodeType.FUNCTION,

    # ==================================================
    # Control flow
    # ==================================================
    "for_statement": UASTNodeType.LOOP,
    "while_statement": UASTNodeType.LOOP,
    "do_statement": UASTNodeType.LOOP,
    "for_in_statement": UASTNodeType.LOOP,
    "for_of_statement": UASTNodeType.LOOP,

    "if_statement": UASTNodeType.BRANCH,
    "switch_statement": UASTNodeType.MULTI_BRANCH,
    "conditional_expression": UASTNodeType.BRANCH,

    # ==================================================
    # Calls / operations
    # ==================================================
    "call_expression": UASTNodeType.CALL,
    "method_invocation": UASTNodeType.CALL,

    # JSX → treat component usage as CALL
    "jsx_element": UASTNodeType.CALL,
    "jsx_self_closing_element": UASTNodeType.CALL,

    # ==================================================
    # Assignments & returns
    # ==================================================
    "assignment_expression": UASTNodeType.ASSIGN,
    "return_statement": UASTNodeType.RETURN,
}


class UASTBuilder:
    """
    Builds a Universal AST (UAST) from Tree-sitter AST.

    - Language-agnostic
    - Depth-limited
    - Safe for large frontend repos
    """

    MAX_DEPTH = 20

    @staticmethod
    def build(tree):
        """
        Entry point to build UAST from tree-sitter AST.
        """
        root = UASTNode(UASTNodeType.ENTRY)
        if not tree or not tree.root_node:
            return root

        UASTBuilder._walk(tree.root_node, root, 0)
        return root

    @staticmethod
    def _walk(ast_node, parent: UASTNode, depth: int):
        """
        Recursive DFS traversal of tree-sitter AST,
        mapping known node types into UAST nodes.
        """

        if ast_node is None or depth > UASTBuilder.MAX_DEPTH:
            return

        node_type = NODE_MAP.get(ast_node.type)
        current_parent = parent

        # If this AST node maps to a UAST node, create it
        if node_type:
            u_node = UASTNode(node_type)
            parent.add_child(u_node)
            current_parent = u_node

        # Continue traversal
        for child in ast_node.children:
            UASTBuilder._walk(child, current_parent, depth + 1)
