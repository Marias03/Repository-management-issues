from src.closer import extract_issue_numbers


def test_extract_single_issue_number():
    assert extract_issue_numbers("fix login bug closes #5") == [5]


def test_extract_multiple_issue_numbers():
    message = "Update readme fixes #12 and resolves #3"
    assert extract_issue_numbers(message) == [12, 3]


def test_extract_no_issue_numbers():
    assert extract_issue_numbers("regular commit without issue reference") == []


def test_extract_case_insensitive():
    assert extract_issue_numbers("Closes #9") == [9]


def test_extract_multiple_keywords_in_one_message():
    message = "fixes #1 closes #2 resolves #3"
    assert extract_issue_numbers(message) == [1, 2, 3]


def test_extract_duplicate_mentions():
    message = "fixes #7 and fixes #7 again"
    assert extract_issue_numbers(message) == [7, 7]
