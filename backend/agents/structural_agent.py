# agents/structural_agent.py
import ast
import hashlib
import os
from typing import List, Dict

SUPPORTED_EXT = (".py", ".java", ".js")

class StructuralExtractor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def generic_visit(self, node):
        self.nodes.append(type(node).__name__)
        super().generic_visit(node)

def extract_structure(code: str) -> List[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    extractor = StructuralExtractor()
    extractor.visit(tree)
    return extractor.nodes

def structural_similarity(seq_a: List[str], seq_b: List[str]) -> float:
    if not seq_a or not seq_b:
        return 0.0

    set_a, set_b = set(seq_a), set(seq_b)
    return len(set_a & set_b) / len(set_a | set_b)


class StructuralAgent:
    """
    StructuralAgent:
    - AST-based structural similarity
    - Repo vs repo comparison
    """

    def _collect_nodes(self, repo_path: str) -> List[str]:
        nodes = []
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith(SUPPORTED_EXT):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                            code = fh.read()
                        nodes.extend(extract_structure(code))
                    except Exception:
                        continue
        return nodes

    def run(self, input_path: str, cand_path: str) -> dict:
        nodes_a = self._collect_nodes(input_path)
        nodes_b = self._collect_nodes(cand_path)

        score = structural_similarity(nodes_a, nodes_b)

        return {
            "agent": "structural",
            "score": score,
            "details": {
                "node_count_a": len(nodes_a),
                "node_count_b": len(nodes_b),
            },
        }
