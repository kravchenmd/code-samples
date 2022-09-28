import random
from random import randint
from faker import Faker
from console_bot.src.db import session
from models import Contact, ContactDetails

fake = Faker()


def create_contacts():
    for _ in range(10):
        contact = Contact(
            name=f"{fake.first_name()} {fake.last_name()}"
        )
        session.add(contact)
    session.commit()


def create_contact_details():
    contacts = session.query(Contact).all()

    for contact in contacts:
        ci = ContactDetails(
            phone_list=[fake.phone_number() for _ in range(randint(1, 3))],
            email_list=[fake.ascii_free_email() for _ in range(randint(1, 3))],
            birthday=fake.date_of_birth(),
            contact_id=contact.id
        )
        session.add(ci)
    session.commit()


if __name__ == '__main__':
    create_contacts()
    create_contact_details()
