import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to server")

@sio.event
def receive_message(data):
    print("📩 Message received:", data)

sio.connect("http://localhost:8000")

# Join room
sio.emit("join_room", "chat_test")

# Send message
sio.emit("send_message", {
    "room": "chat_test",
    "sender_id": "python_test",
    "text": "Hello from Python client"
})

time.sleep(5)
sio.disconnect()

