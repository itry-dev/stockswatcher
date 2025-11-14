from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
import json


class WSManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def broadcast(self, payload: dict):
        message = json.dumps(payload, default=str)
        stale = []
        for ws in list(self.active):
            try:
                await ws.send_text(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)