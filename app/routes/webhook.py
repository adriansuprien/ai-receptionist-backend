from fastapi import APIRouter, Request
import anthropic
import re
import os

from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

FOOD_KEYWORDS = [
    "chicken", "lamb", "beef", "rice", "gyro", "platter", "combo",
    "falafel", "shawarma", "burger", "wrap", "kebab", "naan", "biryani",
]


def is_food_order(summary: str) -> bool:
    if not summary:
        return False
    text = summary.lower()
    has_food = any(kw in text for kw in FOOD_KEYWORDS)
    has_confirmation = "order confirmed:** yes" in text or "order confirmed: yes" in text
    return has_food and has_confirmation


def extract_order_summary(transcript: str) -> str:
    if not transcript:
        return ""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=(
                "You are a data extraction assistant for Punjab Halal Meat & Grill. "
                "Analyze the call transcript and respond in this exact format:\n\n"
                "**ORDER SUMMARY**\n\n"
                "**Items Ordered:** [list items and quantities, or 'None']\n"
                "**Customer Name:** [name or 'Not provided']\n"
                "**Phone Number:** [number or 'Not provided']\n"
                "**Special Requests:** [or 'None mentioned']\n"
                "**Pickup Time:** [time or 'Not specified']\n"
                "**Order Confirmed:** [YES or NO]\n"
                "**Call Purpose:** [one sentence description]\n\n"
                "Only mark Order Confirmed as YES if the customer explicitly confirmed or agreed to place the order."
            ),
            messages=[
                {"role": "user", "content": transcript},
            ],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Anthropic error: {e}")
        return ""


@router.post("/webhook")
async def webhook(request: Request):
    print("🔥 WEBHOOK HIT")

    try:
        data = await request.json()
    except Exception:
        data = {}

    message = data.get("message", {})
    message_type = message.get("type", "")

    if message_type != "end-of-call-report":
        print(f"⏭️ Ignoring event type: {message_type}")
        return {"response": "ok"}

    transcript    = message.get("transcript", "")
    duration      = message.get("durationSeconds", 0)
    call_id       = message.get("call", {}).get("id", "")
    phone_number  = message.get("call", {}).get("customer", {}).get("number", "")
    phone_number  = "".join(c for c in phone_number if c.isdigit() or c == "+")
    customer_name = message.get("call", {}).get("customer", {}).get("name", "")

    order_summary = extract_order_summary(transcript)
    order_status  = "new" if is_food_order(order_summary) else "inquiry"

    db = SessionLocal()
    try:
        call = Call(
            call_id=call_id,
            customer_name=customer_name,
            phone_number=phone_number,
            duration=duration,
            transcript=transcript,
            status="completed",
            order_summary=order_summary,
            order_status=order_status,
        )
        db.add(call)
        db.commit()
        print(f"✅ Call saved: {call_id}, is_order={order_status}, summary: {order_summary}")
    except Exception as e:
        db.rollback()
        print(f"❌ DB error: {e}")
    finally:
        db.close()

    return {"response": "ok"}
