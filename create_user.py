import asyncio

from app.database.connection import AsyncSessionLocal
from app.models.user_model import User
from app.utils.security import get_password_hash


async def create_user():

    async with AsyncSessionLocal() as session:

        # ตรวจว่ามี user นี้อยู่แล้วหรือยัง
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("User 'admin' already exists.")
            return

        new_user = User(
            username="Dexter morgan",
            password_hash=get_password_hash("morgan123"),
            role="clinician"
        )

        session.add(new_user)
        await session.commit()

        print("User 'admin' created successfully.")


if __name__ == "__main__":
    asyncio.run(create_user())