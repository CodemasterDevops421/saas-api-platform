from .worker import app
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..services.analytics_service import AnalyticsService
from datetime import datetime

@app.task
def generate_daily_reports():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            stats = AnalyticsService.get_daily_stats(db, user.id)
            
            if stats['total_requests'] > 0:
                EmailService.send_daily_report(
                    email=user.email,
                    stats=stats
                )
    finally:
        db.close()

@app.task
def cleanup_old_analytics_data():
    db = SessionLocal()
    try:
        # Keep last 90 days of detailed data
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        AnalyticsService.cleanup_old_data(db, cutoff_date)
    finally:
        db.close()