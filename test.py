import json
import websockets

# Local
from models import CreateTradeRequest

BASE_URL = "ws://127.0.0.1:80"


async def main():
    try:
        async with websockets.connect(BASE_URL + '/socket/trade') as socket:
            # joneswilliam@example.org
            # robinwilliams @ example.com

            sign = {'api-key': '62de7b66-0f6e-4036-8c52-cc9e7861e843'}
            await socket.send(json.dumps(sign))
            await socket.recv()
            while True:
                m = {
                    'action': 'close',
                    'trade_id': '4c7d0511-6235-4d7f-a175-bd52c37472cf'
                }
                await socket.send(json.dumps(m))

                r = await socket.recv()
                print(json.loads(r))

                await asyncio.sleep(3)
    except Exception as e:
        print(type(e), str(e))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
