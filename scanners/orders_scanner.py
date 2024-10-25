import json
import random
import threading
from typing import List, Set

from sqlalchemy import select, update, delete

from config import REDIS_CLIENT
# Local
from db_models import Orders, Users
from enums import OrderType, MarketSide, Topic
from models import TradeUpdate
from utils import get_session

import asyncio


class TradeManager:
    def __init__(self):
        self.is_active = True
        self.quotes: dict[str, float] = {}
        self.active_trades: List[Orders] = []
        # self.active_trades: Set[Orders] = set()
        # self.active_channels: Set[str] = set()
        self.active_channels: list[str] = []
        self.pubsub = REDIS_CLIENT.pubsub()

    async def get_active_trades(self):
        """
        Retrieves all active trades in sel
        :return:
        """
        async with get_session() as session:
            try:
                while self.is_active:
                    result = await session.execute(select(Orders).where(Orders.is_active == True))
                    trades = result.scalars().all()
                    await self.process_trades(trades)
                    for trade in self.active_trades:
                        asyncio.create_task(self.manage_trade(trade))
                        await asyncio.sleep(1)
                    # del trades
            except Exception as e:
                print(type(e), str(e))
                print('caught 2')


    async def process_trades(self, trades):
        try:
            for trade in trades:
                if trade not in self.active_trades:
                    self.active_trades.append(trade)

                if trade.ticker not in self.active_channels:
                    self.active_channels.append(trade.ticker)
                    self.pubsub.subscribe(trade.ticker)
        except Exception as e:
            print(type(e), str(e))
            print('caught')
        finally:
            return


    async def listen_for_message(self):
        await asyncio.sleep(1)
        while self.is_active:
            for m in self.pubsub.listen():
                if m and m.get('type', None) == 'message':
                    self.quotes[m.get('channel', None).decode('utf-8')] = float(m.get('data', None).decode())
                    # print("*\n" * 10 ** 2)
                    # print(m)
                    # print("*\n" * 10 ** 2)
                    # print(self.quotes)


    async def manage_trade(self, trade: Orders):
        """Manage individual trade lifecycle"""
        try:
            # Initialising properties in memory
            channel_name = f"{trade.user_id}-trades"
            print(channel_name)

            ticker = trade.ticker
            dollar_amount = trade.dollar_amount
            unrealised_pnl = trade.unrealised_pnl
            open_price = trade.open_price
            stop_loss = trade.stop_loss
            take_profit = trade.take_profit
            quote_price = self.quotes.get(ticker, None)
            side = trade.side

            # Managing
            async with get_session() as session:
                while trade.is_active and self.is_active:
                    new_price = self.quotes.get(ticker, None) == quote_price

                    if new_price == quote_price:
                        continue

                    if side == MarketSide.LONG:
                        unrealised_pnl = (dollar_amount * (1 - ((new_price - open_price) / open_price)))
                        try:
                            if stop_loss >= new_price >= take_profit:
                                trade.unrealised_pnl = unrealised_pnl
                                trade.is_active = False
                        except TypeError:
                            pass

                    if side == MarketSide.SHORT:
                        unrealised_pnl = (dollar_amount * (1 + ((new_price - open_price) / open_price)))
                        try:
                            if stop_loss <= new_price <= take_profit:
                                trade.unrealised_pnl = unrealised_pnl
                                trade.is_active = False
                        except TypeError:
                            pass

                    if (unrealised_pnl >= (-1 * dollar_amount)):
                        trade.realised_pnl = unrealised_pnl
                        trade.is_active = False

                    # Send equity update
                    REDIS_CLIENT.publish(
                        channel=channel_name,
                        message=json.dumps(
                            TradeUpdate(topic=Topic.UPDATE, value=unrealised_pnl, order_id=str(trade.trade_id)).dict()
                        )
                    )
                    await asyncio.sleep(1)

                if trade in self.active_trades:
                    self.active_trades.remove(trade)
                    await session.execute(delete(Orders).where(Orders.trade_id == trade.trade_id))
                    await session.commit()

                    REDIS_CLIENT.publish(
                        channel=channel_name, message=json.dumps(TradeUpdate(
                            topic=Topic.CLOSE, order_id=str(trade.trade_id)
                        ).dict())
                    )
        except Exception as e:
            print(f"Error managing trade {trade.trade_id}: {e}")
            print("-" * 30)


    async def close_trade(self, trade):
        async with get_session() as session:
            await session.execute(
                update(Orders).where(Orders.trade_id == trade.trade_id)
                .values(**trade)
            )
            await session.commit()


manager = TradeManager()

def bridge():
    asyncio.run(manager.listen_for_message())

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bridge())

def bridge2():
    asyncio.run(manager.get_active_trades())


def run2():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bridge2())


# async def main():
#     tasks = [
#         asyncio.create_task(manager.get_active_trades()),
#         # asyncio.create_task(manager.listen_for_message()),
#     ]
#     await asyncio.gather(*tasks)



if __name__ == "__main__":
    thread1 = threading.Thread(target=run, daemon=True)
    thread2 = threading.Thread(target=run2, daemon=True)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # import asyncio
    # asyncio.run(main())
