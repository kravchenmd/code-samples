from console_bot.src.models import ContactDetails, Note

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


def pagination(data):
    current_index = 1
    current_page = 1
    result = ''
    is_empty = False

    if isinstance(data[0], ContactDetails):
        repr_func = contact_repr
    elif isinstance(data[0], Note):
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


def contact_repr(c: ContactDetails) -> str:
    first_name = c.contact.first_name
    last_name = c.contact.last_name
    phones = ', '.join(c.phone_list)
    emails = ', '.join(c.email_list)
    birthday = c.birthday
    return f"\tName: {first_name} {last_name}\n\tPhones: {phones}" \
           f"\n\tEmails: {emails}\n\tBirthday: {birthday}\n\n"


def note_repr(el: Note) -> str:
    note_id = el.id
    creation_date = el.created
    tags = ' '.join([tag.tag for tag in el.tags])
    text = el.text
    return f"\tid: {note_id}\n\tcreated on: {creation_date}\n\ttags: {tags}\n\t{text}\n\n"
