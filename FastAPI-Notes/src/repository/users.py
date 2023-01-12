from sqlalchemy.orm import Session
from src.models import User
from src.schemas.users import UserModel
from src.libs.hash import Hash


async def get_all_users(db: Session, skip: int, limit: int):
    all_users = db.query(User).offset(skip).limit(limit).all()
    return all_users


async def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user


async def get_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    return user


async def create_user(db: Session, user: UserModel):
    new_user = User(username=user.username, email=user.email, password=Hash.get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_user(db: Session, user_id: int, new_user: UserModel):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        await user.update(username=new_user.username, email=new_user.email,
                          password=Hash.get_password_hash(new_user.password)).aplly()
    return user


async def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        await user.delete()
    return user
