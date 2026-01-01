from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class UASTNodeType(Enum):
    """
    Fixed universal node vocabulary.
    DO NOT add language-specific concepts here.
    """

    ENTRY = "ENTRY"          # function / main / method
    LOOP = "LOOP"            # for / while / do
    BRANCH = "BRANCH"        # if / else / switch
    CALL = "CALL"            # function or method call
    ASSIGN = "ASSIGN"        # variable assignment
    RETURN = "RETURN"        # return / yield / output
    EXPR = "EXPR"            # condition / expression
    BLOCK = "BLOCK"          # grouping (optional)


@dataclass
class UASTNode:
    """
    Universal AST Node.
    """

    node_type: UASTNodeType
    children: List["UASTNode"] = field(default_factory=list)

    # optional metadata (never language-specific)
    depth: int = 0

    def add_child(self, child: "UASTNode"):
        child.depth = self.depth + 1
        self.children.append(child)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def __repr__(self):
        return f"{self.node_type.value}(depth={self.depth}, children={len(self.children)})"
