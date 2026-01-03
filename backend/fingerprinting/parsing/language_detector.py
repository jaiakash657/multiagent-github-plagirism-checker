import os

# Tree-sitter language keys used by your parser
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
}

def detect_language(file_path: str):
    """
    Detect programming language from file extension.

    Returns:
        str | None
        e.g. 'python', 'java', 'javascript', 'cpp'
    """
    _, ext = os.path.splitext(file_path.lower())
    return EXTENSION_LANGUAGE_MAP.get(ext)
