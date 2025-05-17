from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Order, UserPurchase, User
from sqlalchemy import select
from datetime import datetime, timedelta

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
