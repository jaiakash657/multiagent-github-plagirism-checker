from enum import Enum
from dataclasses import dataclass, field
from typing import List


class UASTNodeType(Enum):
    """
    Fixed universal node vocabulary.
    Language-agnostic ONLY.
    """

    ENTRY = "ENTRY"

    # structural boundaries
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"

    # control flow
    LOOP = "LOOP"
    BRANCH = "BRANCH"
    MULTI_BRANCH = "MULTI_BRANCH"

    # operations
    CALL = "CALL"
    ASSIGN = "ASSIGN"
    RETURN = "RETURN"


JS_NODE_MAP = {
    # Functions
    "function_declaration": UASTNodeType.FUNCTION,
    "method_definition": UASTNodeType.FUNCTION,
    "arrow_function": UASTNodeType.FUNCTION,

    # Control flow
    "if_statement": UASTNodeType.BRANCH,
    "switch_statement": UASTNodeType.MULTI_BRANCH,
    "for_statement": UASTNodeType.LOOP,
    "while_statement": UASTNodeType.LOOP,

    # Calls / ops
    "call_expression": UASTNodeType.CALL,
    "assignment_expression": UASTNodeType.ASSIGN,
    "return_statement": UASTNodeType.RETURN,

    # JSX (VERY IMPORTANT)
    "jsx_element": UASTNodeType.CALL,   # component usage
    "jsx_self_closing_element": UASTNodeType.CALL,
}


@dataclass
class UASTNode:
    node_type: UASTNodeType
    children: List["UASTNode"] = field(default_factory=list)
    depth: int = 0

    def add_child(self, child: "UASTNode"):
        child.depth = self.depth + 1
        self.children.append(child)

    def is_leaf(self) -> bool:
        return not self.children

    def __repr__(self):
        return f"{self.node_type.value}(d={self.depth}, c={len(self.children)})"
