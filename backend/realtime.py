from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
from models import Users
from auth import get_current_user
from fastapi import status, HTTPException
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM
from database import SessionLocal

"""
This module provides real-time notification delivery via WebSocket for authenticated users.
Clients connect to /api/realtime/ws/notifications with a valid JWT token as a query parameter.
When a notification is created for a user, it is broadcast to all active WebSocket connections for that user.
"""

router = APIRouter(prefix="/api/realtime", tags=["realtime"])

# In-memory pub/sub
active_connections: Dict[int, List[WebSocket]] = {}

def get_user_from_token(token: str):
    """
    Decode a JWT token and return the associated User object, or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        db = SessionLocal()
        user = db.query(Users).filter(Users.id == user_id).first()
        db.close()
        return user
    except Exception:
        return None

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.
    
    Query Parameters:
        token (str): JWT token for authentication. Must be provided as a query parameter.
    
    On connection, the server authenticates the user and adds the WebSocket to the user's active connections.
    Notifications can be sent to all active connections for a user using broadcast_notification().
    """
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

# Internal utility: Call this function when a new notification is created
async def broadcast_notification(user_id: int, notification_data: dict):
    """
    Broadcast a notification to all active WebSocket connections for the given user.
    Args:
        user_id (int): The user ID to send the notification to.
        notification_data (dict): The notification payload to send as JSON.
    """
    connections = active_connections.get(user_id, [])
    for ws in connections:
        await ws.send_json(notification_data) 