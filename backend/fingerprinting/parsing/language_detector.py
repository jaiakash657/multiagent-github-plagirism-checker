import os

# Map extensions to specific Tree-sitter grammar keys
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".js": "javascript",
    ".jsx": "javascript",   # tree-sitter-javascript handles JSX
    ".ts": "typescript",   # REQUIRES tree-sitter-typescript
    ".tsx": "tsx",          # REQUIRES tree-sitter-typescript (tsx parser)
}

def detect_language(file_path: str):
    if not file_path:
        return None
    _, ext = os.path.splitext(file_path.lower())
    return EXTENSION_LANGUAGE_MAP.get(ext)