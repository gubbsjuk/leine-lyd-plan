from sqlalchemy import TIMESTAMP, Column, String, func

from models.base import Base


class Schedule(Base):
    __tablename__ = "schedule"
    playlist = Column(String())
    playlist_id = Column(String())
    start_day = Column(String(), primary_key=True)
    start_time = Column(String(), primary_key=True)
    last_updated = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
