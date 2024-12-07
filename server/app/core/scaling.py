from dataclasses import dataclass
from typing import List, Dict
import aiohttp
import asyncio

@dataclass
class ScalingMetrics:
    cpu_usage: float
    memory_usage: float
    request_rate: float
    error_rate: float

class AutoScaler:
    def __init__(self, metrics_url: str):
        self.metrics_url = metrics_url
        self.thresholds = {
            'cpu': 70,
            'memory': 80,
            'requests': 1000,
            'errors': 1
        }

    async def get_scaling_recommendation(self) -> Dict:
        metrics = await self._collect_metrics()
        return {
            'scale_up': self._should_scale_up(metrics),
            'scale_down': self._should_scale_down(metrics),
            'target_replicas': self._calculate_target_replicas(metrics)
        }

    def _should_scale_up(self, metrics: ScalingMetrics) -> bool:
        return (
            metrics.cpu_usage > self.thresholds['cpu'] or
            metrics.memory_usage > self.thresholds['memory'] or
            metrics.request_rate > self.thresholds['requests']
        )

    def _should_scale_down(self, metrics: ScalingMetrics) -> bool:
        return (
            metrics.cpu_usage < self.thresholds['cpu'] * 0.5 and
            metrics.memory_usage < self.thresholds['memory'] * 0.5 and
            metrics.request_rate < self.thresholds['requests'] * 0.5
        )

    def _calculate_target_replicas(self, metrics: ScalingMetrics) -> int:
        cpu_replicas = int(metrics.cpu_usage / self.thresholds['cpu'] * 10)
        mem_replicas = int(metrics.memory_usage / self.thresholds['memory'] * 10)
        req_replicas = int(metrics.request_rate / self.thresholds['requests'] * 10)
        
        return max(min(max(cpu_replicas, mem_replicas, req_replicas), 50), 5)