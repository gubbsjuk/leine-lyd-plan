import sqlalchemy_utils

from sqlalchemy import create_engine

import models


engine = create_engine("sqlite:///5l.db", echo=True, future=True)
if sqlalchemy_utils.database_exists(engine.url):
    sqlalchemy_utils.drop_database(engine.url)

models.base.Base.metadata.create_all(engine)
