import sqlalchemy_utils

from sqlalchemy import create_engine

import models.schedule
import models.config_mdl


engine = create_engine("sqlite:///5l.db", echo=True, future=True)
if sqlalchemy_utils.database_exists(engine.url):
    sqlalchemy_utils.drop_database(engine.url)

models.schedule.Base.metadata.create_all(engine)
models.config_mdl.Base.metadata.create_all(engine)
