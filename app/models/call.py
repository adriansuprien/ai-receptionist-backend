from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, index=True)
    customer_name = Column(String)
    phone_number = Column(String)
    duration = Column(Float)
    transcript = Column(String)
    status = Column(String)