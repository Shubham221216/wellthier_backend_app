import socketio

sio = socketio.AsyncServer(
    async_mode = 'asgi',
    cors_allowed_origins = '*',
)

# ----------------------------
# Socket Events
# ----------------------------

@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_room(sid, room):
    # room = data.get('room')
    await sio.enter_room(sid, room)
    # await sio.emit('room_joined', {'room': room}, room=sid)
    print(f"{sid} joined room {room}")

# @sio.event
# async def send_message(sid, data):
#     """
#     data = {
#         "room": "chat_u1_u2",
#         "sender_id": "u1",
#         "receiver_id": "u2",
#         "text": "Hello"
#     }
#     """
#     room = data["room"]
#     await sio.emit("receive_message", data, room=room)


@sio.event
async def send_message(sid, data):
    room = data["room"]

    print("📩 Message received from client:")
    print(f"  SID: {sid}")
    print(f"  ROOM: {room}")
    print(f"  SENDER: {data.get('sender_id')}")
    print(f"  TEXT: {data.get('text')}")

    # broadcast to everyone in room
    await sio.emit("receive_message", data, room=room)



# VERY IMPORTANT NEXT STEPS (Backend-first)

# Now we upgrade this into a real app, not a demo.

# 🔹 1️⃣ Persist messages (PostgreSQL)

# Save every message

# Load chat history when user opens chat

# 🔹 2️⃣ JWT-authenticated sockets

# Only logged-in users connect

# Secure room access

# 🔹 3️⃣ Online / offline users

# Presence indicator

# Last seen

# 🔹 4️⃣ Typing indicators
# typing_start
# typing_stop

# 🔹 5️⃣ Read / delivered receipts
# message_delivered
# message_seen
