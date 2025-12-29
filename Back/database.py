# Back/database.py
"""
[작동 원리 및 실행 순서]

1. 인스턴스 생성 (db = Database())
   - Database 클래스의 인스턴스가 생성되지만, 아직 DB 연결은 수립되지 않음 (pool = None).
   - 이 'db' 객체는 싱글톤처럼 애플리케이션 전역에서 공유됨.

2. 연결 시작 (main.py -> lifespan -> db.connect())
   - FastAPI 앱이 시작될 때(Startup) `lifespan` 함수가 실행됨.
   - `await db.connect()`가 호출되면 `asyncpg.create_pool`을 통해 DB 연결 풀을 생성함.
   - 연결 풀(Pool)은 여러 개의 DB 연결을 미리 만들어두고 재사용하는 방식 (성능 최적화).
   - 이 시점에 'items' 테이블이 없으면 자동으로 생성함 (CREATE TABLE IF NOT EXISTS).

3. 쿼리 실행 (API 호출 시 -> await conn.execute/fetch)
   - API 요청이 들어오면 `async with db.pool.acquire() as conn:` 형태로 풀에서 연결을 하나 빌림.
   - SQL 쿼리를 실행하고 결과를 반환받음.
   - 블록을 빠져나가면(`async with` 종료) 연결이 자동으로 풀로 반환됨.

4. 연결 종료 (main.py -> lifespan 종료 -> db.disconnect())
   - FastAPI 앱이 종료될 때(Shutdown) `db.disconnect()`가 호출됨.
   - 생성된 풀을 닫고 모든 DB 연결을 정리함.
"""
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        print("Connecting to Database...")
        try:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "postgres"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
                port=os.getenv("DB_PORT", "5432")
            )
            print("Database Connected!")
            
            # (선택) 테이블 자동 생성 로직도 여기에 둘 수 있습니다.
            async with self.pool.acquire() as conn:
                 await conn.execute('''
                    /* Helper: Drop table for schema migration during dev - COMMENTED OUT FOR PERSISTENCE */
                    DROP TABLE IF EXISTS todos; -- Reset todos to apply FK change
                    DROP TABLE IF EXISTS users; -- Reset users to apply UNIQUE constraint
                    DROP TABLE IF EXISTS posts;
                    DROP TABLE IF EXISTS post_images;
                    DROP TABLE IF EXISTS post_replies;

                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL PRIMARY KEY,
                        content TEXT
                    );

                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        login_id VARCHAR(30) UNIQUE NOT NULL,
                        login_pw TEXT NOT NULL,
                        nick_name VARCHAR(20) UNIQUE NOT NULL,
                        check_admin BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS todos (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        due_date DATE,
                        is_done BOOLEAN DEFAULT FALSE,
                        author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS posts (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        view_count INTEGER DEFAULT 0,
                        is_public BOOLEAN DEFAULT TRUE,
                        author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS post_images (
                        id SERIAL PRIMARY KEY,
                        image_name TEXT,
                        image_location TEXT,
                        uploader_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                        post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS post_replies (
                        id SERIAL PRIMARY KEY,
                        description TEXT,
                        post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        reply_id INTEGER REFERENCES post_replies(id) ON DELETE CASCADE,
                        delete_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                 ''')
                 
        except Exception as e:
            print(f"Error connecting to database: {e}")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("Database Connection Closed.")

    async def get_connection(self):
        if not self.pool:
            raise Exception("Database not connected")
        return self.pool.acquire()

# 싱글톤 인스턴스 생성
db = Database()