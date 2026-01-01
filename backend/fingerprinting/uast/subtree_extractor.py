from typing import List
from fingerprinting.uast.uast_nodes import UASTNode


class SubtreeExtractor:
    @staticmethod
    def extract(root: UASTNode) -> List[str]:
        subtrees = []
        SubtreeExtractor._dfs(root, subtrees)
        return subtrees

    @staticmethod
    def _dfs(node: UASTNode, acc: List[str]):
        signature = SubtreeExtractor._serialize(node)
        acc.append(signature)

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
