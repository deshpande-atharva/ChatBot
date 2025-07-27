from typing import Dict, Set
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Dictionary mapping session_id to set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept WebSocket connection and add to active connections"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        """Remove WebSocket from active connections"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            # Clean up empty session entries
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        await websocket.send_text(message)

    async def broadcast(self, session_id: str, message: dict):
        """Broadcast message to all connections for a session"""
        if session_id in self.active_connections:
            message_text = json.dumps(message)
            
            # Create a list to track connections to remove
            dead_connections = []
            
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message_text)
                except Exception as e:
                    # Connection is dead, mark for removal
                    print(f"Error sending to websocket: {e}")
                    dead_connections.append(connection)
            
            # Remove dead connections
            for connection in dead_connections:
                self.disconnect(session_id, connection)

    async def disconnect_all(self):
        """Disconnect all active connections (for shutdown)"""
        for session_id in list(self.active_connections.keys()):
            for connection in list(self.active_connections[session_id]):
                try:
                    await connection.close()
                except:
                    pass
            del self.active_connections[session_id]