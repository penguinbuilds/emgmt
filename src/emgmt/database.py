from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.emgmt.config import settings
# from src.emgmt.models import Base

engine = create_engine(settings.DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def create_db_and_tables():
#     Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
