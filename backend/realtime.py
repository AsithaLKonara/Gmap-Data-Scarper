from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
from models import User
from auth import get_current_user
from fastapi import status, HTTPException
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM
from database import SessionLocal

router = APIRouter()

# In-memory pub/sub
active_connections: Dict[int, List[WebSocket]] = {}

def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        return user
    except Exception:
        return None

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = get_user_from_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    if user.id not in active_connections:
        active_connections[user.id] = []
    active_connections[user.id].append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        active_connections[user.id].remove(websocket)
        if not active_connections[user.id]:
            del active_connections[user.id]

# Call this function when a new notification is created
async def broadcast_notification(user_id: int, notification_data: dict):
    connections = active_connections.get(user_id, [])
    for ws in connections:
        await ws.send_json(notification_data) 