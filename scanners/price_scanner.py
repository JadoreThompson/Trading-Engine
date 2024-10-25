import asyncio
import threading
import ccxt

# Local
from config import REDIS_CLIENT


async def watch_price(ticker):
    """Publishes ticker price to channel, triggers event"""
    exch = ccxt.binance()
    exch.load_markets()
    price = 0

    while True:
        try:
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
