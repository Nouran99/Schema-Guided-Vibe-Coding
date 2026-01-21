from fastapi import FastAPI, HTTPException, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import uuid
import hashlib
import json
import jwt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "chat-secret-key"
users_db = {}
rooms_db = {}
messages_db = []
active_connections = []
unread_counts = {}

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatRoomCreate(BaseModel):
    name: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt(username: str) -> str:
    return jwt.encode({"sub": username, "exp": time.time() + 3600}, SECRET_KEY, algorithm="HS256")

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections.append({"username": username, "websocket": websocket})
    users_db[username]["status"] = "online"
    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            if msg_data.get("type") == "typing":
                for conn in active_connections:
                    if conn["username"] != username:
                        await conn["websocket"].send_text(json.dumps({"type": "typing", "user": username}))
            elif msg_data.get("type") == "message":
                room_id = msg_data["room_id"]
                msg = {"id": len(messages_db), "room_id": room_id, "user_id": username, "content": msg_data["content"], "created_at": time.time()}
                messages_db.append(msg)
                for conn in active_connections:
                    if conn["username"] != username:
                        unread_counts[(conn["username"], room_id)] = unread_counts.get((conn["username"], room_id), 0) + 1
                    await conn["websocket"].send_text(json.dumps({"type": "new_message", "message": msg}))
    except:
        pass
    finally:
        active_connections[:] = [c for c in active_connections if c["username"] != username]
        users_db[username]["status"] = "offline"

@app.post("/api/auth/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username exists")
    users_db[user.username] = {"email": user.email, "password_hash": hash_password(user.password), "status": "offline"}
    return {"message": "User registered"}

@app.post("/api/auth/login")
def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if hash_password(user.password) != users_db[user.username]["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    users_db[user.username]["status"] = "online"
    token = create_jwt(user.username)
    return {"message": "Login successful", "token": token, "user": user.username}

@app.post("/api/rooms")
def create_room(room: ChatRoomCreate):
    room_id = str(uuid.uuid4())
    rooms_db[room_id] = {"name": room.name, "created_at": time.time()}
    return {"room_id": room_id, "message": "Room created"}

@app.get("/api/rooms")
def list_rooms():
    return [{"id": k, **v} for k, v in rooms_db.items()]

@app.post("/api/rooms/{room_id}/join")
def join_room(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": f"Joined room {room_id}"}

@app.get("/api/rooms/{room_id}/messages")
def get_messages(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    room_msgs = [m for m in messages_db if m["room_id"] == room_id]
    return room_msgs

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    await file.read()
    file_url = f"/uploads/{uuid.uuid4()}_{file.filename}"
    return {"file_url": file_url, "message": "File uploaded"}

@app.get("/api/users/status")
def get_user_status():
    return [{"username": k, "status": v["status"]} for k, v in users_db.items()]