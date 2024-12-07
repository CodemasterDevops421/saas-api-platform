from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .... import models, schemas, crud
from ....database import get_db
from ....services.stripe_service import StripeService
from datetime import datetime

router = APIRouter()

@router.post("/create-subscription")
async def create_subscription(
    plan_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = crud.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    if not user.stripe_customer_id:
        customer = await StripeService.create_customer(user.email)
        user.stripe_customer_id = customer.id
        db.commit()
    
    subscription = await StripeService.create_subscription(
        user.stripe_customer_id,
        plan.stripe_price_id
    )
    
    db_subscription = models.Subscription(
        user_id=user.id,
        plan_id=plan_id,
        stripe_subscription_id=subscription.id,
        stripe_customer_id=user.stripe_customer_id,
        status=subscription.status,
        current_period_start=datetime.fromtimestamp(subscription.current_period_start),
        current_period_end=datetime.fromtimestamp(subscription.current_period_end)
    )
    
    db.add(db_subscription)
    db.commit()
    
    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
        "client_secret": subscription.latest_invoice.payment_intent.client_secret
    }

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = StripeService.construct_webhook_event(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if event.type == "customer.subscription.created":
        await StripeService.handle_subscription_created(db, event.data.object)
    elif event.type == "customer.subscription.updated":
        await StripeService.handle_subscription_updated(db, event.data.object)
    
    return {"status": "processed"}