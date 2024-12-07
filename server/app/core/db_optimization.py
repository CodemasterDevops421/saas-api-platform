from sqlalchemy import event, text
from sqlalchemy.orm import Session
from typing import List, Dict

class QueryOptimizer:
    def __init__(self, session: Session):
        self.session = session
        self.query_cache = {}

    def analyze_table_stats(self, table_name: str) -> Dict:
        result = self.session.execute(text(f"""
            SELECT
                schemaname,
                relname,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_analyze
            FROM pg_stat_all_tables
            WHERE relname = :table_name
        """), {'table_name': table_name})
        
        return dict(result.first() or {})

    def suggest_indexes(self, table_name: str) -> List[str]:
        result = self.session.execute(text(f"""
            SELECT
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats
            WHERE tablename = :table_name
            AND correlation < 0.5
            AND n_distinct > 100
        """), {'table_name': table_name})
        
        suggestions = []
        for row in result:
            if row.correlation < 0.3:
                suggestions.append(f"CREATE INDEX idx_{table_name}_{row.attname} ON {table_name}({row.attname});")
        
        return suggestions

    def optimize_query_plan(self, query):
        # Get query execution plan
        plan = self.session.execute(text(f"EXPLAIN ANALYZE {query}")).fetchall()
        
        # Analyze plan and suggest optimizations
        suggestions = []
        for line in plan:
            if 'Seq Scan' in line[0]:
                suggestions.append("Consider adding an index to avoid sequential scan")
            elif 'Hash Join' in line[0] and 'cost=' in line[0]:
                cost = float(line[0].split('cost=')[1].split('..')[1].split()[0])
                if cost > 1000:
                    suggestions.append("Consider denormalization or materialized view")
        
        return suggestions

    def vacuum_analyze(self, table_name: str):
        self.session.execute(text(f"VACUUM ANALYZE {table_name}"))

    def create_materialized_view(self, name: str, query: str):
        self.session.execute(text(f"""
            CREATE MATERIALIZED VIEW {name} AS
            {query}
            WITH DATA
        """))

    def refresh_materialized_view(self, name: str):
        self.session.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {name}"))