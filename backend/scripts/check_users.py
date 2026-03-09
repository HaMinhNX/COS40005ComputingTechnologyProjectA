
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    result = conn.execute(text("SELECT username, role FROM users"))
    for row in result:
        print(f"User: {row[0]}, Role: {row[1]}")
