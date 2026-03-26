from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

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
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None

# Must Do List Models
class TodoCreate(BaseModel):
    title: str
    description: str
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    # author is handled by auth middleware or explicit login context usually, 
    # but for now let's make it optional or remove if we infer it from session. 
    # keeping it simple as per request.

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_done: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    due_date: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]
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

# Stock Models
class StockItem(BaseModel):
    rank: int
    symbol: str
    name: str
    price: float
    change: float
    currency: str

class StockListResponse(BaseModel):
    market: str
    stocks: List[StockItem]
    status: str
    message: Optional[str] = None

# Update forward refs for recursive model
CommentResponse.model_rebuild()

# Video Models
class VideoTagResponse(BaseModel):
    id: int
    name: str

class VideoCommentCreate(BaseModel):
    content: str
    reply_id: Optional[int] = None

class VideoCommentResponse(BaseModel):
    id: int
    author: str
    content: str
    created_at: datetime
    reply_id: Optional[int] = None

class VideoCreate(BaseModel):
    title: str
    description: str
    url: str
    tag_id: Optional[int] = None

class VideoResponse(BaseModel):
    id: int
    title: str
    original_title: Optional[str] = None
    description: str
    url: str
    video_key: Optional[str] = None
    view_count: int
    like_count: int
    hate_count: int
    reported_count: int
    tag_id: Optional[int] = None
    tag_name: Optional[str] = None
    uploader_id: int
    author: str 
    created_at: datetime
    comments: List[VideoCommentResponse] = []

class VideoListResponse(BaseModel):
    total: int
    videos: List[VideoResponse]

