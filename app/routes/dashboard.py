from fastapi import APIRouter
from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()

@router.get("/calls")
def get_calls():
    db = SessionLocal()
    calls = db.query(Call).order_by(Call.id.desc()).all()
    db.close()
    return [
        {
            "id":            c.id,
            "call_id":       c.call_id,
            "customer_name": c.customer_name,
            "phone_number":  c.phone_number,
            "duration":      round(c.duration / 60, 1) if c.duration else 0,
            "transcript":    c.transcript,
            "status":        c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in calls
    ]

@router.get("/analytics")
def get_analytics():
    db = SessionLocal()
    calls = db.query(Call).all()
    db.close()
    total_calls    = len(calls)
    total_seconds  = sum(c.duration or 0 for c in calls)
    total_minutes  = round(total_seconds / 60, 1) if total_seconds else 0
    return {
        "total_calls":   total_calls,
        "total_minutes": total_minutes,
    }