import re
from random import randint
from faker import Faker

from src import db
from src.models import Contact, Phone, Email

fake = Faker()


def create_contacts():
    for i in range(10):
        contact_name = f"{fake.first_name()} {fake.last_name()}"
        contact = Contact(
            name=contact_name,
            birthday=fake.date_of_birth(),
            user_id=1
        )
        db.session.add(contact)

        contact_id = db.session.query(Contact).where(Contact.name == contact_name).first().id
        for _ in range(randint(1, 3)):
            phone = Phone(
                phone_number=re.sub(r"[^0-9()-]", "", fake.phone_number()),
                contact_id=contact_id
            )
            db.session.add(phone)
        for _ in range(randint(1, 3)):
            email = Email(
                email=fake.ascii_free_email(),
                contact_id=contact_id
            )
            db.session.add(email)
    db.session.commit()


if __name__ == '__main__':
    create_contacts()
