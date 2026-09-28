from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core import config


db_url = config.settings.db_url

engine = create_engine(db_url)

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)