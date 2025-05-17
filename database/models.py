from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    referral_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_subscribed = Column(Boolean, default=False)
    subscription_expires = Column(DateTime, nullable=True)
    referrals = relationship("User", remote_side=[id])

class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
