import re
from mongoengine import ValidationError
from datetime import datetime


def is_valid_phone(phone: str) -> None:
    pattern = r'(?:\+\d{12,13}\b)|(?:\b(?<!\+)\d{10,11}\b)|(?:\b\d{2}(?!\W)\b)'
    if not re.match(pattern, phone):
        raise ValidationError("\nPhone must be a single numeric string\n" +
                              "\tExample: '+[12-13 digits]' or '[10-11 digits]' " +
                              "Or for DEBUG: just '[2 digits]")


def is_valid_email(email: str) -> None:
    pattern = r'\b[a-zA-Z]{1}[\w]+@[a-zA-Z]+\.[a-zA-Z]+'
    if not re.match(pattern, email):
        raise ValidationError("\nCheck please email format:\n" +
                              "\tExample: user01@domain.com\n")


def is_valid_date(date_str: str) -> None:
    try:
        datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        raise ValidationError("\nDate must be a single date string in format dd-mm-yyyy\n" +
                              "\tExample: '01-01-1970'\n")
