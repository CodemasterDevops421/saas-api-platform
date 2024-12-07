import psutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class TaskMetrics:
    task_id: str
    name: str
    state: str
    runtime: float
    memory_used: int
    cpu_percent: float
    timestamp: datetime

class TaskMonitor:
    def __init__(self):
        self.metrics: List[TaskMetrics] = []
        self.process = psutil.Process()
    
    def record_metrics(self, task_id: str, name: str, state: str) -> None:
        metrics = TaskMetrics(
            task_id=task_id,
            name=name,
            state=state,
            runtime=self.process.cpu_times().user,
            memory_used=self.process.memory_info().rss,
            cpu_percent=self.process.cpu_percent(),
            timestamp=datetime.now()
        )
        self.metrics.append(metrics)
        
        # Keep last 1000 metrics
        if len(self.metrics) > 1000:
            self.metrics.pop(0)
    
    def get_task_stats(self) -> Dict:
        return {
            'total_tasks': len(self.metrics),
            'avg_runtime': sum(m.runtime for m in self.metrics) / len(self.metrics),
            'avg_memory': sum(m.memory_used for m in self.metrics) / len(self.metrics),
            'avg_cpu': sum(m.cpu_percent for m in self.metrics) / len(self.metrics),
            'states': {
                state: len([m for m in self.metrics if m.state == state])
                for state in set(m.state for m in self.metrics)
            }
        }