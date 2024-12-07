import psutil
import time
from datetime import datetime
import redis
import json

class ResourceMonitor:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.metrics_key = 'system:metrics'
        self.retention_hours = 24

    def collect_metrics(self):
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'load': psutil.getloadavg()
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'connections': len(psutil.net_connections()),
                'io': psutil.net_io_counters()._asdict()
            }
        }
        
        # Store in Redis with expiration
        self.redis_client.setex(
            f"{self.metrics_key}:{int(time.time())}",
            60 * 60 * self.retention_hours,
            json.dumps(metrics)
        )

    def get_metrics(self, minutes=5):
        now = int(time.time())
        start_time = now - (minutes * 60)
        
        keys = self.redis_client.keys(f"{self.metrics_key}:*")
        metrics = []
        
        for key in keys:
            timestamp = int(key.split(':')[-1])
            if timestamp >= start_time:
                data = json.loads(self.redis_client.get(key))
                metrics.append(data)
        
        return sorted(metrics, key=lambda x: x['timestamp'])

    def get_alerts(self):
        metrics = self.get_metrics(minutes=5)
        if not metrics:
            return []
        
        alerts = []
        latest = metrics[-1]
        
        # CPU Usage Alert
        if latest['cpu']['percent'] > 80:
            alerts.append({
                'level': 'critical',
                'message': f"High CPU usage: {latest['cpu']['percent']}%"
            })
        
        # Memory Alert
        if latest['memory']['percent'] > 85:
            alerts.append({
                'level': 'critical',
                'message': f"High memory usage: {latest['memory']['percent']}%"
            })
        
        # Disk Space Alert
        if latest['disk']['percent'] > 90:
            alerts.append({
                'level': 'critical',
                'message': f"Low disk space: {latest['disk']['percent']}% used"
            })
        
        return alerts

if __name__ == '__main__':
    monitor = ResourceMonitor()
    while True:
        monitor.collect_metrics()
        alerts = monitor.get_alerts()
        if alerts:
            print(f"Alerts: {alerts}")
        time.sleep(60)