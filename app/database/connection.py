import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base

# อ่านจาก environment ก่อน
DATABASE_URL = os.getenv("DATABASE_URL")

# ถ้าไม่มี (เช่น local dev) ให้ fallback เป็น SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./milkyway.db"

# ถ้าเป็น postgres แบบ sync ให้แปลงเป็น async
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1
    )

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # production ไม่ควร echo=True
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session