from flask import render_template, request, flash, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
import pathlib
import uuid
from datetime import datetime, timedelta
from marshmallow import ValidationError
from . import app
from src.libs.validation_file import is_allowed_filename
from src.repository import pictures as rep_pict
from src.repository import users as rep_users
from src.libs.validation_sсhemas import RegistrationSchema, LoginSchema


@app.before_request
def before_func():
    """ Check if `Remember` was checked and login automatically"""
    auth = True if 'username' in session else False
    if not auth:
        token_user = request.cookies.get('username')
        if token_user:
            user = rep_users.get_user_by_token(token_user)
            if user:
                session['username'] = {"username": user.username, "id": user.id}


@app.route('/healthcheck', strict_slashes=False)
def healthcheck():
    return 'I am working'


@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    print(auth)
    return render_template('pages/index.html', title='Cloud Pictures', auth=auth)


@app.route('/pictures', strict_slashes=False)
def pictures():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)  # return from where it was
    pictures_user = rep_pict.get_all_pictures(session['username']['id'])
    return render_template('pages/pictures.html', auth=auth, pictures=pictures_user)


@app.route('/registration', methods=['GET', 'POST'], strict_slashes=False)
def registration():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            RegistrationSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/registration.html', messages=err.messages)
        email = request.form.get('email')
        password = request.form.get('password')
        nick = request.form.get('nick')
        user = rep_users.create_user(email, password, nick)
        # print(user)
        return redirect(url_for('login'))
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/registration.html')


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            LoginSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/login.html', messages=err.messages)
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') == 'on' else False
        # remember: None - unchecked, 'on' - checked

        user = rep_users.login(email, password)
        print(user)
        if user is None:
            return redirect(url_for('login'))
        session['username'] = {"username": user.username, "id": user.id}
        response = make_response(redirect(url_for('index')))
        if remember:
            token = str(uuid.uuid4())
            expire_data = datetime.now() + timedelta(days=60)
            response.set_cookie('username', token, expires=expire_data)
            rep_users.set_token(user, token)
        return response
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/login.html')


@app.route('/logout', strict_slashes=False)
def logout():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    session.pop('username')
    response = make_response(redirect(url_for('index')))
    response.set_cookie('username', '', expires=-1)  # remove cookie when logging out

    return response


@app.route('/pictures/upload', methods=['GET', 'POST'], strict_slashes=False)
def pictures_upload():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'POST':
        description = request.form.get('description')
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file!', category="error")
            return redirect(request.url)
        if file and is_allowed_filename(file.filename):
            filename = secure_filename(file.filename)
            file_path = pathlib.Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(file_path)
            rep_pict.upload_file_for_user(session['username']['id'], file_path, description)
            flash('Picture has been uploaded successfully')
            return redirect(url_for('pictures_upload'))
    return render_template('pages/upload.html', auth=auth)


@app.route('/pictures/edit/<pict_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_picture(pict_id: int):
    """ Edit description of a picture """
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_id = session['username']['id']
    picture = rep_pict.get_one_picture(pict_id, user_id)
    if request.method == 'POST':
        description = request.form.get('description')
        rep_pict.update_picture(pict_id, user_id, description)
        return redirect(url_for('pictures'))
    return render_template('pages/edit.html', auth=auth, picture=picture)


@app.route('/pictures/delete/<pict_id>', methods=['POST'], strict_slashes=False)
def delete(pict_id: int):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'POST':
        if rep_pict.delete_picture(pict_id, session['username']['id']):
            flash('Picture has been deleted successfully')
        else:
            flash('Wrong path to the picture!', category="error")
    return redirect(url_for('pictures'))
