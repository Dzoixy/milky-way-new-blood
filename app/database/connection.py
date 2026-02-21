import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base

# ======================================================
# DATABASE URL
# ======================================================

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback สำหรับ local dev เท่านั้น
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./milkyway.db"

# Render / Heroku postgres URL fix (sync → async)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1
    )

# ======================================================
# ENGINE (Production-ready pooling)
# ======================================================

engine = create_async_engine(
    DATABASE_URL,
    echo=False,                 # ห้ามเปิดใน production
    pool_pre_ping=True,         # เช็ค connection ก่อนใช้งาน
    pool_size=5,                # worker connection pool
    max_overflow=10,            # burst traffic
)

# ======================================================
# SESSION FACTORY
# ======================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

# ======================================================
# Dependency
# ======================================================

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session