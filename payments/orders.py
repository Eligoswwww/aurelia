from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Order, UserPurchase, User
from sqlalchemy import select
from datetime import datetime, timedelta
from payments.paypal import create_paypal_order, capture_paypal_order

async def create_order(
    session: AsyncSession,
    user_id: int,
    order_type: str,
    amount: float,
    part_id: Optional[int] = None,
    payment_id: Optional[str] = None,
    paypal_order_id: Optional[str] = None,
) -> Order:
    order = Order(
        user_id=user_id,
        order_type=order_type,
        amount=amount,
        part_id=part_id,
        payment_id=payment_id,
        paypal_order_id=paypal_order_id,
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
        user.subscription_expire = datetime.utcnow() + timedelta(days=30)
    elif order.order_type in ("chapter", "full_access"):
        if order.part_id:
            purchase = UserPurchase(user_id=user.id, part_id=order.part_id)
            session.add(purchase)
        if order.order_type == "full_access":
            user.subscribed = True
            user.subscription_expire = None

    await session.commit()
    return True

async def pay_and_unlock_full_book(session: AsyncSession, user_id: int, order: Order):
    # Захватываем платеж через PayPal
    capture_id = await capture_paypal_order(order.paypal_order_id)
    if not capture_id:
        return False

    # Обновляем order с payment_id = capture_id и меняем статус
    order.payment_id = capture_id
    order.status = "paid"
    # Даем пользователю полный доступ
    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.has_full_access = True
        user.subscribed = True
        user.subscription_expire = None
    await session.commit()
    return True

async def create_paypal_payment(session: AsyncSession, user_id: int, amount: float, return_url: str, cancel_url: str):
    # Создаем заказ в базе с пустым paypal_order_id
    order = await create_order(session, user_id=user_id, order_type="full_access", amount=amount)

    # Создаем заказ в PayPal
    paypal_order_id, approve_url = await create_paypal_order(amount, return_url, cancel_url)
    if not approve_url:
        return None, None

    # Сохраняем paypal_order_id в заказе
    order.paypal_order_id = paypal_order_id
    await session.commit()

    return order, approve_url

async def mark_order_paid_by_paypal(session: AsyncSession, paypal_order_id: str):
    # Ищем заказ по paypal_order_id
    result = await session.execute(select(Order).where(Order.paypal_order_id == paypal_order_id))
    order = result.scalar_one_or_none()
    if not order:
        return False

    # Захватываем платеж (если еще не захвачен)
    if order.status != "paid":
        capture_id = await capture_paypal_order(paypal_order_id)
        if not capture_id:
            return False
        order.payment_id = capture_id
        order.status = "paid"
        # Обновляем пользователя
        user = await session.get(User, order.user_id)
        if user:
            user.has_full_access = True
            user.subscribed = True
            user.subscription_expire = None
        await session.commit()
    return True
