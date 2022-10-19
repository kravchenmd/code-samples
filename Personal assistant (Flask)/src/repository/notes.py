from sqlalchemy import and_

from src import db
from src.models import Tag, Note
from src.libs.forms import TagForm, NoteForm


def create_tag(user_id: int, form: TagForm) -> None:
    new_tag = Tag()
    form.populate_obj(new_tag)
    new_tag.user_id = user_id
    db.session.add(new_tag)
    db.session.commit()


def get_tag_list(user_id: int) -> list[Tag]:
    tag_list = db.session.query(Tag).where(Tag.user_id == user_id).all()
    return tag_list


def get_all_notes(user_id: int) -> list[Tag]:
    return db.session.query(Note).where(Note.user_id == user_id).all()


def create_note(user_id: int, form: NoteForm, tag_list: list[str]) -> None:
    new_note = Note()
    form.populate_obj(new_note)
    new_note.user_id = user_id
    tags = db.session.query(Tag).filter(and_(Tag.name.in_(tag_list), Tag.user_id == user_id)).all()
    new_note.tags = tags
    db.session.add(new_note)
    db.session.commit()


def get_note(note_id: int, user_id: int) -> Note:
    note = db.session.query(Note).where(and_(Note.id == note_id, Note.user_id == user_id)).first_or_404()
    note.tag_list = ', '.join([str(tag.name) for tag in note.tags])
    return note


def set_done_note(note_id: int, user_id: int) -> None:
    db.session.query(Note).where(and_(Note.id == note_id, Note.user_id == user_id)).first_or_404().done = True
    db.session.commit()


def delete_note(note_id: int, user_id: int) -> None:
    db.session.query(Note).where(and_(Note.id == note_id, Note.user_id == user_id)).delete()
    db.session.commit()
