import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


database_url = os.environ["DATABASE_URL"]

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

