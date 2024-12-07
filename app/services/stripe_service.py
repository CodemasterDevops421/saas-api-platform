import stripe
from fastapi import HTTPException
from ..config import settings
from .. import models
from sqlalchemy.orm import Session
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    async def create_customer(email: str) -> stripe.Customer:
        try:
            return stripe.Customer.create(email=email)
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def create_subscription(customer_id: str, price_id: str):
        try:
            return stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str):
        try:
            return stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))