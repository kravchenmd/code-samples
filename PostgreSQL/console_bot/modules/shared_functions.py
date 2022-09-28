from datetime import datetime, date

from console_bot.notebook.notes_class import Notes
from console_bot.src.models import ContactDetails, Tag

PAGINATION = 3


def func_arg_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except TypeError:
            f_name = func.__name__
            if f_name in ('exit_program', 'hello', 'back'):
                return "ERROR: This command has to be written without arguments!"
            return "ERROR: Some unhandled error occurred!"

    return wrapper


@func_arg_error
def hello() -> str:
    return "\nHello! How can I help you?"


@func_arg_error
def back():
    return


@func_arg_error
def exit_program():
    return "Good bye!"


def date_conv(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError("Date must be a single date string in format dd-mm-yyyy\n" +
                         "Example: '01-01-1970'")


def pagination(data: list[ContactDetails | Notes]):
    current_index = 1
    current_page = 1
    result = ''
    is_empty = False

    if type(data[0]) == ContactDetails:
        repr_func = contact_repr
    elif type(data[0]) == Tag:
        repr_func = note_repr
    else:
        return "ERROR: unsupported type of elements to print!"

    for el in data:
        page_end = f"{'--' + str(current_page) + '--' : ^33}\n"  # at the end of each page
        result += repr_func(el)

        if current_index + (current_page - 1) * PAGINATION >= len(data):
            is_empty = True
            page_end = f"{'--end--' : ^33}"  # at the end of the data
        current_index += 1
        if current_index > PAGINATION or is_empty:
            result += page_end
            yield result
            current_page += 1
            current_index = 1
            result = ''


def contact_repr(el) -> str:
    birthday_str = el.birthday.strftime("%d-%m-%Y")
    return f"\tName: {el.contact.name}\n\tPhones: {', '.join(el.phone_list)}" \
           f"\n\tEmails: {', '.join(el.email_list)}\n\tBirthday: {birthday_str}\n\n"


def note_repr(el) -> str:
    creation_date = el.note.creation_date.strftime("%d-%m-%Y")
    return f"\tid: {el.note_id}\n\tcreated on: {creation_date}\n\ttags: {el.tags}\n\t{el.note.text}\n\n"
