from sqlalchemy.orm import Session
from ..models.audit_log import AuditLog
from fastapi import Request

async def log_audit_event(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: str = None,
    changes: dict = None,
    request: Request = None
):
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        changes=changes,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(log_entry)
    db.commit()
    return log_entry