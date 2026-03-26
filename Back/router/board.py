from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException
from typing import List, Optional
from schemas import PostResponse, CommentResponse, CommentCreate, PostListResponse
from controller.auth.auth_controller import get_current_user, get_optional_current_user
from controller.post import post_controller

router = APIRouter(prefix="/posts", tags=["Board"])

@router.get("", response_model=PostListResponse)
async def get_posts(request: Request, page: int = 1, limit: int = 15, author_me: bool = False):
    author_id = None
    if author_me:
        current_user = await get_optional_current_user(request)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        author_id = current_user.id
    return await post_controller.get_posts(page, limit, author_id)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    return await post_controller.get_post(post_id)

@router.post("", response_model=PostResponse)
async def create_post(
    title: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_user)
):
    return await post_controller.create_post(title, description, is_public, image, current_user)

@router.post("/image/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    return await post_controller.upload_image(file, current_user)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    title: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_user)
):
    return await post_controller.update_post(post_id, title, description, is_public, image, current_user)

@router.delete("/{post_id}")
async def delete_post(post_id: int, current_user = Depends(get_current_user)):
    return await post_controller.delete_post(post_id, current_user)

# Comments
@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(post_id: int):
    return await post_controller.get_comments(post_id)

@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user = Depends(get_current_user)
):
    return await post_controller.create_comment(post_id, comment, current_user)

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, current_user = Depends(get_current_user)):
    return await post_controller.delete_comment(comment_id, current_user)
