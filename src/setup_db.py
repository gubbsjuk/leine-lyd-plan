import sqlalchemy_utils

from sqlalchemy import create_engine

from models.base import Base


engine = create_engine("sqlite:///5l.db", echo=True, future=True)
if sqlalchemy_utils.database_exists(engine.url):
    sqlalchemy_utils.drop_database(engine.url)

Base.metadata.create_all(engine)
