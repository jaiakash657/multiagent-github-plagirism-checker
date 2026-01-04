import os
from fingerprinting.parsing.language_detector import detect_language
from fingerprinting.parsing.treesitter_parser import TreeSitterParser

# Test code (Sample React/JSX code similar to a Netflix Clone)
test_code = """
import React from 'react';
function NetflixButton({ title }) {
    const handleClick = () => console.log("Clicked " + title);
    return <button onClick={handleClick}>{title}</button>;
}
"""

def debug_parse():
    print("--- Tree-sitter Debugger ---")
    
    # 1. Test Language Detection
    lang = detect_language("test.jsx")
    print(f"Detected Language for .jsx: {lang}")
    
    # 2. Test Parser
    print(f"Attempting to parse sample code...")
    tree = TreeSitterParser.parse_code(test_code, lang)
    
    if not tree or not tree.root_node:
        print("❌ FAILED: Parser returned None or empty tree.")
        return

    print(f"✅ SUCCESS: Root node type: {tree.root_node.type}")
    
    # 3. Check for ERROR nodes
    # If the grammar is wrong, Tree-sitter creates 'ERROR' nodes
    def has_errors(node):
        if node.type == "ERROR": return True
        for child in node.children:
            if has_errors(child): return True
        return False

    if has_errors(tree.root_node):
        print("⚠️  WARNING: Tree contains ERROR nodes. Grammar/Version mismatch.")
    else:
        print("💎 Tree is clean (No ERROR nodes).")

    # 4. Print S-Expression
    print("\nS-Expression (Structure):")
    print(str(tree.root_node)[:500] + "...")

if __name__ == "__main__":
    debug_parse()