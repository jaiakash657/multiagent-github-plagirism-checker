from preprocessing.cleaner import clean_code

def read_file(filepath: str) -> str:
    """
    Read file safely with UTF-8, ignoring decode errors.
    """
    try:
        return open(filepath, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""


def chunk_text(text: str, max_lines: int = 200):
    """
    Split content into chunks for embedding (because large files must be chunked).
    """
    lines = text.split("\n")
    chunks = []

    for i in range(0, len(lines), max_lines):
        chunk = "\n".join(lines[i: i + max_lines]).strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def extract_clean_chunks(filepath: str):
    """
    Read → clean → chunk code file.
    Returns: list of cleaned chunks.
    """
    raw = read_file(filepath)
    cleaned = clean_code(raw)
    chunks = chunk_text(cleaned)

    return chunks
