import asyncio
import os
import sys

# Add current directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

from database import db
from controller.auth import get_password_hash, verify_password

async def test():
    print("Testing DB Connection...")
    try:
        await db.connect()
        print("DB Connected. Pool:", db.pool)
    except Exception as e:
        print(f"DB Connection Failed: {e}")
        return

    print("Testing Password Hash...")
    try:
        hashed = get_password_hash("test")
        print("Hashed:", hashed)
        print("Verify:", verify_password("test", hashed))
    except Exception as e:
        print(f"Password Hash Failed: {e}")
        return
    
    try:
        async with db.pool.acquire() as conn:
            print("Acquired connection")
            row = await conn.fetchrow("SELECT 1")
            print("Query Result:", row)
    except Exception as e:
         print(f"Query Failed: {e}")

    await db.disconnect()

if __name__ == "__main__":
    # Windows SelectorEventLoopPolicy might be needed or Proactor?
    # For asyncpg on Windows, sometimes Proactor is issue or loop policy.
    # But let's just run it.
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(test())
