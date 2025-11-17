import os
import shutil

BASE_DATA = "data"


def ensure_folder(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def save_repo_temp(repo_name: str):
    """
    Creates a folder under data/repos/<repo_name>.
    Returns the full path so agents can use it.
    """
    repo_path = os.path.join(BASE_DATA, "repos", repo_name)
    ensure_folder(repo_path)
    return repo_path


def save_extracted(repo_name: str, file_name: str, content: str):
    """
    Save extracted/cleaned code.
    """
    folder = os.path.join(BASE_DATA, "extracted", repo_name)
    ensure_folder(folder)

    full_path = os.path.join(folder, file_name)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return full_path


def delete_repo_temp(repo_name: str):
    """
    Cleanup temporary repo after analysis.
    Windows-safe version: forces deletion even for locked .git files.
    """
    import stat

    def remove_readonly(func, path, exc):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass  # last layer of safety

    repo_path = os.path.join(BASE_DATA, "repos", repo_name)

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
