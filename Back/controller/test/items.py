# Back/controller/items.py
from fastapi import APIRouter
from database import db

from schemas import ItemRequest, ItemResponse # 실행되는 main.py 기준으로 절대 경로로 import
from typing import List

# 라우터 객체 생성 (prefix를 설정하면 이 라우터의 모든 URL 앞에 붙습니다)
router = APIRouter(
    prefix="/items",    # 모든 경로는 /items 로 시작
    tags=["Items"]      # Swagger 문서에서 그룹핑할 이름
)

# @app.post("/items") -> @router.post("/") 로 변경 (prefix가 이미 /items니까)
@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemRequest):
    async with db.pool.acquire() as conn:
        new_id = await conn.fetchval(
            "INSERT INTO items (content) VALUES ($1) RETURNING id", 
            item.content
        )
    return ItemResponse(id=new_id, content=item.content)

# @app.get("/items") -> @router.get("/")
@router.get("/", response_model=List[ItemResponse])
async def get_items():
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM items ORDER BY id DESC")
    return [ItemResponse(id=row['id'], content=row['content']) for row in rows]