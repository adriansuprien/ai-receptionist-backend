from fastapi import APIRouter, Request
from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()

@router.post("/retell-webhook")
async def retell_webhook(request: Request):
    data = await request.json()

    print("🔥 INCOMING WEBHOOK:", data)

    event = data.get("event")
    call_data = data.get("call", {})

    # 🚨 ONLY SAVE WHEN CALL ENDS
    if event != "call_ended":
        return {"status": "ignored"}

    call_id = call_data.get("call_id")
    phone = call_data.get("from_number")
    duration = call_data.get("total_duration_seconds", 0)
    transcript = call_data.get("transcript", "")
    status = call_data.get("call_status", "completed")

    db = SessionLocal()

    call = Call(
        call_id=call_id,
        customer_name=None,
        phone_number=phone,
        duration=duration,
        transcript=transcript,
        status=status
    )

    db.add(call)
    db.commit()
    db.close()

    return {"status": "saved"}