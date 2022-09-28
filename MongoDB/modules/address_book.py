from datetime import datetime, timedelta
from mongoengine import ValidationError

from console_bot.modules.shared_functions import pagination
from console_bot.modules.validation import is_valid_phone, is_valid_email, is_valid_date
from console_bot.src.models import Contact, ContactDetails


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
                return "ERROR: This command needs 3 arguments: `first_name`, `last_name` and 'new_birthday'" \
                       "separated by 1 space!"
            if f_name in ('remove_email',):
                return "ERROR: This command needs 3 arguments: `first_name`, `last_name` and 'email'" \
                       "separated by 1 space!"
            if f_name in ('remove_phone',):
                return "ERROR: This command needs 3 arguments: `first_name`, `last_name` and 'phone'" \
                       "separated by 1 space!"
            if f_name in ('change_phone',):
                return "ERROR: This command needs 4 arguments: `first_name`, `last_name`, " \
                       "'old_phone' and 'new_phone' separated by 1 space!"
            if f_name in ('edit_email',):
                return "ERROR: This command needs 4 arguments: `first_name`, `last_name`, " \
                       "'old_email' and 'new_email' separated by 1 space!"
            if f_name in ('add_contact',):
                return "ERROR: This command needs 5 arguments: `first_name`, `last_name`, `phone`, " \
                       "`email` and `birthday` separated by 1 space!"

            return "ERROR: Some unhandled error occurred!"

    return wrapper


@func_arg_error
def add_contact(first_name: str, last_name: str, phone: str, email: str, birthday: str) -> str:
    if '' in [first_name, last_name]:
        return "You need to create contact with first and last names!"
    if Contact.objects(first_name=first_name, last_name=last_name):
        return "The contact with this name is already created"

    try:
        contact = Contact(
            first_name=first_name,
            last_name=last_name
        )
        contact.validate()
    except ValidationError:
        return "Name of contact must contain only letters (a-z and A-Z)!"
    else:
        contact.save()

    try:
        contact_details = ContactDetails(
            contact=contact,
            phone_list=[phone],
            email_list=[email] if email else None,
            birthday=birthday,
        )
        contact_details.validate()
    except (ValueError, ValidationError) as e:
        contact.delete()  # delete the created contact if its details are not valid
        return str(e)
    else:
        contact_details.save()

    return f"Contact has been created successfully!"


@func_arg_error
def show_contacts() -> str:
    data = ContactDetails.objects()
    if not len(data):
        return "There are no contacts to show yet..."

    # contact_details_lookup = {
    #     "$lookup": {
    #         "from": "contact_details",
    #         "localField": "_id",
    #         "foreignField": "contact",
    #         "as": "contact_details",
    #     }
    # }
    # pipeline = [contact_details_lookup]
    # data = list(Contact.objects().aggregate(*pipeline))

    result = "\nList of all contacts:\n"
    for page in pagination(data):
        result += page
    return result


@func_arg_error
def show_phones(first_name: str, last_name: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    result = f"\nPhones of contact {first_name} {last_name}:\n\t"
    result += ", ".join(contact_details.phone_list)
    return result


@func_arg_error
def show_emails(first_name: str, last_name: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    result = f"\nEmails of contact {first_name} {last_name}:\n\t"
    result += ", ".join(contact_details.email_list)
    return result


@func_arg_error
def show_birthday(first_name: str, last_name: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    return f"\nBirthday of contact {first_name} {last_name}: {contact_details.birthday}"


@func_arg_error
def remove_contact(first_name: str, last_name: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact.delete()
    return f"\nContact {first_name} {last_name} has been removed successfully!"


@func_arg_error
def remove_phone(first_name: str, last_name: str, phone: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    phone_list = contact_details.phone_list
    if phone not in phone_list:
        return "Phone can't be removed: it's not in the list of the contact!"
    else:
        phone_list.remove(phone)
        contact_details.update(phone_list=phone_list)
        return f"\nPhone {phone} has been removed successfully!"


@func_arg_error
def remove_email(first_name: str, last_name: str, email: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    email_list = contact_details.email_list
    if email not in email_list:
        return "Email can't be removed: it's not in the list of the contact!"
    else:
        email_list.remove(email)
        contact_details.update(phone_list=email_list)
        return f"\nEmail {email} has been removed successfully!"


@func_arg_error
def remove_birthday(first_name: str, last_name: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    contact_details.update(birthday=None)
    return f"\nBirthday has been removed successfully from contact {first_name} {last_name}!"


@func_arg_error
def change_phone(first_name: str, last_name: str, old_phone: str, new_phone: str) -> str:
    try:
        is_valid_phone(old_phone)
        is_valid_phone(new_phone)
    except ValidationError as err:
        return str(err)
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    phone_list = contact_details.phone_list
    if not phone_list:
        return f"\nContact {first_name} {last_name} has no phones"
    phone_list.remove(old_phone)
    phone_list.append(new_phone)
    contact_details.update(phone_list=phone_list)
    return f"\nPhone was successfully changed!"


@func_arg_error
def change_email(first_name: str, last_name: str, old_email: str, new_email: str) -> str:
    try:
        is_valid_email(old_email)
        is_valid_email(new_email)
    except ValidationError as err:
        return str(err)
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    email_list = contact_details.email_list
    if not email_list:
        return f"\nContact {first_name} {last_name} has no emails"
    email_list.remove(old_email)
    email_list.append(new_email)
    contact_details.update(email_list=email_list)
    return f"\nEmail was successfully changed!"


@func_arg_error
def change_birthday(first_name: str, last_name: str, new_birthday: str) -> str:
    try:
        is_valid_date(new_birthday)
    except ValidationError as err:
        return str(err)
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    contact_details.update(birthday=datetime.strptime(new_birthday, "%d-%m-%Y").date())
    return f"\nEmail was successfully changed!"


@func_arg_error
def days_to_birthday(first_name: str, last_name: str) -> str:
    contact = Contact.objects(first_name=first_name, last_name=last_name).first()
    if not contact:
        return "There is no contact with this name!"
    contact_details = ContactDetails.objects(contact=contact).first()
    if contact_details.birthday is None:
        return f"Contact {first_name} {last_name} has no birthday"
    return f"\n{contact_details.days_to_birthday()} day(s) to birthday of {first_name} {last_name}"


@func_arg_error
def birthday_in(input_day: str) -> str:
    result = []
    current_date = datetime.now().date()
    input_day = int(input_day)
    b_day = timedelta(days=input_day) + current_date

    contact_details = ContactDetails.objects()
    for el in contact_details:
        if (el.birthday.day, el.birthday.month) == (b_day.day, b_day.month):
            contact = el.contact
            result.append(f"{contact.first_name} {contact.last_name}")
    if not result:
        return f"There is no contacts with birthday in {input_day} day(s)"
    return ", ".join(result)


@func_arg_error
def find(search_string: str) -> str:
    """ Find (sub-)string `search_string` in name of contacts """
    result = []
    contacts = Contact.objects()
    for contact in contacts:
        name = f"{contact.first_name} {contact.last_name}"
        if search_string.lower() in name.lower():
            result.append(name)
    if not result:
        return f"There is no contacts with `{search_string}` in name"
    return f"\nFind for `{search_string}`:\n\t" + "\n\t".join(result)


if __name__ == '__main__':
    # print(add_contact('QP', 'M', '12', 'mk@gm.com', '02-02-1970'))
    print(show_contacts())
