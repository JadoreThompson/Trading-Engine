import random
from typing import Optional
from datetime import datetime
from uuid import uuid4

# SQLAlchemy
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, UUID, Integer, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from config import DB_ENGINE, ph
from enums import MarketSide


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, primary_key=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    api_key: Mapped[str] = mapped_column(String)

    # Relationships
    orders = relationship('Orders', back_populates='user')
    # watchlist = relationship('Watchlist', back_populates='user')


class Orders(Base):
    __tablename__ = 'trades'

    trade_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('users.email'), nullable=False)
    ticker: Mapped[str] = mapped_column(String)
    dollar_amount: Mapped[float] = mapped_column(Float)
    realised_pnl: Mapped[Optional[float]] = mapped_column(Float, default=0)
    unrealised_pnl: Mapped[Optional[float]] = mapped_column(Float, default=0)
    open_price: Mapped[Optional[float]] = mapped_column(Float)
    close_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    order_type: Mapped[str] = mapped_column(String)
    # execution_type: Mapped[str] = mapped_column(String)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=True)
    take_profit: Mapped[float] = mapped_column(Float, nullable=True)
    side: Mapped[float] = mapped_column(String, default=None, nullable=True)

    # Relationships
    user = relationship("Users", back_populates="orders")


from faker import Faker
async def create_fake_data(session: AsyncSession):

    fake = Faker()

    for _ in range(0, 1):
    #     key = fake.uuid4()
    #     print(key)
    #     email = fake.email()
    #     print(email)
    #     user = Users(
    #         email=email,
    #         password=fake.password(),
    #         balance=fake.random_number(digits=5),
    #         api_key=ph.hash(key)
    #     )
    #     session.add(user)
    #     await session.flush()  # Ensure the user is added to the DB

        email = 'joneswilliam@example.org'
        tickers = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        sides = [MarketSide.LONG.value, MarketSide.SHORT.value]
        for _ in range(100):
            trade = Orders(
                side=sides[random.randint(0, 1)],
                user_id=email,
                ticker=tickers[random.randint(0, len(tickers) - 1)],
                dollar_amount=fake.random_number(digits=4),
                open_price=fake.random_number(digits=3),
                close_price=fake.random_number(digits=3),
                order_type=fake.random_element(elements=('buy', 'sell')),
            )
            session.add(trade)
        await session.flush()



async def create():
    async with DB_ENGINE.begin() as conn:
        async_session = sessionmaker(conn, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            await create_fake_data(session)


if __name__ == "__main__":
    import asyncio
    # asyncio.run(create())
