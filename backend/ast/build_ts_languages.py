from tree_sitter import Language

Language.build_library(
    "build/ts-languages.dll",
    [
        "tree-sitter-python",
        "tree-sitter-java",
        "tree-sitter-javascript",
    ],
)

print("✅ Tree-sitter language library built successfully")
