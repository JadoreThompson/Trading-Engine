import asyncio
import json
from contextlib import asynccontextmanager
import argon2.exceptions
from sqlalchemy import insert, select, update

# FA
from fastapi import WebSocket
import pydantic_core

# Local
from config import API_KEY_ALIAS, REDIS_CLIENT
from db_models import Orders
from enums import OrderType
from exceptions import DoesNotExist, NotSupplied
from models import CreateTradeRequest, MarketOrder
from utils import get_user, get_session


@asynccontextmanager
async def websocket_exception_handler(websocket: WebSocket):
    """
    Handler for any exceptions that occur during operation
    much like the add_exception_handler decorator from FastAPI
    """
    try:
        yield websocket
    except Exception as e:
        if isinstance(e, argon2.exceptions.InvalidHashError):
            await websocket.send_text(json.dumps({'e': 'Invalid API Key'}))
        elif isinstance(e, pydantic_core.ValidationError):
            await websocket.send_text(json.dumps({'e': 'Invalid Model Schemas'}))
        elif isinstance(e, DoesNotExist):
            await websocket.send_text(json.dumps({'e': str(e)}))
        elif isinstance(e, RuntimeError):
            pass
        await websocket.close()



class ConnectionManager:
    def __init__(self, websocket: WebSocket = None):
        self.socket = websocket
        self.pubsub = REDIS_CLIENT.pubsub()
        self.channel_name: str = ""

    async def connect(self):
        """
        Connects to client and waits for the api key to be sent,
        once validated user can continue to send requests
        :return:
        """
        async with websocket_exception_handler(self.socket) as socket:
            # Signing User to ensure they exist
            await socket.accept()
            m = await socket.receive_text()
            m = json.loads(m)
            self.user = await get_user(m[API_KEY_ALIAS])
            self.channel_name = f"{self.user.email}-trades"

            asyncio.create_task(self.ping())

            self.pubsub.subscribe(self.channel_name)
            asyncio.create_task(self.relay_messages)
            await socket.send_text(json.dumps({'m': 'connection established'}))


    async def ping(self):
        """
        Pings client to keep connection alive during times of no sendouts
        """
        async with websocket_exception_handler(self.socket) as socket:
            while True:
                await asyncio.sleep(5)
                await self.socket.send_bytes(bytes('ping'.encode('utf-8')))


    async def recv(self):
        """
        Receives close order and open order request
        and creates the appropriate task
        :return:
        """
        async with websocket_exception_handler(self.socket) as socket:
            m = await socket.receive_text()
            m = json.loads(m)
            action = m.get('action', None)

            if action == 'open':
                asyncio.create_task(self.process_order(m))
            elif action == 'close':
                asyncio.create_task(self.close_trade(m))


    async def process_order(self, data):
        """
        Cleans the incoming create order request and funnels it's properties
        :param data:
        :return:
        """
        async with websocket_exception_handler(self.socket) as socket:
            order = CreateTradeRequest(**data)
            order_type = order.type

            if order_type == OrderType.MARKET_ORDER:
                try:
                    details = MarketOrder(**{k: v for k, v in vars(
                        order.order_details.market_order).items()} if order.order_details.market_order else None)
                except TypeError:
                    raise NotSupplied(OrderType.MARKET_ORDER.value)

            asyncio.create_task(self.create_trade(details, socket, order_type))

    async def create_trade(self, data, socket, order_type):
        """
        Creates a row in the Orders Table
        :param data:
        :param socket:
        :param order_type:
        :return:
        """
        async with get_session() as session:
            order = await session.execute(insert(Orders)
            .values(
                **data.dict(),
                user_id=self.user.email,
                order_type=order_type
            ).returning(Orders.trade_id))
            order_id = str(order.scalar_one())
            await session.commit()
        await socket.send_text(json.dumps({'m': 'Order created successfully', 'oi': order_id}))


    async def close_trade(self, data: dict):
        """
        Set's is_active to False for the specific trade
        :param data:
        :return:
        """
        async with websocket_exception_handler(self.socket) as socket:
            async with get_session() as session:
                trade_id = data.get('trade_id', None)
                result = await session.execute(select(Orders).where(Orders.trade_id == trade_id))
                order = result.fetchone()
                if order:
                    await session.execute(update(Orders)
                                          .where(Orders.trade_id == trade_id)
                                          .values(
                        unrealised_pnl=0,
                        realised_pnl=order.unrealised_pnl,
                        is_active=False
                    ))
                    await session.commit()
                    await socket.send_text(json.dumps({'m': 'Trade Closed Successfully'}))
                else:
                    raise DoesNotExist('Trade')

    async def relay_messages(self):
        """
        Reads messages from pubsub and sends back to client,
        See orders_scanner to understand
        :return:
        """
        while True:
            for m in self.pubsub.listen():
                if m and m.get('type') == 'message':
                    print(m)

    async def disconnect(self, reason):
        """Ends connection"""
        await self.socket.send_text(json.dumps({'m': 'disconnecting', 'r': reason}))
        await self.socket.close()
