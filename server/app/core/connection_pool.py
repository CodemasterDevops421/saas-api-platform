from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from redis import ConnectionPool
from typing import Dict

class ConnectionPoolManager:
    def __init__(self, config: Dict):
        self.db_pool = self._create_db_pool(config['database'])
        self.redis_pool = self._create_redis_pool(config['redis'])
        self.metrics = {
            'db_connections': 0,
            'redis_connections': 0
        }
    
    def _create_db_pool(self, config: Dict):
        return create_engine(
            config['url'],
            poolclass=QueuePool,
            pool_size=config.get('pool_size', 20),
            max_overflow=config.get('max_overflow', 10),
            pool_timeout=config.get('timeout', 30),
            pool_recycle=config.get('recycle', 3600),
            pool_pre_ping=True
        )
    
    def _create_redis_pool(self, config: Dict):
        return ConnectionPool(
            host=config['host'],
            port=config['port'],
            max_connections=config.get('max_connections', 50),
            socket_timeout=config.get('timeout', 5),
            socket_connect_timeout=config.get('connect_timeout', 5)
        )
    
    def get_db_session(self):
        Session = sessionmaker(bind=self.db_pool)
        self.metrics['db_connections'] += 1
        return Session()
    
    def get_redis_connection(self):
        self.metrics['redis_connections'] += 1
        return self.redis_pool.get_connection()
    
    def get_metrics(self):
        return {
            'db_pool': {
                'size': self.db_pool.size(),
                'checkedin': self.db_pool.checkedin(),
                'overflow': self.db_pool.overflow(),
                'checkedout': self.db_pool.checkedout()
            },
            'redis_pool': {
                'connections': self.metrics['redis_connections']
            }
        }