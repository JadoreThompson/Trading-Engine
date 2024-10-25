# Local
from middleware import WebsocketExceptionHandler
from stream import stream

# FA
from fastapi import FastAPI


app = FastAPI()
app.include_router(stream)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app")
