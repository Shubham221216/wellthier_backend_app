from fastapi import FastAPI
import socketio
import os

from app.api import auth
from app.api.socket import sio
from app.db.database import engine,Base

# app = FastAPI()
fastapi_app = FastAPI()

@fastapi_app.get("/api/health")
async def read_root():
    return {"msg": "Success"}



fastapi_app.include_router(auth.router)

# 🔥 Mount Socket.IO
app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=fastapi_app
)