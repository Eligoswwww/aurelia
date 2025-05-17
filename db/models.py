from sqlalchemy import (
    Integer, String, Boolean, DateTime, ForeignKey, Float, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_expire: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    has_full_access = Column(Boolean, default=False)

    purchases = relationship("UserPurchase", back_populates="user")
    orders = relationship("Order", back_populates="user")

class BookPart(Base):
    __tablename__ = "book_parts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String)  # Текст
    part_type: Mapped[str] = mapped_column(String(50))  # 'chapter', 'volume', 'bonus'
    price: Mapped[float] = mapped_column(Float, default=0.0)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("book_parts.id"), nullable=True)

    parent = relationship("BookPart", remote_side=[id], backref="subparts")

class UserPurchase(Base):
    __tablename__ = "user_purchases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    part_id: Mapped[int] = mapped_column(Integer, ForeignKey("book_parts.id"))
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="purchases")
    part = relationship("BookPart")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    part_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("book_parts.id"), nullable=True)  # если покупка отдельной части
    order_type: Mapped[str] = mapped_column(String(50))  # "subscription", "chapter", "full_access"
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, paid, canceled
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ID платежа из платежной системы
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    part = relationship("BookPart", foreign_keys=[part_id])
