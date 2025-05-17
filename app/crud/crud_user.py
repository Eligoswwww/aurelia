from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CRUDUser:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, user_id: int):
        return db.query(self.model).filter(self.model.id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, obj_in: UserCreate):
        hashed_password = pwd_context.hash(obj_in.password)
        db_obj = self.model(
            email=obj_in.email,
            hashed_password=hashed_password,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate):
        if obj_in.password:
            db_obj.hashed_password = pwd_context.hash(obj_in.password)
        if obj_in.is_active is not None:
            db_obj.is_active = obj_in.is_active
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, email: str, password: str):
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

crud_user = CRUDUser(User)
