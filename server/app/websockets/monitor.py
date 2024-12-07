from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import psutil
import json

class PerformanceMonitor:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.sampling_rate = 1  # seconds
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast_metrics(self):
        while True:
            metrics = {
                'cpu': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'network': self._get_network_stats(),
                'requests': self._get_request_stats()
            }
            
            for connection in self.active_connections:
                try:
                    await connection.send_json(metrics)
                except WebSocketDisconnect:
                    self.disconnect(connection)
            
            await asyncio.sleep(self.sampling_rate)
    
    def _get_network_stats(self):
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    def _get_request_stats(self):
        # Get from Redis or in-memory counter
        return {
            'total': 0,
            'success': 0,
            'error': 0,
            'latency': 0
        }