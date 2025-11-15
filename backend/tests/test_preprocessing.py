from preprocessing.cleaner import strip_comments_and_blank

def test_cleaner_basic():
    text = "# comment\n\nprint('hi')\n'''multi\nline'''\n"
    cleaned = strip_comments_and_blank(text)
    assert "print" in cleaned
    assert "comment" not in cleaned
