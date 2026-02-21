import asyncio
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal, engine, Base
from app.models.user_model import User
from app.utils.security import get_password_hash
from app.database.connection import DATABASE_URL
print("Using DB:", DATABASE_URL)
async def create_user():

    # 🔹 สร้าง table ก่อน (สำคัญ)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("User already exists.")
            return

        new_user = User(
            username="Dexter",
            password_hash=get_password_hash("Morgan123"),
            role="clinician"
        )

        session.add(new_user)
        await session.commit()

        print("User created successfully.")


if __name__ == "__main__":
    asyncio.run(create_user())