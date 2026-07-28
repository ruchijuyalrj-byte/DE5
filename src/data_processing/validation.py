"""
Data validation functions.
"""


# Example function to implement:
def validate_isbn(isbn):
    """Clean and validate an ISBN-13 value.

    Args:
        isbn: Raw ISBN value (may be a hyphenated string, a number, or None)

    Returns:
        The cleaned ISBN-13 string if valid, or None if invalid.

    TODO: Implement check-digit validation and formatting cleanup.
    """

    isbn_new = str(isbn)

    if len(isbn_new) != 13:
        return (None)

    return isbn

    """one = 1
    three = 3
    check1 = 1
    check3 = 1
    sum = 0

    for i in isbn:
        check1 = i * one
        check3 = i * three
        sum = check1 + check3

    check_digit = (10 - (sum % 10)) % 10"""
        

