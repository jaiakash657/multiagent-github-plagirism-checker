import os

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".java", ".cpp", ".ts", ".tsx",
    ".html", ".css", ".json", ".md", ".c", ".h"
}

EXCLUDED_FOLDERS = {
    "node_modules", "__pycache__", ".git", "dist", "build"
}

def list_valid_files(repo_path: str):
    """
    Walk through repository and return only allowed code files.
    """
    valid_files = []

    for root, dirs, files in os.walk(repo_path):
        # Remove excluded folders from traversal
        dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                valid_files.append(os.path.join(root, file))

    return valid_files
