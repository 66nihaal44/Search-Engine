from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

engine = None
SessionLocal = None

def init_db():
  global engine, SessionLocal
  engine = create_engine("postgresql://postgres.tgimnlfbhygfefgvnimz:$688039ForNihaal@aws-1-us-west-2.pooler.supabase.com:6543/postgres")
  SessionLocal = sessionmaker(bind=engine)
  Base.metadata.create_all(engine)
