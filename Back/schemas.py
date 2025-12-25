from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EchoRequest(BaseModel):
    message: str

#DB저장 테스트 요청용 pydantic
class ItemRequest(BaseModel):
    content: str

#DB저장 테스트 응답용 pydantic
class ItemResponse(BaseModel):
    id: int
    content: str

# Must Do List Models
class TodoCreate(BaseModel):
    title: str
    description: str
    due_date: date
    author: Optional[str] = None # Optional for now

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_done: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    due_date: date
    is_done: bool
    created_at: datetime
    author: Optional[str] = None
