from fastapi import HTTPException, status, Request, UploadFile
from schemas import UserCreate, UserLogin, UserResponse
from database import db
import bcrypt
import os
import shutil
import uuid

PROFILE_UPLOAD_DIR = "profile_uploads"
os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def create_user(user: UserCreate) -> UserResponse:
    async with db.pool.acquire() as conn:
        existing_user = await conn.fetchrow("SELECT id FROM users WHERE login_id = $1", user.login_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login ID already exists"
            )
        
        # Check if nickname already exists
        existing_nickname = await conn.fetchrow("SELECT id FROM users WHERE nick_name = $1", user.nick_name)
        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname already exists"
            )
        
        hashed_pw = get_password_hash(user.login_pw)
        
        row = await conn.fetchrow(
            """
            INSERT INTO users (login_id, login_pw, nick_name)
            VALUES ($1, $2, $3)
            RETURNING id, nick_name, check_admin, profile_image, created_at
            """,
            user.login_id, hashed_pw, user.nick_name
        )
        
        return UserResponse(
            id=row['id'],
            nick_name=row['nick_name'],
            check_admin=row['check_admin'],
            profile_image=row['profile_image'],
            created_at=row['created_at']
        )

async def authenticate_user(user: UserLogin, request: Request) -> UserResponse:
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, login_pw, nick_name, check_admin, profile_image, created_at FROM users WHERE login_id = $1",
            user.login_id
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login ID or password"
            )
            
        if not verify_password(user.login_pw, row['login_pw']):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login ID or password"
            )
        
        request.session['user_id'] = row['id']
        
        return UserResponse(
            id=row['id'],
            nick_name=row['nick_name'],
            check_admin=row['check_admin'],
            profile_image=row['profile_image'],
            created_at=row['created_at']
        )

async def logout_user(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}

async def get_current_user(request: Request) -> UserResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, nick_name, check_admin, profile_image, created_at FROM users WHERE id = $1",
            user_id
        )
        if not row:
            request.session.clear()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return UserResponse(
            id=row['id'],
            nick_name=row['nick_name'],
            check_admin=row['check_admin'],
            profile_image=row['profile_image'],
            created_at=row['created_at']
        )

async def get_optional_current_user(request: Request):
    """인증 없어도 None 반환 (공개 엔드포인트의 선택적 인증용)"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

async def update_profile_image(file: UploadFile, request: Request) -> UserResponse:
    current_user = await get_current_user(request)

    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다.")

    filename = f"profile_{current_user.id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(PROFILE_UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_path = f"/static/profile/{filename}"

    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE users SET profile_image = $1 WHERE id = $2
            RETURNING id, nick_name, check_admin, profile_image, created_at
            """,
            image_path, current_user.id
        )

    return UserResponse(
        id=row['id'],
        nick_name=row['nick_name'],
        check_admin=row['check_admin'],
        profile_image=row['profile_image'],
        created_at=row['created_at']
    )
