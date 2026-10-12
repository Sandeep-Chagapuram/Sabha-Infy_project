from typing import Dict, List, Any
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active WebSockets for live meeting transcript events and notifications."""

    def __init__(self):
        # room_name -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_name: str):
        await websocket.accept()
        if room_name not in self.active_connections:
            self.active_connections[room_name] = []
        self.active_connections[room_name].append(websocket)

    def disconnect(self, websocket: WebSocket, room_name: str):
        if room_name in self.active_connections:
            if websocket in self.active_connections[room_name]:
                self.active_connections[room_name].remove(websocket)
            if not self.active_connections[room_name]:
                del self.active_connections[room_name]

    async def broadcast_to_room(self, room_name: str, message: Dict[str, Any]):
        if room_name in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[room_name]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Failed to send to websocket: {e}")
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(dead, room_name)

ws_manager = ConnectionManager()
