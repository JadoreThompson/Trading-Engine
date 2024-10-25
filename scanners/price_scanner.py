import asyncio
import random
import threading
import time
import ccxt
from sqlalchemy import distinct, select

from config import REDIS_CLIENT
from db_models import Orders
from utils import get_session


# In a thread for each ticker we run an async process that
# is watching the price

async def watch_price(ticker):
    exch = ccxt.binance()
    exch.load_markets()
    price = 0

    while True:
        try:
            # print(type(exch.fetch_mark_price(ticker)))
            # print(1)
            new_price = float(exch.fetch_mark_price(ticker).get('info', {}).get('indexPrice', None))
            if new_price > price:
                price = new_price
                REDIS_CLIENT.publish(channel=ticker, message=round(price, 2))
                print(f"{ticker}", price)
        except Exception as e:
            print(type(e), str(e))
            continue


def price_bridger(ticker):
    asyncio.run(watch_price(ticker))


async def price_overseer():
    threads = []

    tickers = ['BTC/USDT', 'SOL/USDT', 'ETH/USDT']

    for ticker in tickers:
        thread = threading.Thread(target=price_bridger, args=(ticker,), daemon=True)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def run():
    asyncio.run(price_overseer())


if __name__ == "__main__":
    run()
