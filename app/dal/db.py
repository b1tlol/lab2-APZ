from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, AccountORM, CategoryORM, TransactionORM

def build_session_factory(db_url: str = "sqlite:///fin.db"):
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
