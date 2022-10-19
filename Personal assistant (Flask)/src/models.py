import re
from datetime import datetime

from sqlalchemy.orm import validates

from src import db
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    token_cookie = db.Column(db.String(255), nullable=True, default=None)
    notes = db.relationship('Note', back_populates='user')
    contacts = db.relationship('Contact', back_populates='user')

    @validates('username')
    def validate_user_name(self, _, username):
        pattern = r'\b[a-zA-z].+'
        if not re.match(pattern, username):
            raise AssertionError('Username must start with a letter!')
        if len(username) < 5 or len(username) > 120:
            raise AssertionError('Username must be between 5 and 20 characters')
        return username

    def __repr__(self):
        return f"User({self.id}, {self.username})"


note_m2m_tag = db.Table(
    'note_m2m_tag',
    db.Model.metadata,
    db.Column("id", db.Integer, primary_key=True),
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id', ondelete="CASCADE")),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"))
)


class Tag(db.Model):
    __tablename__ = 'tags'
    __table_args__ = (db.UniqueConstraint('name', 'user_id'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Tag({self.name}, {self.user_id})"


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    done = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', cascade='all, delete', back_populates='notes')
    tags = db.relationship('Tag', secondary=note_m2m_tag, backref='notes', passive_deletes='all')

    def __str__(self):
        return f"{self.name}:{self.user_id}"


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birthday = db.Column(db.Date, nullable=True)
    phones = db.relationship('Phone', back_populates='contact')
    emails = db.relationship('Email', back_populates='contact')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', cascade='all, delete', back_populates='contacts')

    @validates('name')
    def validate_name(self, _, name):
        pattern = r'[^a-zA-Z ]'
        if re.findall(pattern, name):
            raise AssertionError('Name of a contact must contain only letters!')
        return name

    @hybrid_property
    def days_to_birthday(self) -> int:
        if self.birthday is None:
            return -1

        now = datetime.now()
        birthday = datetime(now.year, self.birthday.month, self.birthday.day)
        if birthday < now:
            birthday = birthday.replace(year=now.year + 1)
        days = (birthday - now).days + 1
        return days


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = db.relationship('Contact', cascade='all, delete', back_populates='phones')

    @validates('phone_number')
    def validate_name(self, _, phone_number):
        if re.findall(r"\b\+", phone_number) or re.findall(r"[^\d+\-() ]", phone_number):
            raise AssertionError("Phone number can start with `+` and must contain only digits and signs `-() `")
        if not(8 < len(re.findall(r'\d', phone_number)) < 15):
            raise AssertionError("Total number of digits in phone number should be between 8 and 15")
        return phone_number


class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = db.relationship('Contact', cascade='all, delete', back_populates='emails')

    @validates('email')
    def validate_name(self, _, email):
        pattern = r'\b[a-zA-Z]{1}[\w]+@[a-zA-Z]+\.[a-zA-Z]+'
        if not re.match(pattern, email):
            raise AssertionError('Email must be in format: example@domain.com')
        return email
