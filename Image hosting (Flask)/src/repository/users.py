from src import db
from src import models
import bcrypt


def create_user(email: str, password: str, nickname: str) -> models.User:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
    user = models.User(username=nickname, email=email, hash=hashed)
    db.session.add(user)
    db.session.commit()
    return user


def login(email: str, password: str) -> None | models.User:
    user = find_by_email(email)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user.hash):  # `not` -> match
        return None
    return user


def find_by_email(email: str) -> models.User:
    user = db.session.query(models.User).filter(models.User.email == email).first()
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
