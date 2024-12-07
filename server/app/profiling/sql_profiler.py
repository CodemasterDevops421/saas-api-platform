from sqlalchemy import event
from sqlalchemy.engine import Engine
from time import time
from ..monitoring.logger import logger

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time() - conn.info['query_start_time'].pop(-1)
    
    if total > 0.1:  # Log slow queries (>100ms)
        logger.warning(
            "Slow SQL Query: %s\nParameters: %s\nDuration: %.3f seconds",
            statement, parameters, total
        )