from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Any
import json
import logging
from uuid import UUID
from database import get_db
from auth import verify_token
from models import User
from middleware.ownership import ResourceAccess
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websockets"])

class ConnectionManager:
    """Manages active WebSocket connections for live coaching."""
    def __init__(self):
        # session_id -> list of websockets (patient and observing doctors)
        self.active_sessions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        self.active_sessions[session_id].append(websocket)
        logger.info(f"WebSocket connected to session {session_id}. Total: {len(self.active_sessions[session_id])}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_sessions:
            self.active_sessions[session_id].remove(websocket)
            if not self.active_sessions[session_id]:
                self.active_sessions.pop(session_id, None)
        logger.info(f"WebSocket disconnected from session {session_id}")

    async def broadcast_to_session(self, session_id: str, message: Any):
        if session_id in self.active_sessions:
            # Send message to all connected clients in this session
            for connection in self.active_sessions[session_id]:
                try:
                    if isinstance(message, dict):
                        await connection.send_json(message)
                    else:
                        await connection.send_text(str(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {e}")

manager = ConnectionManager()

@router.websocket("/ws/session/{session_id}")
async def session_websocket(
    websocket: WebSocket, 
    session_id: str, 
    token: str = None,
    db: Session = Depends(get_db)
):
    # 1. JWT Handshake: Authenticate user from token (query param)
    if not token:
        await websocket.close(code=4001) # Unauthorized
        return

    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001) # Invalid token
        return

    user_id = payload.get("sub")
    current_user = db.query(User).filter(User.user_id == UUID(user_id)).first()
    if not current_user:
        await websocket.close(code=4001)
        return

    # 2. Session Isolation & Resource Guards
    try:
        session_uuid = UUID(session_id)
        # Verify that this user (patient or doctor) has access to the session
        await ResourceAccess.session(session_uuid, current_user, db)
    except Exception as e:
        logger.error(f"WebSocket Access Denied: {e}")
        await websocket.close(code=4003) # Forbidden
        return

    await manager.connect(websocket, session_id)
    try:
        while True:
            # Receive data from patient (e.g., live reps, feedback)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Broadcast to all observers (doctors) in the same session
            await manager.broadcast_to_session(session_id, {
                "type": "live_update",
                "session_id": session_id,
                "data": message
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)
