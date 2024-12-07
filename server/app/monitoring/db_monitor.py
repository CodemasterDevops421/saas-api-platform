from sqlalchemy import event, create_engine
from sqlalchemy.engine import Engine
from prometheus_client import Histogram, Counter
import time
import json
from threading import Lock

class DBMonitor:
    def __init__(self):
        self.query_times = Histogram(
            'db_query_duration_seconds',
            'Database query duration',
            ['query_type', 'table']
        )
        self.slow_queries = Counter(
            'db_slow_queries_total',
            'Total slow queries',
            ['query_type']
        )
        self._query_stats = {}
        self._lock = Lock()

    def start_monitoring(self, engine):
        @event.listens_for(engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - conn.info['query_start_time'].pop(-1)
            
            query_type = statement.split()[0].upper()
            table = self._extract_table(statement)
            
            self.query_times.labels(query_type=query_type, table=table).observe(total_time)
            
            if total_time > 1.0:  # Slow query threshold
                self.slow_queries.labels(query_type=query_type).inc()
                self._record_slow_query(statement, parameters, total_time)

    def _extract_table(self, query):
        # Simple table name extraction
        words = query.split()
        for i, word in enumerate(words):
            if word.upper() in ['FROM', 'INTO', 'UPDATE']:
                if i + 1 < len(words):
                    return words[i + 1].strip('"')
        return 'unknown'

    def _record_slow_query(self, query, params, duration):
        with self._lock:
            query_info = {
                'query': query,
                'parameters': str(params),
                'duration': duration,
                'timestamp': time.time()
            }
            self._query_stats.setdefault('slow_queries', []).append(query_info)
            
            # Keep only last 100 slow queries
            if len(self._query_stats['slow_queries']) > 100:
                self._query_stats['slow_queries'].pop(0)

    def get_query_stats(self):
        with self._lock:
            return json.dumps(self._query_stats)