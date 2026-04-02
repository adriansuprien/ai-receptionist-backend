from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()

@router.api_route("/retell-webhook", methods=["GET", "POST"])
async def retell_webhook(request: Request):
    print("🔥 WEBHOOK HIT")

    try:
        data = await request.json()
    except:
        data = {}

    print("🔥 DATA:", data)

    event = data.get("event")
    call_data = data.get("call", {})

      

    call_id = call_data.get("call_id")
    phone = call_data.get("from_number")
    duration = call_data.get("total_duration_seconds", 0)
    transcript = call_data.get("transcript", "")
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Extract order info from the transcript. Return JSON with: item, quantity, pickup_time."
        },
        {
            "role": "user",
            "content": transcript
        }
    ]
)

    from openai import OpenAI
client = OpenAI(api_key="PASTE_NEW_KEY_HERE")

from fastapi import APIRouter, Request
from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()

@router.api_route("/retell-webhook", methods=["GET", "POST"])
async def retell_webhook(request: Request):
    print("🔥 WEBHOOK HIT")

    try:
        data = await request.json()
    except:
        data = {}

    print("🔥 DATA:", data)

    event = data.get("event")
    call_data = data.get("call", {})

    call_id = call_data.get("call_id")
    phone = call_data.get("from_number")
    duration = call_data.get("total_duration_seconds", 0)
    transcript = call_data.get("transcript", "")

    # ✅ OPENAI CALL (fixed indent)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract order info from the transcript. Return JSON with: item, quantity, pickup_time."
            },
            {
                "role": "user",
                "content": transcript
            }
        ]
    )

    print("🧠 AI OUTPUT:", response.choices[0].message.content)

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