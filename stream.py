import json

import starlette.websockets
import uvicorn
from fastapi import WebSocket, APIRouter


# Local
import exceptions
from managers import ConnectionManager

stream = APIRouter(prefix='/socket', tags=['socket'])


@stream.websocket('/trade')
async def trade(websocket: WebSocket):
    """
    Allows user to send and receive trade updates
    :param websocket:
    :return:
    """
    socket = ConnectionManager(websocket)
    await socket.connect()
    try:
        while True:
            await socket.recv()
    except (
            RuntimeError,
            starlette.websockets.WebSocketDisconnect,
            uvicorn.protocols.utils.ClientDisconnected,
            exceptions.NotSupplied
    ) as e:
        print(type(e), str(e))
        pass
