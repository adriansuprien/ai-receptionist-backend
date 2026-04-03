from fastapi import APIRouter, Request
from openai import OpenAI
import os

from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_order_summary(transcript: str) -> str:
    if not transcript:
        return ""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for Punjab Halal Meat & Grill. "
                        "Extract a concise order summary from the call transcript. "
                        "Include: items ordered, quantities, any special requests, and customer name if mentioned. "
                        "If no order was placed, summarize the purpose of the call in one sentence."
                    ),
                },
                {"role": "user", "content": transcript},
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return ""


@router.post("/webhook")
async def webhook(request: Request):
    print("🔥 WEBHOOK HIT")

    try:
        data = await request.json()
    except Exception:
        data = {}

    print("🔥 DATA:", data)

    # VAPI payload fields
    transcript    = data.get("text", "") or data.get("transcript", "")
    call_id       = data.get("call", {}).get("id", "") if isinstance(data.get("call"), dict) else data.get("call_id", "")
    phone_number  = data.get("call", {}).get("customer", {}).get("number", "") if isinstance(data.get("call"), dict) else data.get("phone_number", "")
    customer_name = data.get("call", {}).get("customer", {}).get("name", "") if isinstance(data.get("call"), dict) else data.get("customer_name", "")
    duration      = data.get("call", {}).get("duration", 0) if isinstance(data.get("call"), dict) else data.get("duration", 0)
    status        = data.get("call", {}).get("status", "completed") if isinstance(data.get("call"), dict) else data.get("status", "completed")

    order_summary = extract_order_summary(transcript)

    db = SessionLocal()
    try:
        call = Call(
            call_id=call_id,
            customer_name=customer_name,
            phone_number=phone_number,
            duration=duration,
            transcript=transcript,
            status=status,
            order_summary=order_summary,
        )
        db.add(call)
        db.commit()
        print(f"✅ Call saved: {call_id}, order: {order_summary}")
    except Exception as e:
        db.rollback()
        print(f"❌ DB error: {e}")
    finally:
        db.close()

    return {"response": "Thank you for calling Punjab Halal Meat & Grill. Your order has been received!"}
