from data_processing.validation import validate_isbn


def test_valid_isbn():
    result = validate_isbn('9780306406157')
    # TODO: assert result equals '9780306406157'

def test_invalid_isbn():
    result = validate_isbn('not-an-isbn')
    # TODO: assert result is None

def test_wrong_length():
    result = validate_isbn('123456789')
    # TODO: assert result is None