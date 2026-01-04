from typing import Dict, Optional, List
import os
import logging
from collections import defaultdict

# Importing the logic we fixed earlier
from fingerprinting.parsing.language_detector import detect_language
from fingerprinting.parsing.treesitter_parser import TreeSitterParser

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx",
    ".py", ".java", ".cpp", ".c", ".h",
}

EXCLUDED_FOLDERS = {
    "node_modules", "__pycache__", ".git",
    "dist", "build", ".next", "coverage"
}

class StructuralAgent:
    """
    StructuralAgent (Direct Tree-sitter AST)
    - Parses code into Tree-sitter Trees.
    - Groups trees by language.
    - Compares structural similarity using Tree-sitter node properties.
    """

    def _build_repo_trees(self, repo_path: str) -> Dict[str, List]:
        """Traverses repo and builds a map of {lang: [root_nodes]}"""
        tree_map = defaultdict(list)
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue
                
                file_path = os.path.join(root, file)
                lang = detect_language(file_path)
                if not lang:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        code = f.read()
                    
                    if len(code.strip()) < 20:
                        continue

                    tree = TreeSitterParser.parse_code(code, lang)
                    if tree and tree.root_node:
                        tree_map[lang].append(tree.root_node)
                except Exception as e:
                    logger.debug(f"[STRUCT] Skip {file_path}: {e}")
        return tree_map

    def _compare_trees(self, node1, node2) -> float:
        """Robust structural comparison using Iterative Traversal."""
        def get_safe_structural_list(root_node):
            nodes = []
            stack = [root_node]
            while stack:
                curr = stack.pop()
                if curr.is_named:
                    nodes.append(curr.type)
                for i in range(curr.child_count - 1, -1, -1):
                    stack.append(curr.child(i))
            return nodes

        try:
            list1 = get_safe_structural_list(node1)
            list2 = get_safe_structural_list(node2)

            if not list1 or not list2:
                return 0.0

            set1 = set(f"{list1[i]}->{list1[i+1]}" for i in range(len(list1)-1))
            set2 = set(f"{list2[i]}->{list2[i+1]}" for i in range(len(list2)-1))

            if not set1 or not set2:
                set1, set2 = set(list1), set(list2)

            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            return float(intersection) / union if union > 0 else 0.0
        except Exception as e:
            logger.error(f"Structural comparison failed: {e}")
            return 0.0

    def run(self, input_repo_path: str, cand_repo_path: str, simhash_score: Optional[float] = None) -> Dict:
        """Orchestrator Entry Point"""
        # 1. Fast Path for nearly identical files
        if simhash_score is not None and simhash_score >= 0.98:
            return {"agent": "structural", "score": 1.0, "details": {"status": "skipped_high_sim"}}

        # 2. Build Tree Maps
        input_map = self._build_repo_trees(input_repo_path)
        cand_map = self._build_repo_trees(cand_repo_path)

        # 3. Compare within same languages
        scores = [0.0]
        for lang, in_trees in input_map.items():
            if lang in cand_map:
                for t1 in in_trees:
                    for t2 in cand_map[lang]:
                        scores.append(self._compare_trees(t1, t2))

        final_score = max(scores)
        return {
            "agent": "structural",
            "score": round(float(final_score), 4),
            "details": {
                "input_files": sum(len(v) for v in input_map.values()),
                "cand_files": sum(len(v) for v in cand_map.values()),
                "comparisons": len(scores) - 1
            }
        }