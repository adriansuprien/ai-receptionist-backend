from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.webhook import router as webhook_router
from app.routes.dashboard import router as dashboard_router
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"message": "AI Receptionist Backend Running"}

#test push