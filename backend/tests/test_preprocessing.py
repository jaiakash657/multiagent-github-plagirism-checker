# from preprocessing.cleaner import clean_code
# from preprocessing.extractor import extract_clean_chunks
# from preprocessing.file_selector import list_valid_files

# def test_clean_code():
#     raw = """
# # comment
# x = 10   # inline
# """
#     cleaned = clean_code(raw)
#     assert "#" not in cleaned
#     assert "x = 10" in cleaned


# def test_extract_clean_chunks(sample_code_file):
#     chunks = extract_clean_chunks(sample_code_file)
#     assert len(chunks) > 0
#     assert "def add" in chunks[0]


# def test_file_selector(temp_repo, sample_code_file):
#     files = list_valid_files(temp_repo)
#     assert sample_code_file in files
