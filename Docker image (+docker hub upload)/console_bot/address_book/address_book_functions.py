from datetime import datetime

from .address_book_class import AddressBook, Phone, Birthday, Name, Email, Record, \
    FieldException, AddressBookSerializer


# This decorator handles the correct number of arguments that are passed into the function
def func_arg_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except TypeError:
            f_name = func.__name__
            if f_name in ('exit_program', 'hello', 'show_all_phones'):
                return "ERROR: This command has to be written without arguments!"
            if f_name in ('show_phone', 'days_to_birthday', 'find_contacts', 'remove_contact',
                          'show_email', 'remove_birthday'):
                return "ERROR: This command needs 1 arguments: " \
                       f"'{'search_word' if f_name == 'find_contacts' else 'name'}' separated by 1 space! "
            if f_name in ('birthday_in',):
                return "ERROR: This command needs 1 obligatory argument 'days_to_birthday'!"
            if f_name in ('add_contact',):
                return "ERROR: This command needs 1 obligatory argument 'name' and 3 supplementary " \
                       "'phone', 'email' and 'birthday' separated by 1 space!"
            if f_name in ('change_birthday',):
                return "ERROR: This command needs 2 arguments: 'name' and 'birthday' separated by 1 space!"
            if f_name in ('remove_email',):
                return "ERROR: This command needs 2 arguments: 'name' and 'email' separated by 1 space!"
            if f_name in ('remove_phone',):
                return "ERROR: This command needs 2 arguments: 'name' and 'phone' separated by 1 space!"
            if f_name in ('change_phone',):
                return "ERROR: This command needs 3 arguments: 'name', 'phone' and 'new_phone' separated by 1 space!"
            if f_name in ('edit_email',):
                return "ERROR: This command needs 3 arguments: 'name', 'email' and 'new_email' separated by 1 space!"
            return "Some unhandled error occurred!"

    return wrapper


@func_arg_error
def hello() -> str:
    return "Hello! How can I help you?"


@func_arg_error
def add_contact(contacts: AddressBook, name: str, phone: str = '', email: str = '', birthday: str = '') -> str:
    try:
        n = Name(name)
        p = Phone(phone) if phone else None
        e = Email(email) if email else None
        b = Birthday(birthday) if birthday else None
    except ValueError as err:
        return f"ERROR: {err}"

    if name in contacts.data.keys():
        if not phone and not birthday and not email:
            return "ERROR: The contact with this name is already created! Try to update it!"
        if phone:
            try:
                contacts.data[name].add_phone(p)
            except FieldException as msg:
                return str(msg)
        if birthday:
            try:
                contacts.data[name].add_birthday(b)
            except FieldException as msg:
                return str(msg)
        if email:
            try:
                contacts.data[name].add_email(e)
            except FieldException as msg:
                return str(msg)
        return "Contact has been updated successfully!"
    else:
        contact_record = Record(n)
        if phone:
            contact_record.add_phone(p)
        if birthday:
            contact_record.add_birthday(b)
        if email:
            contact_record.add_email(e)
        contacts.add_record(name, contact_record)
        return f"Contact has been created successfully!"


@func_arg_error
def remove_contact(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return "ERROR: There is no contact with this name!"

    contacts.remove_record(name)
    return f"Contact {name} has been removed successfully!"


@func_arg_error
def change_phone(contacts: AddressBook, name: str, phone: str, new_phone: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        p = Phone(phone)
        new_p = Phone(new_phone)
    except ValueError as err:
        return f"ERROR: {err}"

    result = contacts.data.get(name).change_phone(p, new_p)
    return result


@func_arg_error
def edit_email(contacts: AddressBook, name: str, email: str, new_email: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        old_e = Email(email)
        new_e = Email(new_email)
    except ValueError as err:
        return f"ERROR: {err}"

    result = contacts.data.get(name).edit_email(old_e, new_e)
    return result


@func_arg_error
def change_birthday(contacts: AddressBook, name: str, new_birthday: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        b = Birthday(new_birthday)
    except ValueError as err:
        return f"ERROR: {err}"

    result = contacts.data.get(name).change_birthday(b)
    return result


@func_arg_error
def remove_phone(contacts: AddressBook, name: str, phone: str) -> str:
    """
    Remove phone number from the contact. But doesn't remove contact itself if it has no phone numbers.
    """
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        p = Phone(phone)
    except ValueError as err:
        return f"ERROR: {err}"
    result = contacts.data.get(name).remove_phone(p)
    return result


@func_arg_error
def show_phone(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    return contacts.get(name).get_phones()


@func_arg_error
def remove_email(contacts: AddressBook, name: str, email: str) -> str:
    """
    Remove email from the contact. But doesn't remove contact itself if it has no email.
    """
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    try:
        e = Email(email)
    except ValueError as err:
        return f"ERROR: {err}"
    result = contacts.data.get(name).remove_email(e)
    return result


@func_arg_error
def show_email(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    return contacts.get(name).get_emails()


@func_arg_error
def show_all_phones(contacts: AddressBook) -> str:
    if not contacts.data:
        return "There are no contacts to show yet..."
    result = ''
    for page in contacts:
        result += page
    return result


@func_arg_error
def days_to_birthday(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    if contacts[name].birthday is None:
        return "This contact has no birthday field!"
    now = datetime.now()
    birthday = datetime(now.year, contacts[name].birthday.get_month(), contacts[name].birthday.get_day())
    if birthday < now:
        birthday = birthday.replace(year=now.year + 1)
    days = (birthday - now).days + 1
    return f"{days} day(s) to {contacts[name].name.get_name()}'s birthday!"


@func_arg_error
def birthday_in(contacts: AddressBook, input_day) -> str:
    result = contacts.find_birthday(input_day)
    return result


@func_arg_error
def remove_birthday(contacts: AddressBook, name: str) -> str:
    if name not in contacts.data.keys():
        return f"There is no contact with name '{name}'"

    result = contacts.data.get(name).remove_birthday()
    return result


@func_arg_error
def back():
    return


@func_arg_error
def exit_program():
    return "Good bye!"


@func_arg_error
def save_contacts(contacts: AddressBook, filename: str = AddressBookSerializer.save_path) -> str:
    result = AddressBookSerializer(contacts).save_to_file(filename)
    return result


@func_arg_error
def load_contacts(contacts: AddressBook, filename: str = AddressBookSerializer.save_path) -> str:
    data, result = AddressBookSerializer(contacts).load_from_file(filename)
    if not (data is None):
        contacts.data = data
    return result


@func_arg_error
def find_contacts(contacts: AddressBook, search_string: str) -> str:
    result = contacts.find(search_string)
    return result


@func_arg_error
def find_contact(contacts: AddressBook, search_string: str) -> str:
    result = contacts.find_contact(search_string)
    return result
