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
