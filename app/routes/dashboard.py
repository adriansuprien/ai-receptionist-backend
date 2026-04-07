from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pytz
import re
from app.db.database import SessionLocal
from app.models.call import Call
from app.models.settings import Settings as SettingsModel

eastern = pytz.timezone("US/Eastern")

router = APIRouter()


def to_eastern(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(eastern).isoformat()


def extract_name_from_summary(order_summary: str) -> str:
    if not order_summary:
        return ""
    match = re.search(r"(?:Customer Name|Customer)\s*:\s*(.+)", order_summary, re.IGNORECASE)
    if match:
        return match.group(1).split("\n")[0].strip()
    return ""

class SettingsSchema(BaseModel):
    restaurantName: str = ""
    phoneNumber: str = ""
    openingHours: str = ""
    greeting: str = ""
    forwardNumber: str = ""
    openTime: str = "09:00"
    closeTime: str = "17:00"
    takeOrders: str = "true"
    bookAppointments: str = "false"


@router.get("/calls")
def get_calls():
    db = SessionLocal()
    calls = db.query(Call).order_by(Call.id.desc()).all()
    db.close()
    return [
        {
            "id":            c.id,
            "call_id":       c.call_id,
            "customer_name": c.customer_name or extract_name_from_summary(c.order_summary),
            "phone_number":  c.phone_number,
            "duration":      round(c.duration / 60, 1) if c.duration else 0,
            "transcript":    c.transcript,
            "status":        c.status,
            "order_summary": c.order_summary,
            "order_status":  c.order_status or "new",
            "created_at":    to_eastern(c.created_at),
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
    db = SessionLocal()
    try:
        row = db.query(SettingsModel).filter(SettingsModel.id == 1).first()
        if not row:
            return SettingsSchema().model_dump()
        return SettingsSchema(
            restaurantName=row.restaurantName or "",
            phoneNumber=row.phoneNumber or "",
            openingHours=row.openingHours or "",
            greeting=row.greeting or "",
            forwardNumber=row.forwardNumber or "",
            openTime=row.openTime or "09:00",
            closeTime=row.closeTime or "17:00",
            takeOrders=row.takeOrders or "true",
            bookAppointments=row.bookAppointments or "false",
        ).model_dump()
    finally:
        db.close()


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
def save_settings(settings: SettingsSchema):
    db = SessionLocal()
    try:
        row = db.query(SettingsModel).filter(SettingsModel.id == 1).first()
        if not row:
            row = SettingsModel(id=1)
            db.add(row)
        for key, val in settings.model_dump().items():
            setattr(row, key, val)
        db.commit()
        return {"message": "Settings saved", "settings": settings.model_dump()}
    finally:
        db.close()
