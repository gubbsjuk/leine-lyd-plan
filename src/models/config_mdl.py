from typing import Any

from sqlalchemy import TIMESTAMP, Column, String, func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()  # type: Any


class Config(Base):
    userID = Column(String(), primary_key=True)
    deviceID = Column(String())
    last_updated = Column(
        TIMESTAMP, server_default.func.now(), onupdate=func.current_timestamp()
    )
