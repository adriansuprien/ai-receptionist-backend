from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id              = Column(Integer, primary_key=True, default=1)
    restaurantName  = Column(String, default="Punjab Halal Meat & Grill")
    phoneNumber     = Column(String, default="")
    openingHours    = Column(String, default="")
    greeting        = Column(String, default="")
    forwardNumber   = Column(String, default="")
    openTime        = Column(String, default="09:00")
    closeTime       = Column(String, default="17:00")
    takeOrders      = Column(String, default="true")
    bookAppointments = Column(String, default="false")
