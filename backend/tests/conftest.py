import pytest
import tempfile
import os
from storage.file_manager import ensure_folder

@pytest.fixture
def temp_repo():
    """
    Creates a temporary repo folder for testing.
    """
    with tempfile.TemporaryDirectory() as tmp:
        ensure_folder(tmp)
        yield tmp


@pytest.fixture
def sample_code_file(temp_repo):
    """
    Creates a sample code file inside test repo.
    """
    file_path = os.path.join(temp_repo, "main.py")
    with open(file_path, "w") as f:
        f.write("""
# This is a comment
def add(a, b):
    return a + b  # inline comment
""")
    return file_path
