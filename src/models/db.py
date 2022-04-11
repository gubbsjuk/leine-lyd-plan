from typing import Any

from sqlalchemy import TIMESTAMP, Column, String, func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()  # type: Any


class Device(Base):
    __tablename__ = "device"
    user_id = Column(String(), primary_key=True)  # TODO: Don't know if this makes sense
    device_id = Column(String())
    device_name = Column(String())
    last_updated = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class Schedule(Base):
    __tablename__ = "schedule"
    playlist = Column(String())
    playlist_uri = Column(String())
    start_day = Column(String(), primary_key=True)
    start_time = Column(String(), primary_key=True)
    last_updated = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
