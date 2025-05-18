from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_expire: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    has_full_access: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связь с покупками пользователя (UserPurchase)
    purchases: Mapped[list["UserPurchase"]] = relationship("UserPurchase", back_populates="user")

    # Связь с заказами
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")


class BookPart(Base):
    __tablename__ = "book_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String)  # Текст части книги
    part_type: Mapped[str] = mapped_column(String(50))  # 'chapter', 'volume', 'bonus'
    price: Mapped[float] = mapped_column(Float, default=0.0)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("book_parts.id"), nullable=True)

    parent: Mapped["BookPart | None"] = relationship("BookPart", remote_side=[id], backref="subparts")


class UserPurchase(Base):
    __tablename__ = "user_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    part_id: Mapped[int] = mapped_column(Integer, ForeignKey("book_parts.id"))
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="purchases")
    part: Mapped["BookPart"] = relationship("BookPart")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    part_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("book_parts.id"), nullable=True)  # если покупка части
    order_type: Mapped[str] = mapped_column(String(50))  # "subscription", "chapter", "full_access"
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, paid, canceled
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)  # ID платежа из PayPal или Boosty
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="orders")
    part: Mapped["BookPart | None"] = relationship("BookPart", foreign_keys=[part_id])
