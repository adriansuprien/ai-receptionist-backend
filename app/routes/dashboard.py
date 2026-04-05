from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pytz
from app.db.database import SessionLocal
from app.models.call import Call

eastern = pytz.timezone("US/Eastern")

router = APIRouter()

# In-memory settings store (replace with DB-backed if needed)
_settings = {
    "restaurantName": "Punjab Halal Meat & Grill",
    "phoneNumber": "",
    "openingHours": "",
    "greeting": "",
}


class Settings(BaseModel):
    restaurantName: str = ""
    phoneNumber: str = ""
    openingHours: str = ""
    greeting: str = ""


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
            "order_summary": c.order_summary,
            "order_status":  c.order_status,
            "created_at":    pytz.utc.localize(c.created_at).astimezone(eastern).isoformat() if c.created_at else None,
        }
        for c in calls
    ]


@router.get("/analytics")
def get_analytics():
    db = SessionLocal()
    calls = db.query(Call).all()
    db.close()
    total_calls   = len(calls)
    total_seconds = sum(c.duration or 0 for c in calls)
    total_minutes = round(total_seconds / 60, 1) if total_seconds else 0
    return {
        "total_calls":   total_calls,
        "total_minutes": total_minutes,
    }


@router.get("/settings")
def get_settings():
    return _settings


class OrderStatusUpdate(BaseModel):
    status: str


@router.patch("/calls/{call_id}/status")
def update_order_status(call_id: int, body: OrderStatusUpdate):
    if body.status not in ("new", "completed"):
        raise HTTPException(status_code=400, detail="status must be 'new' or 'completed'")
    db = SessionLocal()
    try:
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        call.order_status = body.status
        db.commit()
        return {"id": call_id, "order_status": call.order_status}
    finally:
        db.close()


@router.post("/settings")
def save_settings(settings: Settings):
    _settings.update(settings.model_dump())
    return {"message": "Settings saved", "settings": _settings}
