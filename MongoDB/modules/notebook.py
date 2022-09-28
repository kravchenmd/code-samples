from datetime import datetime

from mongoengine import ValidationError

from console_bot.modules.shared_functions import pagination
from console_bot.modules.validation import is_valid_date
from console_bot.src.models import Note, Tag


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
            if f_name in ('edit_creation_date',):
                return "ERROR: This command needs 2 arguments: 'note_id' and 'new_creation_date' separated by 1 space!"
            if f_name in ('add_tags',):
                return "ERROR: This command needs 2 types of arguments: 'note_id' and " \
                       f"one or several 'tag', each separated by spaces!"
            return "Some unhandled error occurred!"

    return wrapper


@func_arg_error
def add_note() -> str:
    text = input("Input the text of the note to be created: ")
    if not text:
        return "\nNote must contain some text!"
    tags = input("Input tags for the note, separated by spaces: ").split()
    if tags:
        tag_list = []
        for el in tags:
            tag = Tag.objects(tag=el).first()
            if not tag:
                tag = Tag(tag=el).save()
            tag_list.append(tag)
    Note(text=text, tags=tag_list).save()
    return "\nNote has bees added successfully!"


@func_arg_error
def delete_note(note_id: str) -> str:
    if not note_id:
        return "You must enter id of a note to edit!"
    note = Note.objects(id=note_id).first()
    if not note:
        return "There is no note with this id!"
    note.delete()
    return f"\nNote with id '{note.id}' has been successfully deleted"


@func_arg_error
def edit_text(note_id: str, *new_text: str) -> str:
    if not note_id:
        return "You must enter id of a note to edit!"
    note = Note.objects(id=note_id).first()
    if not note:
        return "There is no note with this id!"

    note.update(text=' '.join(new_text))
    return f"\nText of note with id {note.id} has been changed"


@func_arg_error
def edit_creation_date(note_id: str, new_date: str) -> str:
    if not note_id:
        return "You must enter id of a note to edit!"
    note = Note.objects(id=note_id).first()
    if not note:
        return "There is no note with this id!"

    try:
        is_valid_date(new_date)
    except ValidationError as err:
        return str(err)
    note.creation = new_date
    note.update(created=new_date)
    return f"\nDate of creation of the note with id {note.id} has changed"


@func_arg_error
def add_tags(note_id: str, *tags) -> str:
    if not note_id:
        return "You must enter id of a note to edit!"
    note = Note.objects(id=note_id).first()
    if not note:
        return "There is no note with this id!"
    if not tags:
        return "You must enter some tags to add!"
    new_tags = []
    current_tags = note.tags
    for el in tags:
        tag = Tag.objects(tag=el).first()
        if tag in current_tags:
            continue
        if not tag:
            tag = Tag(tag=el).save()
        new_tags.append(tag)

    if not new_tags:
        return f"\nThere is no new tags to add to the note with id `{note.id}`\n"
    note.update(tags=current_tags+new_tags)
    return f"\nFollowing tags have been added to the note with id \n" \
           f"\t{' '.join([el.tag for el in new_tags])}"


@func_arg_error
def show_all() -> str:
    notes = Note.objects(is_done=False)
    if not notes:
        return "\nThere are no notes to show yet..."
    result = "\nList of all notes:\n"
    for page in pagination(notes):
        result += page
    return result


@func_arg_error
def show_done_notes():
    """ Show notes with status `done` """
    notes = Note.objects(is_done=True)
    if not notes:
        return "\nThere are no done notes"
    result = "\nList of all done notes:\n"
    for page in pagination(notes):
        result += page
    return result


@func_arg_error
def find_by_text(search_string: str) -> str:
    """ Find (sub-)string `search_string` in the text of the note """
    notes = Note.objects(is_done=False)
    if not notes:
        return "\nThere are no notes to show yet..."
    data = []
    for note in notes:
        if search_string.lower() in note.text.lower():
            data.append(note)
    if not data:
        return f"\nNo results for `{search_string}` term in text of notes...\n"
    result = f"\nFound results for `{search_string}` term in text of notes:\n"
    for page in pagination(data):
        result += page
    return result


@func_arg_error
def find_by_tag(search_string: str) -> str:
    """ Find (sub-)string `search_string` in the text of the tags """
    notes = Note.objects(is_done=False)
    if not notes:
        return "\nThere are no notes to show yet..."
    data = []
    for note in notes:
        tags = [el.tag for el in note.tags]
        if search_string.lower() in ' '.join(tags).lower():
            data.append(note)
    if not data:
        return f"\nNo notes with tag `{search_string}`..\n"
    result = f"\nFound notes with tag `{search_string}:\n"
    for page in pagination(data):
        result += page
    return result


@func_arg_error
def mark_as_done(note_id: str) -> str:
    if not note_id:
        return "You must enter id of a note to edit!"
    note = Note.objects(id=note_id).first()
    if not note:
        return "There is no note with this id!"

    note.update(is_done=True)
    return f"\nNote with id {note.id} has been marked as done"


@func_arg_error
def unmark_as_done(note_id: str) -> str:
    if not note_id:
        return "You must enter id of a note to edit!"
    note = Note.objects(id=note_id).first()
    if not note:
        return "There is no note with this id!"

    note.update(is_done=False)
    return f"\nNote with id {note.id} has been marked as undone"


if __name__ == '__main__':
    print(add_note())
    # print(show_all())

