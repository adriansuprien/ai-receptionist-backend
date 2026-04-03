from fastapi import APIRouter, Request
from openai import OpenAI
import os

from app.db.database import SessionLocal
from app.models.call import Call

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/webhook")
async def webhook(request: Request):
    print("🔥 WEBHOOK HIT")

    try:
        data = await request.json()
    except Exception:
        data = {}

    print("🔥 DATA:", data)

    transcript = data.get("text", "")

    # SIMPLE RESPONSE FOR VAPI
    return {
        "response": "What would you like to order?"
    }