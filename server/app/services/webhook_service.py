import hmac
import hashlib
import json
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx
from ..models.webhook import Webhook
from ..core.config import settings
from .audit_service import AuditService

class WebhookService:
    @staticmethod
    async def create_webhook(db: Session, user_id: int, url: str, events: List[str]) -> Webhook:
        # Generate webhook secret
        secret = secrets.token_hex(32)
        
        webhook = Webhook(
            user_id=user_id,
            url=url,
            events=events,
            secret=secret
        )
        
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook

    @staticmethod
    def generate_signature(payload: dict, secret: str) -> str:
        return hmac.new(
            secret.encode('utf-8'),
            json.dumps(payload).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def trigger_webhook(webhook: Webhook, event: str, payload: dict):
        if event not in webhook.events:
            return

        signature = WebhookService.generate_signature(payload, webhook.secret)
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Event-Type': event
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()

        except Exception as e:
            # Log failed webhook attempt
            AuditService.log_webhook_failure(
                webhook_id=webhook.id,
                event=event,
                error=str(e)
            )
            raise

    @staticmethod
    async def trigger_webhooks_for_user(db: Session, user_id: int, event: str, payload: dict):
        webhooks = db.query(Webhook).filter(
            Webhook.user_id == user_id,
            Webhook.is_active == True
        ).all()

        for webhook in webhooks:
            try:
                await WebhookService.trigger_webhook(webhook, event, payload)
            except Exception:
                # Continue with other webhooks even if one fails
                continue