#back 기본 import
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#db connection
from database import db 
from contextlib import asynccontextmanager

#pydantic import
from schemas import EchoRequest, ItemRequest, ItemResponse

@asynccontextmanager #fastapi 앱이 켜지고 꺼질 때 DB 연결/해제 설정
async def lifespan(app: FastAPI):
    await db.connect() #앱 시작 시 DB 연결
    yield
    await db.disconnect() #앱 종료 시 DB 연결 해제

#router import 
from controller.test.items import router as items_router

app = FastAPI(lifespan=lifespan)

#router 등록
app.include_router(items_router)


# CORS definition
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "*" # 개발 편의를 위해 모든 출처 허용 (배포 시 제거 필요)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # origins 변수 대신 강제로 와일드카드 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/echo")
def echo_message(request: EchoRequest):
    return {"echo": f"Server received: {request.message}"}



