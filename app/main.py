from fastapi import FastAPI
from app.routes import webhook, dashboard
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(webhook.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "AI Receptionist Backend Running"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)