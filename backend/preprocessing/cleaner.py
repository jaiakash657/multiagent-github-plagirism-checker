import re

def clean_code(content: str) -> str:
    """
    Remove comments & extra whitespace from code.
    Works for Python, JS, C++, Java, HTML.
    """

    # Remove /* block comments */
    content = re.sub(r"/\\*.*?\\*/", "", content, flags=re.DOTALL)

    # Remove // single-line comments
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)

    # Remove # Python comments
    content = re.sub(r"#.*?$", "", content, flags=re.MULTILINE)

    # Remove HTML <!-- --> comments
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

    # Remove extra blank lines
    content = re.sub(r"\n\s*\n", "\n", content)

    return content.strip()
