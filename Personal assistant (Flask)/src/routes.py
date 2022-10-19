import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from . import app
from flask import render_template, request, session, redirect, url_for, make_response, flash

from src.repository import users, notes, contacts
from src import repository
from marshmallow import ValidationError
from src.libs.validation_schemas import SignUpSchema, SignInSchema
from .libs.forms import TagForm, NoteForm
from .repository.seed import create_contacts


@app.before_request
def before_func():
    """ Check if `Remember` was checked and sig in automatically"""
    auth = True if 'username' in session else False
    if not auth:
        token_user = request.cookies.get('username')
        if token_user:
            user = repository.users.get_user_by_token(token_user)
            if user:
                session['username'] = {"username": user.username, "id": user.id}


@app.route('/healthcheck')
def healthcheck():
    return 'Console bot app: running'


@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    username = session['username'].get('username') if 'username' in session else None
    return render_template('pages/index.html', auth=auth, username=username)


@app.route('/signup', methods=['GET', 'POST'], strict_slashes=False)
def sign_up():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            SignUpSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/sign_up.html', not_auth=True, messages=err.messages)
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1 != password2:
            return render_template('pages/sign_up.html', not_auth=True, messages="Passwords don't match!")
        username = request.form.get('username').strip()
        try:
            user = repository.users.sign_up_user(username, password1)
        except IntegrityError:
            return render_template('pages/sign_up.html', not_auth=True,
                                   error='This username is already used... Try another one')
        except AssertionError as err:
            return render_template('pages/sign_up.html', not_auth=True, error=err)
        # print(user)
        return redirect(url_for('index'))
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/sign_up.html', not_auth=True)


@app.route('/signin', methods=['GET', 'POST'], strict_slashes=False)
def sign_in():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            SignInSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/sign_in.html', not_auth=True, messages=err.messages)
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') == 'on' else False

        user = repository.users.sign_in_user(username, password)
        # print(user)
        if user is None:
            message = {'Login error': ["Wrong username or password!"]}
            return render_template('pages/sign_in.html', not_auth=True, messages=message)
        session['username'] = {"username": user.username, "id": user.id}
        response = make_response(redirect(url_for('index')))
        if remember:
            token = str(uuid.uuid4())
            expire_data = datetime.now() + timedelta(days=60)
            response.set_cookie('username', token, expires=expire_data)
            repository.users.set_token(user, token)
        return response
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/sign_in.html', not_auth=True)


@app.route('/signout', strict_slashes=False)
def sign_out():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    session.pop('username')
    response = make_response(redirect(url_for('index')))
    response.set_cookie('username', '', expires=-1)  # remove cookie when logging out

    return response


@app.route('/notebook', strict_slashes=False)
def notebook():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    user_notes = repository.notes.get_all_notes(session['username']['id'])
    return render_template('pages/notebook/notebook.html', auth=auth, notes=user_notes)


@app.route('/notebook/tag', methods=['GET', 'POST'], strict_slashes=False)
def add_tag():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            form = TagForm(request.form)
            notes.create_tag(session['username']['id'], form)
            flash('Tag has been created successfully')
            return redirect(url_for('add_tag'))
        except ValueError as err:
            return render_template('pages/notebook/tag.html', auth=auth, error=err)
        except IntegrityError:
            return render_template('pages/notebook/tag.html', error='Tag must be unique!')
    return render_template('pages/notebook/tag.html')


@app.route('/notebook/note', methods=['GET', 'POST'], strict_slashes=False)
def add_note():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    user_id = session['username']['id']
    user_tags = notes.get_tag_list(user_id)
    if request.method == 'POST':
        try:
            tag_list = request.form.getlist('tags')
            form = NoteForm(request.form)
            # print(form)
            # print(form.name, form.description, tag_list)
            notes.create_note(user_id, form, tag_list)
            return redirect(url_for('notebook'))
        except ValueError as err:
            return render_template('pages/notebook/note.html', tags=user_tags, error=err)
    return render_template('pages/notebook/note.html', tags=user_tags)


@app.route('/notebook/note/details', strict_slashes=False)
def note_details():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    note_id = int(request.args['note_id'])
    user_id = session['username']['id']
    note = repository.notes.get_note(note_id, user_id)
    return render_template('pages/notebook/detail.html', note=note)


@app.route('/notebook/note/set', strict_slashes=False)
def set_done():
    note_id = int(request.args['note_id'])
    user_id = session['username']['id']
    repository.notes.set_done_note(note_id, user_id)
    return redirect(url_for('notebook'))


@app.route('/notebook/note/delete', strict_slashes=False)
def delete_note():
    note_id = int(request.args['note_id'])
    user_id = session['username']['id']
    repository.notes.delete_note(note_id, user_id)
    return redirect(url_for('notebook'))


@app.route('/contacts', strict_slashes=False)
def contacts():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    user_contacts = repository.contacts.get_all_contacts(session['username']['id'])
    return render_template('pages/contacts/contacts.html', contacts=user_contacts)


@app.route('/contacts/contact', methods=['GET', 'POST'], strict_slashes=False)
def add_contact():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    # create_contacts()  # call seed-function to fill data!
    if request.method == 'POST':
        try:
            repository.contacts.create_contact(request.form, session['username']['id'])
        except ValueError as err:
            return render_template('pages/contacts/contact.html', error=err)
        except AssertionError as err:
            return render_template('pages/contacts/contact.html', error=err)
        return redirect(url_for('contacts'))
    return render_template('pages/contacts/contact.html', title='Add contact')


@app.route('/contacts/contact/details', strict_slashes=False)
def contact_details():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    contact_id = int(request.args['contact_id'])
    user_id = session['username']['id']
    cont_details = repository.contacts.get_contact(user_id, contact_id)
    return render_template('pages/contacts/detail.html', contact=cont_details)


@app.route('/contacts/edit', methods=['GET', 'POST'], strict_slashes=False)
def edit_contact():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    user_id = session['username']['id']
    if request.method == 'POST':
        try:
            cont_details = repository.contacts.update_contact(request.form, user_id)
        except ValueError as err:
            return render_template('pages/contacts/contact.html', error=err)
        return redirect(url_for('contact_details', contact_id=cont_details.id))
    else:
        contact_id = int(request.args['contact_id'])
        cont_details = repository.contacts.get_contact(user_id, contact_id)
    return render_template('pages/contacts/contact.html', title="Edit contact", contact=cont_details)


@app.route('/contacts/delete', strict_slashes=False)
def delete_contact():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    user_id = session['username']['id']
    contact_id = int(request.args['contact_id'])
    repository.contacts.delete_contact(user_id, contact_id)
    return redirect(url_for('contacts'))
