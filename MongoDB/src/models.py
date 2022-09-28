from datetime import datetime

from mongoengine import *

from console_bot.modules.validation import is_valid_phone, is_valid_email, is_valid_date

connect(host='mongodb://localhost:27017/console_bot')


class Contact(Document):
    first_name = StringField(
        regex=r'(?:^[a-zA-Z]+$)', max_length=20, min_length=1, required=True, unique=True)
    last_name = StringField(
        regex=r'(?:^[a-zA-Z]+$)', max_length=20, min_length=1, required=True, unique_with='first_name')
    meta = {'collection': 'contacts'}


class ContactDetails(Document):
    contact = ReferenceField(Contact, reverse_delete_rule=CASCADE)
    phone_list = ListField(StringField(validation=is_valid_phone, required=True))
    email_list = ListField(EmailField(validation=is_valid_email, required=False))
    birthday = DateField(validation=is_valid_date, nullable=True, default=None)
    meta = {'collection': 'contact_details'}

    def days_to_birthday(self) -> int:
        if self.birthday is None:
            return -1

        now = datetime.now()
        birthday = datetime(now.year, self.birthday.month, self.birthday.day)
        if birthday < now:
            birthday = birthday.replace(year=now.year + 1)
        days = (birthday - now).days + 1
        return days


class Tag(Document):
    tag = StringField(max_length=20, unique=True)
    meta = {'collection': 'tags'}


class Note(Document):
    text = StringField(required=True)
    created = DateField(nullable=False, default=datetime.now().date())
    tags = ListField(ReferenceField(Tag))
    is_done = BooleanField(default=False)
    meta = {'collection': 'notes'}
