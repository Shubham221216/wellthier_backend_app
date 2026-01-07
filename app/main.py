from fastapi import FastAPI
import socketio
import os

from app.api import auth
from app.api.socket import sio
from app.db.database import engine,Base
from app.api import user_weight_logs
from app.api import analytics
from app.api import sleep_log




# app = FastAPI()
fastapi_app = FastAPI()

@fastapi_app.get("/api/health")
async def read_root():
    return {"msg": "Success"}

@fastapi_app.get("/")
async def read_main():
    return {"msg": "Welcome to Wellthier Backend API"}


fastapi_app.include_router(auth.router)
fastapi_app.include_router(user_weight_logs.router)
fastapi_app.include_router(analytics.router)
fastapi_app.include_router(sleep_log.router)



# 🔥 Mount Socket.IO
app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=fastapi_app
)