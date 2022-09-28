from datetime import datetime

from console_bot.modules.shared_functions import date_conv

from console_bot.modules.shared_functions import pagination
from console_bot.src.db import session
from console_bot.src.models import Note, Tag
from sqlalchemy.exc import NoResultFound
from sqlalchemy import and_, not_


def func_arg_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except TypeError:
            f_name = func.__name__
            if f_name in ('show_all', 'show_done_notes'):
                return "ERROR: This command has to be written without arguments!"
            if f_name in ('add_note',):
                return "ERROR: This command has to be written without arguments!\n"\
                       "Arguments will be asked in the next steps."
            if f_name in ('add_note', 'delete_note', 'mark_as_done', 'unmark_as_done'):
                return "ERROR: This command needs 1 obligatory arguments: 'note_id' separated by 1 space!"
            if f_name in ('find_by_tag',):
                return "ERROR: This command needs 1 obligatory argument 'tag'!"
            if f_name in ('find_by_text',):
                return "ERROR: This command needs 1 obligatory argument 'search_string'!"
            if f_name in ('edit_text',):
                return "ERROR: This command needs 2 arguments: `note_id` and `new_text` separated by 1 space!"
            if f_name in ('edit_creation_date', 'add_tags'):
                return "ERROR: This command needs 2 arguments: 'note_id' and" \
                       f"'{'date' if f_name == 'edit_creation_date' else 'tag'} separated by 1 space!"
            return "Some unhandled error occurred!"

    return wrapper


@func_arg_error
def add_note() -> str:
    text = input("Input the text of the note to be created: ")
    if not text:
        return "\nNote must contain some text!"
    tags = input("Input tags for the note, separated by spaces: ").split()
    creation_date = datetime.now().date()

    note = Note(text=text, creation_date=creation_date)
    session.add(note)
    session.commit()

    if tags:
        tag = Tag(note_id=note.id, tags=tags)
        session.add(tag)
        session.commit()
    return "\nNote has bees added successfully!"


@func_arg_error
def delete_note(note_id: str) -> str:
    try:
        note_id = int(note_id)
    except ValueError:
        return "ERROR: id of a note must be an integer!"
    try:
        note = session.query(Note).filter(Note.id == note_id).one()
    except NoResultFound:
        return "\nThere is no note with this id!"
    session.query(Note).filter(Note.id == note_id).delete()
    session.commit()
    return f"\nNote with id {note.id} has been successfully deleted"


@func_arg_error
def edit_text(note_id: str, *new_text: str) -> str:
    try:
        note_id = int(note_id)
    except ValueError:
        return "ERROR: id of a note must be an integer!"
    try:
        note = session.query(Note).filter(Note.id == note_id).one()
    except NoResultFound:
        return "\nThere is no note with this id!"

    note.text = ' '.join(new_text)
    session.commit()
    return f"\nText of note with id {note.id} has been changed"


@func_arg_error
def edit_creation_date(note_id: str, new_date: str) -> str:
    try:
        note_id = int(note_id)
    except ValueError:
        return "ERROR: id of a note must be an integer!"
    try:
        note = session.query(Note).filter(Note.id == note_id).one()
    except NoResultFound:
        return "\nThere is no note with this id!"

    new_date = date_conv(new_date)
    note.creation = new_date
    session.commit()
    return f"\nDate of creation of the note with id {note.id} has been added"


@func_arg_error
def add_tags(note_id: str, *tags) -> str:
    try:
        note_id = int(note_id)
    except ValueError:
        return "ERROR: id of a note must be an integer!"
    try:
        note = session.query(Note).filter(Note.id == note_id).one()
    except NoResultFound:
        return "\nThere is no note with this id!"
    if not tags:
        return "You must enter some tags to add!"
    tags = [el for el in tags]

    current_tag = session.query(Tag).filter(Tag.note_id == note_id).one()
    current_tags_list = current_tag.tags

    is_new_tags = set(tags) - set(current_tags_list)
    if not is_new_tags:
        return f"\nThere is no new tags to add to note with id {note.id}"
    updated_tags_list = list(set(tags) | set(current_tags_list))
    current_tag.tags = updated_tags_list
    session.add(current_tag)
    session.commit()
    return f"\nFollowing tags have been added to note with id {note.id}:\n" \
           f"\t{' '.join(is_new_tags)}"


@func_arg_error
def show_all() -> str:
    notes = session.query(Tag).join(Note).filter(Note.id == Tag.note_id).filter(
        not_(Note.is_done)).order_by(Note.id).all()
    # notes = session.query(Note).filter(not_(Note.is_done)).order_by(Note.id).all()
    if not notes:
        return "\nThere are no notes to show yet..."
    result = "\nList of all notes:\n"
    for page in pagination(notes):
        result += page
    return result


@func_arg_error
def show_done_notes():
    """ Show notes with status `done` """
    notes = session.query(Tag).join(Note).filter(Note.is_done).order_by(Note.id).all()
    if not notes:
        return "\nThere are no done notes"
    result = "\nList of all done notes:\n"
    for page in pagination(notes):
        result += page
    return result


@func_arg_error
def find_by_text(search_string: str) -> str:
    """ Find (sub-)string `search_string` in the text of the note """
    notes = session.query(Tag).join(Note).filter(
        and_(not_(Note.is_done), Note.text.ilike(f'%{search_string}%'))).order_by(Note.id).all()
    if not notes:
        return f"\nNo notes found containing text `{search_string}`"
    result = f"\nNotes with `{search_string}` in text:\n"
    for page in pagination(notes):
        result += page
    return result


@func_arg_error
def find_by_tag(search_string: str) -> str:
    """ Find (sub-)string `search_string` in the text of the tags """
    notes = []
    for instance in session.query(Tag).join(Note).filter(not_(Note.is_done)).order_by(Note.id).all():
        if search_string in instance.tags:
            notes.append(instance)
    if not notes:
        return f"\nNo notes found containing tag `{search_string}`"
    result = f"\nNotes with tag `{search_string}`:\n"
    for page in pagination(notes):
        result += page
    return result


@func_arg_error
def mark_as_done(note_id: str) -> str:
    try:
        note_id = int(note_id)
    except ValueError:
        return "ERROR: id of a note must be an integer!"
    try:
        note = session.query(Note).filter(Note.id == note_id).one()
    except NoResultFound:
        return "\nThere is no note with this id!"
    note.is_done = True
    session.commit()
    return f"\nNote with id {note.id} has been marked as `done`"


@func_arg_error
def unmark_as_done(note_id: str) -> str:
    try:
        note_id = int(note_id)
    except ValueError:
        return "ERROR: id of a note must be an integer!"
    try:
        note = session.query(Note).filter(Note.id == note_id).one()
    except NoResultFound:
        return "\nThere is no note with this id!"
    note.is_done = False
    session.commit()
    return f"\nNote with id {note.id} has been marked as `not done`"


if __name__ == '__main__':
    # print(add_tags(1, 'tag 3', 'tag4'))
    print(show_all())
