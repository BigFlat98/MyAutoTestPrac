
import asyncio
import os
from database import db
from dotenv import load_dotenv

load_dotenv()

async def verify_tables():
    await db.connect()
    try:
        tables = ['users', 'todos', 'posts', 'post_images', 'post_replies']
        print("\n--- Verifying Tables ---")
        async with db.pool.acquire() as conn:
            for table in tables:
                exists = await conn.fetchval(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE  table_schema = 'public'
                        AND    table_name   = '{table}'
                    );
                """)
                print(f"Table '{table}': {'EXISTS' if exists else 'MISSING'}")
                
                if exists:
                    # Optional: Print columns to verify structure
                    cols = await conn.fetch(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                    """)
                    # print(f"  Columns: {[row['column_name'] for row in cols]}")

    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_tables())
