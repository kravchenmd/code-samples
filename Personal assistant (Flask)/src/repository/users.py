from src import db
from src import models
import bcrypt


def sign_up_user(nickname: str, password: str) -> models.User:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=8))
    user = models.User(username=nickname, hash=hashed)
    db.session.add(user)
    db.session.commit()
    return user


def sign_in_user(username: str, password: str) -> None | models.User:
    user = find_by_username(username)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user.hash):  # `not` -> match
        return None
    return user


def find_by_username(username: str) -> models.User:
    user = db.session.query(models.User).filter(models.User.username == username).first()
    return user


def find_by_id(_id: str) -> models.User:
    user = db.session.query(models.User).filter(models.User.id == _id).first()
    return user


def set_token(user: models.User, token: str) -> None:
    user.token_cookie = token
    db.session.commit()


def get_user_by_token(token: str) -> None | models.User:
    user = db.session.query(models.User).filter(models.User.token_cookie == token).first()
    if not user:
        return None
    return user
