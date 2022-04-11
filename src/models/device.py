from sqlalchemy import TIMESTAMP, Column, String, func

from models.base import Base


class Device(Base):
    __tablename__ = "device"
    device_id = Column(String(), primary_key=True)
    user_id = Column(String())  # TODO: Don't know if this makes sense
    last_updated = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
