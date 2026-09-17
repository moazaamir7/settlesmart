from collections import defaultdict

from fastapi import WebSocket

from app.schemas.group import GroupMessageRead


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, group_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[group_id].add(websocket)

    def disconnect(self, group_id: str, websocket: WebSocket) -> None:
        self.connections[group_id].discard(websocket)
        if not self.connections[group_id]:
            self.connections.pop(group_id, None)

    async def broadcast_message(self, group_id: str, message: GroupMessageRead) -> None:
        payload = {"type": "message.created", "message": message.model_dump(mode="json")}
        stale: list[WebSocket] = []
        for websocket in self.connections.get(group_id, set()).copy():
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(group_id, websocket)


realtime_manager = ConnectionManager()
