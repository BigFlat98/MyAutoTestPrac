from fastapi import HTTPException, status, Request
from schemas import UserCreate, UserLogin, UserResponse
from database import db
import bcrypt

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
            RETURNING id, nick_name, check_admin
            """,
            user.login_id, hashed_pw, user.nick_name
        )
        
        return UserResponse(
            id=row['id'],
            nick_name=row['nick_name'],
            check_admin=row['check_admin']
        )

async def authenticate_user(user: UserLogin, request: Request) -> UserResponse:
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, login_pw, nick_name, check_admin FROM users WHERE login_id = $1", user.login_id)
        
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
            check_admin=row['check_admin']
        )

async def logout_user(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}

async def get_current_user(request: Request) -> UserResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, nick_name, check_admin FROM users WHERE id = $1", user_id)
        if not row:
            request.session.clear()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return UserResponse(
            id=row['id'],
            nick_name=row['nick_name'],
            check_admin=row['check_admin']
        )
