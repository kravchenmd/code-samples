from faker import Faker
import random
from models import Contact, ContactDetails

fake = Faker()


# Validation needs to be turned off
def seed():
    for count in range(10):
        contact = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name()
        ).save()

        contact_details = ContactDetails(
            contact=contact,
            phone_list=[fake.phone_number() for _ in range(random.randint(1, 3))],
            email_list=[fake.ascii_free_email() for _ in range(random.randint(1, 3))],
            birthday=fake.date_of_birth(),
        ).save()


if __name__ == '__main__':
    # Validation needs to be turned off
    seed()
