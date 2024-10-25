import json
from contextlib import asynccontextmanager
from datetime import timedelta, datetime

import argon2.exceptions
from argon2 import PasswordHasher

# Local
from db_models import Users
# from dependencies import get_session
from config import API_KEY_ALIAS, ph, REDIS_CLIENT
from exceptions import DoesNotExist

# Starlette
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# SQLAlchemy
from sqlalchemy import select


class WebsocketExceptionHandler:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except:
            print('caught')
        finally:
            return await self.app(scope, receive, send)
