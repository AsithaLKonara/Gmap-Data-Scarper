"""Scraper control endpoints."""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from backend.models.schemas import ScrapeRequest, TaskStatus
from backend.services.orchestrator_service import task_manager
from backend.services.stream_service import stream_service
from backend.websocket.logs import log_stream
from backend.middleware.auth import get_optional_user
import json
import asyncio
import os

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.post("/start", response_model=dict)
async def start_scraper(
    request: ScrapeRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Start a new scraping task."""
    from backend.services.plan_service import get_plan_service
    from fastapi import status
    
    try:
        # Require authentication (except in TESTING mode for automated tests)
        is_testing = os.getenv("TESTING") == "true"
        
        if not current_user:
            if is_testing:
                # Only allow unauthenticated access in TESTING mode for automated tests
                user_id = "test_user_12345"
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
        else:
            user_id = current_user.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user"
                )
        
        # Check plan limits (skip in TESTING mode only)
        from backend.models.database import get_session
        db = get_session()
        try:
            if is_testing and not current_user:
                # Skip limit check in TESTING mode for automated tests
                limit_check = {
                    'allowed': True,
                    'remaining': None,
                    'limit': None,
                    'used': 0,
                    'plan_type': 'free'
                }
            else:
                plan_service = get_plan_service(db)
                limit_check = plan_service.check_lead_limit(user_id)
        finally:
            db.close()
        
        if not limit_check['allowed']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Daily lead limit exceeded",
                    "message": f"You have used {limit_check['used']}/{limit_check['limit']} leads today. Upgrade to continue.",
                    "used": limit_check['used'],
                    "limit": limit_check['limit'],
                    "remaining": limit_check['remaining'],
                    "plan_type": limit_check['plan_type']
                }
            )
        
        request.user_id = user_id
        
        # Create task with audit fields
        task_id = task_manager.create_task(request, user_id=user_id)
        
        # Set audit fields on task if stored in database
        # (Task manager may store in memory, so this is optional)
        
        # Start Chrome stream
        stream_service.start_stream(task_id, headless=request.headless or False)
        
        # Start task in background
        task_manager.start_task(task_id, request)
        
        return {
            "status": "started",
            "task_id": task_id,
            "message": f"Scraping task {task_id} started",
            "usage": {
                "used": limit_check['used'],
                "limit": limit_check['limit'],
                "remaining": limit_check['remaining']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/{task_id}", response_model=dict)
async def stop_scraper(task_id: str):
    """Stop a running scraping task."""
    try:
        task_manager.stop_task(task_id)
        stream_service.stop_stream(task_id)
        return {
            "status": "stopped",
            "task_id": task_id,
            "message": f"Task {task_id} stopped"
        }
    except ValueError as e:
        from backend.utils.error_handler import not_found_error
        raise not_found_error(f"Task {task_id}")
    except Exception as e:
        from backend.utils.error_handler import handle_exception
        raise handle_exception(e, context="stop_scraper")


@router.post("/pause/{task_id}", response_model=dict)
async def pause_scraper(task_id: str):
    """Pause a running scraping task."""
    try:
        task_manager.pause_task(task_id)
        return {
            "status": "paused",
            "task_id": task_id,
            "message": f"Task {task_id} paused"
        }
    except ValueError as e:
        from backend.utils.error_handler import not_found_error
        raise not_found_error(f"Task {task_id}")
    except Exception as e:
        from backend.utils.error_handler import handle_exception
        raise handle_exception(e, context="pause_scraper")


@router.post("/resume/{task_id}", response_model=dict)
async def resume_scraper(task_id: str):
    """Resume a paused scraping task."""
    try:
        task_manager.resume_task(task_id)
        return {
            "status": "running",
            "task_id": task_id,
            "message": f"Task {task_id} resumed"
        }
    except ValueError as e:
        from backend.utils.error_handler import not_found_error
        raise not_found_error(f"Task {task_id}")
    except Exception as e:
        from backend.utils.error_handler import handle_exception
        raise handle_exception(e, context="resume_scraper")


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get status of a scraping task."""
    user_id = current_user.get("user_id") if current_user else None
    status = task_manager.get_task_status(task_id, user_id=user_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return status


@router.websocket("/ws/logs/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for streaming logs."""
    from backend.middleware.auth import get_websocket_user
    
    # Authenticate WebSocket connection
    try:
        current_user = await get_websocket_user(websocket)
        if not current_user:
            await websocket.close(code=1008, reason="Authentication required")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))
        return
    
    await websocket.accept()
    await log_stream(websocket, task_id)


@router.websocket("/ws/progress/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for streaming progress updates."""
    from backend.middleware.auth import get_websocket_user
    
    # Authenticate WebSocket connection
    try:
        current_user = await get_websocket_user(websocket)
        if not current_user:
            await websocket.close(code=1008, reason="Authentication required")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))
        return
    
    await websocket.accept()
    
    # Register WebSocket connection
    task_manager.register_websocket(task_id, "progress", websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Connected to progress stream for task {task_id}"
        }))
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except:
            pass
    finally:
        task_manager.unregister_websocket(task_id, "progress", websocket)


@router.websocket("/ws/results/{task_id}")
async def websocket_results(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for streaming results."""
    from backend.middleware.auth import get_websocket_user
    
    # Authenticate WebSocket connection
    try:
        current_user = await get_websocket_user(websocket)
        if not current_user:
            await websocket.close(code=1008, reason="Authentication required")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))
        return
    
    await websocket.accept()
    
    # Register WebSocket connection
    task_manager.register_websocket(task_id, "results", websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Connected to results stream for task {task_id}"
        }))
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except Exception as ws_error:
            import logging
            logging.warning(f"Failed to send error message to WebSocket: {ws_error}")
    finally:
        task_manager.unregister_websocket(task_id, "results", websocket)


@router.get("/phone-coordinates/{task_id}")
async def get_phone_coordinates(task_id: str, selector: str):
    """
    Get phone element coordinates for highlighting.
    
    Args:
        task_id: Task ID
        selector: CSS selector for the phone element
        
    Returns:
        Coordinates normalized to 0-1 range
    """
    try:
        driver = stream_service.get_driver(task_id)
        if not driver:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found or driver not available")
        
        port = stream_service.get_port(task_id)
        if not port:
            raise HTTPException(status_code=404, detail=f"Debug port not available for task {task_id}")
        
        from backend.services.chrome_cdp import ChromeCDPService
        cdp_service = ChromeCDPService(driver, port)
        
        coordinates = cdp_service.get_element_bounding_box(selector)
        if not coordinates:
            raise HTTPException(status_code=404, detail=f"Element not found: {selector}")
        
        return {
            "task_id": task_id,
            "selector": selector,
            "coordinates": coordinates
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live_feed/{task_id}")
async def live_feed(task_id: str):
    """MJPEG stream endpoint for live browser view."""
    from backend.config import STREAM_FPS
    from PIL import Image
    import io
    
    async def generate():
        """Generate MJPEG stream with proper headers and optimization."""
        boundary = b"frame"
        interval = 1.0 / STREAM_FPS
        
        while True:
            try:
                screenshot_path = stream_service.get_latest_screenshot(task_id)
                if screenshot_path and os.path.exists(screenshot_path):
                    try:
                        # Optimize image: convert PNG to JPEG for better compression
                        img = Image.open(screenshot_path)
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format="JPEG", quality=85, optimize=True)
                        frame_data = img_buffer.getvalue()
                        
                        # Send frame with proper MJPEG format
                        yield (b"--" + boundary + b"\r\n"
                               b"Content-Type: image/jpeg\r\n"
                               b"Content-Length: " + str(len(frame_data)).encode() + b"\r\n\r\n" +
                               frame_data + b"\r\n")
                    except Exception:
                        # Fallback: send raw file if image processing fails
                        try:
                            with open(screenshot_path, 'rb') as f:
                                frame_data = f.read()
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/png\r\n'
                                       b'Content-Length: ' + str(len(frame_data)).encode() + b'\r\n\r\n' +
                                       frame_data + b'\r\n')
                        except Exception as e:
                            import logging
                            logging.warning(f"Failed to send fallback screenshot: {e}")
                
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception:
                # Continue on error
                await asyncio.sleep(interval)
    
    return StreamingResponse(
        generate(),
        media_type='multipart/x-mixed-replace; boundary=frame',
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

