#back 기본 import
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

load_dotenv() # .env 파일 로드 명시적 호출

#db connection
from database import db 
from contextlib import asynccontextmanager

#pydantic import

# scheduler
from controller.service.market_scheduler import setup_scheduler

@asynccontextmanager #fastapi 앱이 켜지고 꺼질 때 DB 연결/해제 설정
async def lifespan(app: FastAPI):
    await db.connect() #앱 시작 시 DB 연결
    scheduler = setup_scheduler()
    scheduler.start()
    print("[Scheduler] Started.")
    yield
    scheduler.shutdown()
    print("[Scheduler] Shutdown.")
    await db.disconnect() #앱 종료 시 DB 연결 해제

#router import 
from router import dashboard
from router import todo
from router import board
from router import video
from router.auth import router as auth_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

#router 등록
app.include_router(dashboard.router)
app.include_router(todo.router)
app.include_router(auth_router)
app.include_router(board.router)
app.include_router(video.router)


# CORS definition
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1",
    f"https://{os.getenv('DOMAIN', '')}",
    f"http://{os.getenv('DOMAIN', '')}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origin_regex="https?://.*", # Disabled for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "your-secret-key"), max_age=7200, same_site="lax", https_only=os.getenv("HTTPS_ONLY", "false").lower() == "true")



@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
def health_check():
    return {"status": "ok"}



