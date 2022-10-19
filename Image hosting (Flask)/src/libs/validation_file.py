ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def is_allowed_filename(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
