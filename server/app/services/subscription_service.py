from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from ..models.user import User
from ..core.exceptions import SubscriptionError
from .stripe_service import StripeService

class SubscriptionService:
    @staticmethod
    async def create_subscription(
        db: Session,
        user_id: int,
        tier: SubscriptionTier,
        payment_method_id: str
    ) -> Subscription:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise SubscriptionError("User not found")

        # Check for existing subscription
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if existing_sub:
            raise SubscriptionError("Active subscription already exists")

        try:
            # Create Stripe subscription
            stripe_sub = await StripeService.create_subscription(
                db=db,
                user_id=user_id,
                tier=tier,
                payment_method_id=payment_method_id
            )

            # Create subscription record
            subscription = Subscription(
                user_id=user_id,
                stripe_subscription_id=stripe_sub["id"],
                tier=tier,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=stripe_sub["current_period_start"],
                current_period_end=stripe_sub["current_period_end"],
                plan_data=stripe_sub["plan"]
            )

            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return subscription

        except Exception as e:
            raise SubscriptionError(str(e))

    @staticmethod
    async def cancel_subscription(db: Session, user_id: int) -> bool:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()

        if not subscription:
            raise SubscriptionError("No active subscription found")

        try:
            # Cancel in Stripe
            await StripeService.cancel_subscription(subscription.stripe_subscription_id)

            # Update local record
            subscription.status = SubscriptionStatus.CANCELED
            subscription.cancel_at_period_end = True
            db.commit()
            return True

        except Exception as e:
            raise SubscriptionError(f"Failed to cancel subscription: {str(e)}")

    @staticmethod
    def get_subscription_features(tier: SubscriptionTier) -> dict:
        features = {
            SubscriptionTier.FREE: {
                "api_calls_limit": 1000,
                "rate_limit": 10
            },
            SubscriptionTier.BASIC: {
                "api_calls_limit": 10000,
                "rate_limit": 50
            },
            SubscriptionTier.PRO: {
                "api_calls_limit": 100000,
                "rate_limit": 200
            },
            SubscriptionTier.ENTERPRISE: {
                "api_calls_limit": float('inf'),
                "rate_limit": 1000
            }
        }
        return features.get(tier, features[SubscriptionTier.FREE])