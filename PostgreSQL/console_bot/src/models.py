from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from datetime import datetime

from console_bot.src.db import engine

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class ContactDetails(Base):
    __tablename__ = 'contact_details'
    id = Column(Integer, primary_key=True)
    phone_list = Column(JSON, nullable=True)
    email_list = Column(JSON, nullable=True)
    birthday = Column(Date, nullable=True)
    contact_id = Column('student_id', ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = relationship(Contact, backref=backref('children', passive_deletes=True))

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


class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    creation_date = Column(Date)
    is_done = Column(Boolean, default=False)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    tags = Column(JSON, nullable=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    note = relationship(Note, backref=backref('children', passive_deletes=True))





Base.metadata.create_all(engine)
Base.metadata.bind = engine
