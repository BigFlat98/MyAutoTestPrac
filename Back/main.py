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
from schemas import EchoRequest, ItemRequest, ItemResponse

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
from controller.test.items import router as items_router
from router.auth import router as auth_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

#router 등록
app.include_router(items_router)
app.include_router(dashboard.router)
app.include_router(todo.router)
app.include_router(auth_router)
app.include_router(board.router)
app.include_router(video.router)


# CORS definition
# CORS definition
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost",
    "http://127.0.0.1",
    "http://3.34.207.211", # 사용자 EC2 Public IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origin_regex="https?://.*", # Disabled for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "your-secret-key"), max_age=7200, same_site="lax", https_only=False)



@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/echo")
def echo_message(request: EchoRequest):
    return {"echo": f"Server received: {request.message}"}



