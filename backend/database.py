from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for safety, though .env should exist
    DATABASE_URL = "postgresql://neondb_owner:npg_QPHdxF8TqpX6@ep-late-fog-a1zpudt5-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Connection pooling settings to reduce cold start and keep connections warm
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Keep 5 connections in pool
    max_overflow=10,      # Allow up to 10 extra connections
    pool_pre_ping=True,   # Test connections before using (prevents stale connections)
    pool_recycle=300,     # Recycle connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
