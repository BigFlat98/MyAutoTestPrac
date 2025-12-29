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

# User Schemas
class UserCreate(BaseModel):
    login_id: str
    login_pw: str
    nick_name: str

class UserLogin(BaseModel):
    login_id: str
    login_pw: str

class UserResponse(BaseModel):
    id: int
    nick_name: str
    check_admin: bool

# Must Do List Models
class TodoCreate(BaseModel):
    title: str
    description: str
    due_date: date
    # author is handled by auth middleware or explicit login context usually, 
    # but for now let's make it optional or remove if we infer it from session. 
    # keeping it simple as per request.

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
    author_id: Optional[int] = None # Changed from author(text) to author_id(int)


# Board / Post Models
class PostCreate(BaseModel):
    title: str
    description: str
    image: Optional[str] = None # For image URL

class PostResponse(BaseModel):
    id: int
    title: str
    description: str
    view_count: int
    author: str # Nickname from join
    created_at: datetime
    image: Optional[str] = None

class PostListResponse(BaseModel):
    total: int
    page: int
    limit: int
    posts: list[PostResponse]

class CommentCreate(BaseModel):
    description: str
    reply_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    author: str
    content: str # Maps to description in DB
    created_at: datetime
    replies: list['CommentResponse'] = []
    
    class Config:
        from_attributes = True

# Update forward refs for recursive model
CommentResponse.model_rebuild()
