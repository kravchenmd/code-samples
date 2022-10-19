import re
from datetime import datetime, date
from sqlalchemy import and_
from flask import request

from src import db
from src.models import Contact, Phone, Email

ROWS_PER_PAGE = 5


def get_contact_details(request_form) -> dict:
    fields = ['name', 'birthdate', 'phones', 'emails']
    values = [request_form.get(field).strip(' ,') for field in fields]
    contact_details = {k: v for k, v in zip(fields, values)}
    return contact_details


def split_str_to_list(s: str) -> list:
    return re.split(" |, |\r\n|\n", s)


def create_contact(request_form, user_id: int) -> None:
    contact_details = get_contact_details(request_form)

    new_contact = Contact()
    contact_name = contact_details.get('name').strip()
    print(contact_name)
    new_contact.name = contact_name
    new_contact.birthday = str_date_conv(contact_details.get('birthdate'))
    new_contact.user_id = user_id
    db.session.add(new_contact)

    contact_id = db.session.query(Contact).where(Contact.name == contact_name).first().id
    # print("contact_id", contact_id)
    phones = split_str_to_list(contact_details.get('phones'))
    for phone in phones:
        db.session.add(Phone(phone_number=phone, contact_id=contact_id))
    emails = split_str_to_list(contact_details.get('emails'))
    for email in emails:
        db.session.add(Email(email=email, contact_id=contact_id))

    db.session.commit()


def update_contact(request_form, user_id: int) -> Contact:
    contact = get_contact(user_id, request_form.get('contact_id'))
    new_details = get_contact_details(request_form)
    new_name = new_details.get('name')
    if contact.name != new_name:
        contact.name = new_name
    new_birthday = new_details.get('birthdate')
    if date_str_conv(contact.birthday) != new_birthday:
        contact.birthday = str_date_conv(new_birthday)

    new_phones = split_str_to_list(new_details.get('phones'))
    if new_phones:
        for phone in contact.phones:
            current_number = phone.phone_number
            if current_number not in new_phones:
                db.session.query(Phone).filter(Phone.id == phone.id).delete()
                continue
            new_phones.remove(current_number)
        for phone in new_phones:
            db.session.add(Phone(phone_number=phone, contact_id=contact.id))

    new_emails = split_str_to_list(new_details.get('emails'))
    if new_emails:
        for email in contact.emails:
            current_email = email.email
            if current_email not in new_emails:
                db.session.query(Email).filter(Email.id == email.id).delete()
                continue
            new_emails.remove(current_email)
        for email in new_emails:
            db.session.add(Email(email=email, contact_id=contact.id))
    db.session.commit()

    contact.birthday_str = date_str_conv(contact.birthday)
    contact.phone_list = ' '.join([str(phone.phone_number) for phone in contact.phones])
    contact.email_list = ' '.join([str(email.email) for email in contact.emails])
    return contact


def str_date_conv(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be a single date string in format dd-mm-yyyy\n" +
                         "Example: '1970-01-01'")


def date_str_conv(date_: date) -> str:
    return datetime.strftime(date_, '%Y-%m-%d')


def get_all_contacts(user_id: int) -> list[Contact]:
    # Set the pagination configuration
    page = request.args.get('page', 1, type=int)
    contacts = db.session.query(Contact).where(Contact.user_id == user_id).paginate(page=page, per_page=ROWS_PER_PAGE)
    contacts.pagination = ROWS_PER_PAGE
    return contacts


def get_contact(user_id: int, contact_id: int) -> Contact:
    contact = db.session.query(Contact).where(and_(Contact.id == contact_id, Contact.user_id == user_id)).first_or_404()
    contact.birthday_str = date_str_conv(contact.birthday)
    contact.phone_list = ', '.join([str(phone.phone_number) for phone in contact.phones])
    contact.email_list = ', '.join([str(email.email) for email in contact.emails])
    return contact


def delete_contact(user_id: int, contact_id: int) -> None:
    db.session.query(Contact).where(and_(Contact.id == contact_id, Contact.user_id == user_id)).delete()
    db.session.commit()
