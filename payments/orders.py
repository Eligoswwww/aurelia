from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Order, UserPurchase, User
from sqlalchemy import select
from datetime import datetime, timedelta
from payments.paypal import create_paypal_order, capture_paypal_order
from db.models import User

async def create_order(
    session: AsyncSession,
    user_id: int,
    order_type: str,
    amount: float,
    part_id: Optional[int] = None,
    payment_id: Optional[str] = None,
) -> Order:
    order = Order(
        user_id=user_id,
        order_type=order_type,
        amount=amount,
        part_id=part_id,
        payment_id=payment_id,
        status="pending"
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

async def mark_order_paid(session: AsyncSession, payment_id: str):
    result = await session.execute(select(Order).where(Order.payment_id == payment_id))
    order = result.scalar_one_or_none()
    if not order:
        return False

    order.status = "paid"
    # Обновляем права пользователя в зависимости от типа заказа
    user = order.user
    if order.order_type == "subscription":
        user.subscribed = True
        user.subscription_expire = datetime.utcnow() + timedelta(days=30)  # например, 30 дней подписки
    elif order.order_type in ("chapter", "full_access"):
        if order.part_id:
            purchase = UserPurchase(user_id=user.id, part_id=order.part_id)
            session.add(purchase)
        if order.order_type == "full_access":
            user.subscribed = True
            user.subscription_expire = None  # бессрочный доступ

    await session.commit()
    return True
# payments/orders.py

from .mock_gateway import process_payment

async def pay_and_unlock_full_book(session, user_id: int, order):
    success = await process_payment(order.id, order.amount)
    if not success:
        return False

    # Отметить заказ как оплаченный
    await mark_order_paid(session, order.id)

    # Обновить пользователя — дать доступ к полной книге
    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.has_full_access = True
        await session.commit()
    return True
from payments.paypal import create_paypal_order, capture_paypal_order
from db.models import User

async def create_paypal_payment(session, user_id: int, amount: float, return_url: str, cancel_url: str):
    # Создаем заказ в базе
    order = await create_order(session, user_id=user_id, order_type="full_access", amount=amount)
    paypal_order_id, approve_url = await create_paypal_order(amount, return_url, cancel_url)
    if not approve_url:
        return None, None

    # Сохрани paypal_order_id в заказе (если поле есть)
    order.paypal_order_id = paypal_order_id
    await session.commit()
    return order, approve_url

async def mark_order_paid_by_paypal(session, paypal_order_id: str):
    result = await session.execute(select(User).join(UserPurchase).where(UserPurchase.paypal_order_id == paypal_order_id))
    purchase = result.scalar_one_or_none()
    if purchase:
        await mark_order_paid(session, purchase.id)
        # Даем доступ пользователю
        user = await session.get(User, purchase.user_id)
        if user:
            user.has_full_access = True
            await session.commit()
        return True
    return False
