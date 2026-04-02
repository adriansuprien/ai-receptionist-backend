from fastapi import APIRouter
from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()

@router.get("/calls")
def get_calls():
    db = SessionLocal()
    calls = db.query(Call).all()
    db.close()

    return calls


@router.get("/analytics")
def get_analytics():
    db = SessionLocal()

    total_calls = db.query(Call).count()
    total_duration = sum([c.duration or 0 for c in db.query(Call).all()])

    db.close()

    return {
        "total_calls": total_calls,
        "total_minutes": total_duration / 60 if total_duration else 0
    }