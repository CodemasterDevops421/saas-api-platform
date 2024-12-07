from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websockets.monitor import PerformanceMonitor

router = APIRouter()
monitor = PerformanceMonitor()

@router.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await monitor.connect(websocket)
    try:
        await monitor.broadcast_metrics()
    except WebSocketDisconnect:
        monitor.disconnect(websocket)