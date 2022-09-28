# for rising custom errors in 'add_contact' function
import os
import pickle
import re
from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, timedelta
from importlib.resources import files
from typing import Union, Dict


class FieldException(Exception):
    pass


class Field:
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = value


class Name(Field):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        if value.isalpha():
            Field.value.fset(self, value)
        else:
            raise ValueError("Name must be a single alphabetic string \n" +
                             "Example: 'Abc', 'abc'")

    def get_name(self) -> str:
        return self.value


class Phone(Field):
    def __init__(self, value: str = '') -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        pattern = r'(?:\+\d{12,13}\b)|(?:\b(?<!\+)\d{10,11}\b)|(?:\b\d{2}(?!\W)\b)'
        if re.match(pattern, value):
            Field.value.fset(self, value)
        else:
            raise ValueError("Phone must be a single numeric string\n" +
                             "Example: '+[12-13 digits]' or '[10-11 digits]'\n" +
                             "Or for DEBUG: just '[2 digits]")

    def get_phone(self) -> str:
        return self.value


class Birthday(Field):
    def __init__(self, value: str = '') -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        try:
            Field.value.fset(self, datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            raise ValueError("Birthday must be a single date string in format dd.mm.yyyy\n" +
                             "Example: '01.01.1970'")

    def birthday_date(self) -> str:
        date = self.value.strftime("%d.%m.%Y")
        return date

    def get_month(self) -> str:
        return self.value.month

    def get_day(self) -> str:
        return self.value.day


class Email(Field):
    def __init__(self, value: str = '') -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str) -> None:
        # verification parameters:
        # starts from letter, Latin letters and numbers, @, letters divided by 1 dot
        pattern = r'\b[a-zA-Z]{1}[\w]+@[a-zA-Z]+\.[a-zA-Z]+'
        if re.match(pattern, value):
            Field.value.fset(self, value)
        else:
            raise ValueError("Check please email format:\n" +
                             "Example: user01@domain.com")

    def get_email(self) -> str:
        return self.value


class Record:
    def __init__(self, name: Name) -> None:
        self.name: Name = name
        self.phone_list: list[Phone] = []
        self.email_list: list[Email] = []
        self.birthday: Union[Birthday, None] = None

    def __str__(self) -> str:
        # return f"{self.name.get_name() : <15}:\t{self.get_phones() : ^13}" \
        #        f"\t{self.get_emails() : ^12}\t{self.get_birthday() : >10}\n"
        return '{:<15}: '.format('Name') + f'\t{self.name.get_name()}\n' + \
               '{:>15}: '.format('phones') + f'\t{self.get_phones()}\n' + \
               '{:>15}: '.format('emails') + f'\t{self.get_emails()}\n' + \
               '{:>15}: '.format('birthday') + f'\t{self.get_birthday()}\n\n'

    def __contains__(self, item):  # to short this checking in code
        return item.get_phone() in [phone.get_phone() for phone in self.phone_list]

    def add_phone(self, phone: Phone) -> str:
        if phone in self:
            raise FieldException("This phone number is already in the list of the contact!")
        self.phone_list.append(phone)
        return "Contact has been updated successfully!"

    def get_phones(self) -> str:  # return phones in one string
        if not self.phone_list:
            return '-'
        return ', '.join([phone.get_phone() for phone in self.phone_list])

    def remove_phone(self, phone: Phone) -> str:
        if phone not in self:
            return "Phone can't be removed: it's not in the list of the contact!"
        for el in self.phone_list:
            if el.get_phone() == phone.get_phone():
                self.phone_list.remove(el)
        return "Phone has been removed successfully!"

    def change_phone(self, phone: Phone, new_phone: Phone) -> str:
        if phone not in self:
            return "Phone can't be changed: it's not in the list of the contact!"
        for el in self.phone_list:
            if el.get_phone() == phone.get_phone():
                self.phone_list.remove(el)
                self.phone_list.append(new_phone)
                return f"Phone number has been changed successfully!"

    def add_birthday(self, birthday: Birthday) -> None:
        if self.birthday is not None:
            raise FieldException("Birthday field of this contact is already filled!")
        self.birthday = birthday

    def get_birthday(self) -> str:
        if self.birthday is None:
            return '-'
        return self.birthday.birthday_date()

    def change_birthday(self, new_birthday: Birthday) -> str:
        if self.birthday is None:
            return "Birthday field of this contact is empty: fill it!"
        self.birthday = new_birthday
        return f"Birthday has been changed successfully!"

    def remove_birthday(self):
        if self.birthday is None:
            return "Birthday field of this contact is empty!"
        self.birthday = None
        return f"Birthday has been removed successfully!"

    def add_email(self, email: Email) -> str:
        if email.get_email() in [email.get_email() for email in self.email_list]:
            raise FieldException("This email is already in the list of the contact!")
        self.email_list.append(email)
        return "Contact was updated successfully!"

    def get_emails(self) -> str:  # return emails in one string
        if not self.email_list:
            return '-'
        return ', '.join([email.get_email() for email in self.email_list])

    def remove_email(self, email: Email) -> str:
        if email.get_email() not in [el.get_email() for el in self.email_list]:
            return "Email can't be removed: it's not in the list of the contact!"
        for el in self.email_list:
            if el.get_email() == email.get_email():
                self.email_list.remove(el)
        return "Email was removed successfully!"

    def edit_email(self, email: Email, new_email: Email) -> str:
        if email.get_email() not in [el.get_email() for el in self.email_list]:
            return "Email can't be changed: it's not in the list of the contact!"
        for el in self.email_list:
            if el.get_email() == email.get_email():
                self.email_list.remove(el)
                self.email_list.append(new_email)
                return f"Email number was changed successfully!"


class ContainerSerializer(ABC):
    @abstractmethod
    def save_to_file(self, filename: str) -> str:
        pass

    @abstractmethod
    def load_from_file(self, filename: str) -> str:
        pass


class AddressBook(UserDict):
    def __init__(self, pagination: int = 2) -> None:
        super(UserDict, self).__init__()
        self.pagination = pagination
        self.current_index = 0
        self.current_page = 0  # for showing page number in terminal
        self.data: Dict[str, Record] = {}  # for excluding PyCharm error in def load

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index >= len(self.data):
            self.current_index = 0
            self.current_page = 0
            raise StopIteration

        result = ''

        page_end = f"{'--end--' : ^33}"  # at the end of the data
        for i in range(self.current_index, self.current_index + self.pagination):
            if i >= len(self.data):
                break
            name = list(self.data.keys())[i]
            result += f"{self.data.get(name)}"  # __str__()
            self.current_index += 1
        else:
            if self.current_index < len(self.data):
                self.current_page += 1
                page_end = f"{'--' + str(self.current_page) + '--' : ^33}\n"  # at the end of each page

        result += page_end
        return result

    def add_record(self, name: str, record: Record) -> None:
        self.data[name] = record

    def remove_record(self, name: str) -> None:
        self.data.pop(name)

    def find(self, search_string: str) -> str:
        result = ''

        for record in self.data.values():
            if search_string.lower() in record.name.get_name().lower() or search_string in record.get_phones():
                result += f"{record}"
        return result[:-1]  # remove last '\n'

    def find_birthday(self, input_day):
        found = ''
        y = datetime.now()
        y = y.year
        current_date = datetime.now().date()
        input_day = int(input_day)
        b_day = timedelta(days=input_day) + current_date

        for record in self.data.values():
            i = record.get_birthday()
            m_b = datetime.strptime(i, '%d.%m.%Y').date()
            m_b = m_b.replace(year=y)
            if b_day == m_b:
                found += f'{record.name.get_name()}, '
        if len(found) > 1:
            return f'{found}has a birthday in this {input_day} days'
        else:
            return f'In {input_day} days there is no birthday'

    def find_contact(self, search_string: str) -> str:

        for record in self.data.values():

            if search_string.lower() == record.name.get_name().lower():
                return f'Search results for: "{search_string}" \n{record}'


class AddressBookSerializer(ContainerSerializer):
    save_path = 'database/contacts_db.bin'

    def __init__(self, container: AddressBook):
        self.container = container

    def save_to_file(self, filename: str = save_path) -> str:
        if filename != AddressBookSerializer.save_path:
            AddressBookSerializer.save_path = filename
        my_resources = files("console_bot")
        path = str(my_resources / filename)
        with open(path, 'wb') as file:
            pickle.dump(self.container.data, file)
        return f'Contacts have been saved in file {path} successfully!'

    def load_from_file(self, filename: str = save_path) -> str:
        my_resources = files('console_bot')
        path = str(my_resources / filename)
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                self.container.data = pickle.load(file)
            return f"\nContacts have been loaded from '{filename}' successfully!"
        return f"File '{filename}' does not exist!"
