from typing import List
from fingerprinting.uast.uast_nodes import UASTNode

class SubtreeExtractor:
    @staticmethod
    def extract(root: UASTNode) -> List[str]:
        acc = []
        SubtreeExtractor._dfs(root, acc)
        return acc

    @staticmethod
    def _dfs(node: UASTNode, acc: List[str]):
        acc.append(SubtreeExtractor._serialize(node))
        for child in node.children:
            SubtreeExtractor._dfs(child, acc)

    @staticmethod
    def _serialize(node: UASTNode) -> str:
        if not node.children:
            return node.node_type.value

        return (
            node.node_type.value
            + "("
            + ",".join(SubtreeExtractor._serialize(c) for c in node.children)
            + ")"
        )
