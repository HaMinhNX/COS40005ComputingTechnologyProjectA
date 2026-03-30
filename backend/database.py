from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    # Fallback for safety, though .env should exist
    DATABASE_URL = "postgresql://neondb_owner:npg_QPHdxF8TqpX6@ep-late-fog-a1zpudt5-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine_args = {}
if not DATABASE_URL.startswith("sqlite"):
    engine_args = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
else:
    engine_args = {
        "connect_args": {"check_same_thread": False}
    }

engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
