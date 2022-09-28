import re
from datetime import datetime, timedelta

from console_bot.modules.shared_functions import date_conv, pagination
from console_bot.src.db import session
from console_bot.src.models import Contact, ContactDetails
from sqlalchemy.exc import NoResultFound
from sqlalchemy import and_


# This decorator handles the correct number of arguments that are passed into the function
def func_arg_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except TypeError:
            f_name = func.__name__
            if f_name in ('exit_program', 'hello', 'show_contacts'):
                return "ERROR: This command has to be written without arguments!"
            if f_name in ('show_phones', 'days_to_birthday', 'find', 'remove_contact',
                          'show_emails', 'remove_birthday', 'show_birthday'):
                return "ERROR: This command needs 1 arguments: " \
                       f"'{'search_word' if f_name == 'find' else 'name'}' separated by 1 space! "
            if f_name in ('birthday_in',):
                return "ERROR: This command needs 1 obligatory argument 'input_day'!"
            if f_name in ('change_birthday',):
                return "ERROR: This command needs 2 arguments: 'name' and 'new_birthday' separated by 1 space!"
            if f_name in ('remove_email',):
                return "ERROR: This command needs 2 arguments: 'name' and 'email' separated by 1 space!"
            if f_name in ('remove_phone',):
                return "ERROR: This command needs 2 arguments: 'name' and 'phone' separated by 1 space!"
            if f_name in ('change_phone',):
                return "ERROR: This command needs 3 arguments: 'name', 'old_phone' and 'new_phone' " \
                       "separated by 1 space!"
            if f_name in ('edit_email',):
                return "ERROR: This command needs 3 arguments: 'name', 'old_email' and 'new_email' " \
                       "separated by 1 space!"
            if f_name in ('add_contact',):
                return "ERROR: This command needs 4 arguments: `name`, `phone`, `email` and `birthday` " \
                       "separated by 1 space!"

            return "ERROR: Some unhandled error occurred!"

    return wrapper


def is_valid_phone(phone: str) -> None:
    pattern = r'(?:\+\d{12,13}\b)|(?:\b(?<!\+)\d{10,11}\b)|(?:\b\d{2}(?!\W)\b)'
    if not re.match(pattern, phone):
        raise ValueError("Phone must be a single numeric string\n" +
                         "Example: '+[12-13 digits]' or '[10-11 digits]'\n" +
                         "Or for DEBUG: just '[2 digits]")


def is_valid_email(email: str) -> None:
    pattern = r'\b[a-zA-Z]{1}[\w]+@[a-zA-Z]+\.[a-zA-Z]+'
    if not re.match(pattern, email):
        raise ValueError("Check please email format:\n" +
                         "Example: user01@domain.com")


@func_arg_error
def add_contact(contact_name: str, phone: str, email: str, birthday: str) -> str:
    if contact_name != '':
        try:
            session.query(Contact).filter(Contact.name == contact_name).one()
            if not phone and not birthday and not email:
                return "The contact with this name is already created"
        except NoResultFound:
            try:
                is_valid_phone(phone)
                is_valid_email(email)
                birthday_conv = date_conv(birthday)
            except ValueError as err:
                return str(err)
            new_contact = Contact(name=contact_name)
            session.add(new_contact)
            session.commit()  # TODO: Check this

            contact = session.query(Contact).filter(Contact.name == contact_name).one()
            contact_details = ContactDetails(phone_list=phone, email_list=email,
                                             birthday=birthday_conv, contact_id=contact.id)
            session.add(contact_details)
            session.commit()

            return f"Contact has been created successfully!"


@func_arg_error
def show_contacts() -> str:
    contacts = session.query(ContactDetails).join(Contact).filter(
        Contact.id == ContactDetails.contact_id).order_by(Contact.name).all()
    if not contacts:
        return "There are no contacts to show yet..."
    result = "\nList of all contacts:\n"
    for page in pagination(contacts):
        result += page
    return result


@func_arg_error
def show_phones(contact_name: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    result = f"\nPhones of contact {contact_name}:\n"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    result += ", ".join(contact_details.phone_list)
    return result


@func_arg_error
def show_emails(contact_name: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    result = f"\nEmails of contact {contact_name}:\n"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    result += ", ".join(contact_details.email_list)
    return result


@func_arg_error
def show_birthday(contact_name: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    return f"\nBirthday of contact {contact_name}: {contact_details.birthday}"


@func_arg_error
def remove_contact(contact_name: str) -> str:
    try:
        session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    session.query(Contact).filter(Contact.name == contact_name).delete()
    session.commit()
    return f"\nContact {contact_name} has been removed successfully!"


@func_arg_error
def remove_phone(contact_name: str, phone: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    phone_list = contact_details.phone_list[:]
    if phone not in phone_list:
        return "Phone can't be removed: it's not in the list of the contact!"
    else:
        phone_list.remove(phone)
        contact_details.phone_list = phone_list
        session.commit()
        return f"\nPhone {phone} has been removed successfully!"


@func_arg_error
def remove_email(contact_name: str, email: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    email_list = contact_details.email_list[:]
    if email not in email_list:
        return "Phone can't be removed: it's not in the list of the contact!"
    else:
        email_list.remove(email)
        contact_details.phone_list = email_list
        session.commit()
        return f"\nPhone {email} has been removed successfully!"


@func_arg_error
def remove_birthday(contact_name: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    contact_details.birthday = None
    return f"\nBirthday has been removed successfully from contact {contact_name}!"


@func_arg_error
def change_phone(contact_name: str, old_phone: str, new_phone: str) -> str:
    try:
        is_valid_phone(old_phone)
        is_valid_phone(new_phone)
    except ValueError as err:
        return str(err)
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(and_(ContactDetails.phone_list == old_phone,
                                                                ContactDetails.contact_id == contact.id)).one()
    contact_details.phone_list = new_phone
    session.commit()
    return f"\nPhone was successfully changed!"


@func_arg_error
def change_email(contact_name: str, old_email: str, new_email: str) -> str:
    try:
        is_valid_email(old_email)
        is_valid_email(new_email)
    except ValueError as err:
        return str(err)
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(and_(ContactDetails.email_list == old_email,
                                                                ContactDetails.contact_id == contact.id)).one()
    contact_details.email_list = new_email
    session.commit()
    return f"\nEmail was successfully changed!"


@func_arg_error
def change_birthday(contact_name: str, new_birthday: str) -> str:
    try:
        birthday_conv = date_conv(new_birthday)
    except ValueError as err:
        return str(err)
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    contact_details.birthday = birthday_conv
    session.commit()

    return f"\nBirthday has been updated successfully!"


@func_arg_error
def days_to_birthday(contact_name: str) -> str:
    try:
        contact = session.query(Contact).filter(Contact.name == contact_name).one()
    except NoResultFound:
        return "There is no contact with this name!"
    contact_details = session.query(ContactDetails).filter(ContactDetails.contact_id == contact.id).one()
    if contact_details.birthday is None:
        return f"Contact {contact_name} has no birthday"
    return f"\n{contact_details.days_to_birthday} day(s) to birthday of {contact_name}"


@func_arg_error
def birthday_in(input_day: str) -> str:
    result = []
    current_date = datetime.now().date()
    input_day = int(input_day)
    b_day = timedelta(days=input_day) + current_date

    contact_details = session.query(ContactDetails).all()
    for el in contact_details:
        if (el.birthday.day, el.birthday.month) == (b_day.day, b_day.month):
            contact = session.query(Contact).filter(el.contact_id == Contact.id).one()
            result.append(contact.name)
    if not result:
        return f"There is no contacts with birthday in {input_day} day(s)"
    return ", ".join(result)


@func_arg_error
def find(search_string: str) -> str:
    """ Find (sub-)string `search_string` in name of contacts """
    result = []
    contacts = session.query(Contact).all()
    for contact in contacts:
        if search_string.lower() in contact.name.lower():
            result.append(contact.name)
    if not result:
        return f"There is no contacts with `{search_string}` in name"
    return f"\nFind for `{search_string}`:\n\t" + "\n\t".join(result)


if __name__ == '__main__':
    # print(add_contact('AD', '66', 'om@gm.com', '02-05-2000'))
    # print(show_contacts())
    # for c in pagination(contacts):
    #     print(c)
    print(find('a'))
