import os

from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models import Base


load_dotenv()

engine = create_async_engine(os.getenv("DB_PATH"), echo=True, future=True)

async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
