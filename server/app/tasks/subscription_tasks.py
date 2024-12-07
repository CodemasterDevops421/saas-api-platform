from .worker import app
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..services.subscription_service import SubscriptionService
from ..services.email_service import EmailService
from datetime import datetime, timedelta

@app.task
def check_subscription_renewals():
    db = SessionLocal()
    try:
        upcoming_renewals = SubscriptionService.get_upcoming_renewals(
            db,
            days_threshold=3
        )
        
        for subscription in upcoming_renewals:
            EmailService.send_renewal_reminder(
                email=subscription.user.email,
                subscription=subscription
            )
    finally:
        db.close()

@app.task
def process_failed_payments():
    db = SessionLocal()
    try:
        failed_payments = SubscriptionService.get_failed_payments(db)
        
        for payment in failed_payments:
            EmailService.send_payment_failed_notification(
                email=payment.subscription.user.email,
                payment=payment
            )
    finally:
        db.close()