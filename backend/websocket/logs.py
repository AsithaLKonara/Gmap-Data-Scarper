"""WebSocket handlers for real-time log streaming."""
from fastapi import WebSocket, WebSocketDisconnect
from backend.services.orchestrator_service import task_manager
from backend.models.schemas import LogMessage
from datetime import datetime
import json


async def log_stream(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for streaming logs.
    
    Note: Authentication should be handled before calling this function.
    """
    # WebSocket should already be accepted by the route handler
    if websocket.client_state.name != "CONNECTED":
        await websocket.accept()
    
    # Register WebSocket connection
    task_manager.register_websocket(task_id, "logs", websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(
            LogMessage(
                level="INFO",
                message=f"Connected to log stream for task {task_id}"
            ).model_dump_json()
        )
        
        # Keep connection alive and forward messages
        while True:
            # Wait for any message (ping/pong or close)
            try:
                data = await websocket.receive_text()
                # Echo back or handle ping
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
            
    except Exception as e:
        # Send error and close
        try:
            await websocket.send_text(
                LogMessage(
                    level="ERROR",
                    message=f"WebSocket error: {str(e)}"
                ).model_dump_json()
            )
        except Exception as ws_error:
            import logging
            logging.warning(f"Failed to send error message to WebSocket: {ws_error}")
    finally:
        # Unregister WebSocket connection
        task_manager.unregister_websocket(task_id, "logs", websocket)

