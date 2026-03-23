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
                    -- DROP TABLE IF EXISTS todos; -- Reset todos to apply FK change
                    -- DROP TABLE IF EXISTS users; -- Reset users to apply UNIQUE constraint
                    
                    /* Force schema update for Video Feature Refactor */
                    -- DROP TABLE IF EXISTS video_comments CASCADE;
                    -- DROP TABLE IF EXISTS videos CASCADE;
                    -- DROP TABLE IF EXISTS video_tags CASCADE;

                    /* Playground 제거로 items 테이블 삭제 */
                    DROP TABLE IF EXISTS items;

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
                        start_date DATE,
                        end_date DATE,
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

                    CREATE TABLE IF NOT EXISTS chat_rooms(
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS messages(
                        id SERIAL PRIMARY KEY,
                        room_id INTEGER REFERENCES chat_rooms(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        content TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP,
                        deleted_at TIMESTAMP
                    );

                    /* Default Chat Room (ID: 1) */
                    INSERT INTO chat_rooms (id, name) VALUES (1, 'General') ON CONFLICT (id) DO NOTHING;

                    /* Video Tags Table (Single Choice) */
                    CREATE TABLE IF NOT EXISTS video_tags (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) UNIQUE NOT NULL
                    );
                    
                    /* Seed Default Tags */
                    INSERT INTO video_tags (name) VALUES 
                        ('Music'), ('Game'), ('Humor'), ('Vlog'), ('Tech'), ('Policy'), ('Beauty'), ('Sports')
                    ON CONFLICT (name) DO NOTHING;

                    CREATE TABLE IF NOT EXISTS videos (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        original_title TEXT,
                        description TEXT,
                        url TEXT NOT NULL,
                        video_key TEXT,
                        view_count INTEGER DEFAULT 0,
                        like_count INTEGER DEFAULT 0,
                        hate_count INTEGER DEFAULT 0,
                        reported_count INTEGER DEFAULT 0,
                        tag_id INTEGER REFERENCES video_tags(id) ON DELETE SET NULL,
                        uploader_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS video_comments (
                        id SERIAL PRIMARY KEY,
                        video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        content TEXT NOT NULL,
                        reply_id INTEGER REFERENCES video_comments(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* ==================== Dashboard Market Data Tables ==================== */

                    /* 공포탐욕지수 스냅샷 - 수집할 때마다 INSERT, 조회 시 최신 1건 사용 */
                    CREATE TABLE IF NOT EXISTS market_fear_greed (
                        id SERIAL PRIMARY KEY,
                        score INTEGER NOT NULL,
                        rating VARCHAR(20) NOT NULL,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* 주식 현재가 스냅샷 - 수집할 때마다 INSERT, 조회 시 market별 최신 수집분 사용 */
                    CREATE TABLE IF NOT EXISTS market_stocks (
                        id SERIAL PRIMARY KEY,
                        market VARCHAR(10) NOT NULL,
                        rank INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        symbol VARCHAR(20) NOT NULL,
                        price NUMERIC(15,2) NOT NULL,
                        change_rate NUMERIC(6,2) NOT NULL,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* 원/달러 환율 일별 시계열 - trade_date UNIQUE, UPSERT로 중복 방지 */
                    CREATE TABLE IF NOT EXISTS market_exchange_rate (
                        id SERIAL PRIMARY KEY,
                        trade_date DATE UNIQUE NOT NULL,
                        rate NUMERIC(10,2) NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* 한/미 기준금리 시계열 - trade_date UNIQUE, UPSERT로 중복 방지 */
                    CREATE TABLE IF NOT EXISTS market_interest_rate (
                        id SERIAL PRIMARY KEY,
                        trade_date DATE UNIQUE NOT NULL,
                        kr_rate NUMERIC(5,2),
                        us_rate NUMERIC(5,2),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* 암호화폐 현재가 스냅샷 - 수집할 때마다 INSERT, 조회 시 coin별 최신 1건 사용 */
                    CREATE TABLE IF NOT EXISTS market_crypto_price (
                        id SERIAL PRIMARY KEY,
                        coin VARCHAR(10) NOT NULL,
                        krw_price NUMERIC(20,2) NOT NULL,
                        usd_price NUMERIC(15,4) NOT NULL,
                        change_rate NUMERIC(6,2) NOT NULL,
                        kimchi_premium NUMERIC(6,2) NOT NULL,
                        exchange_rate NUMERIC(10,2) NOT NULL,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* 암호화폐 90일 OHLCV 히스토리 - (coin, trade_datetime) UNIQUE, UPSERT로 중복 방지 */
                    CREATE TABLE IF NOT EXISTS market_crypto_history (
                        id SERIAL PRIMARY KEY,
                        coin VARCHAR(10) NOT NULL,
                        trade_datetime TIMESTAMP NOT NULL,
                        upbit_price NUMERIC(20,2) NOT NULL,
                        binance_price NUMERIC(20,2) NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (coin, trade_datetime)
                    );

                    /* 금 현재가 스냅샷 - 수집할 때마다 INSERT, 조회 시 최신 1건 사용 */
                    CREATE TABLE IF NOT EXISTS market_gold_price (
                        id SERIAL PRIMARY KEY,
                        domestic_price NUMERIC(15,2) NOT NULL,
                        change_rate NUMERIC(6,2) NOT NULL,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    /* 금 가격 시계열 - trade_date UNIQUE, UPSERT로 중복 방지 */
                    CREATE TABLE IF NOT EXISTS market_gold_history (
                        id SERIAL PRIMARY KEY,
                        trade_date DATE UNIQUE NOT NULL,
                        domestic_price NUMERIC(15,2) NOT NULL,
                        international_price NUMERIC(15,4),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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