import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models.subscription import Subscription
from ..models.user import User
from .cache_service import cache

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    async def create_subscription(db: Session, user_id: int, price_id: str):
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create or get Stripe customer
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={"user_id": user_id}
                )
                user.stripe_customer_id = customer.id
                db.commit()

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )

            # Update database
            db_sub = Subscription(
                user_id=user_id,
                stripe_subscription_id=subscription.id,
                status=subscription.status,
                price_id=price_id
            )
            db.add(db_sub)
            db.commit()

            return {
                "subscriptionId": subscription.id,
                "clientSecret": subscription.latest_invoice.payment_intent.client_secret
            }

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    @cache(ttl_seconds=3600)
    async def get_subscription_details(subscription_id: str):
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))