from fastapi import APIRouter, status, Request
from schemas import UserCreate, UserLogin, UserResponse
from controller.auth import auth_controller

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    return await auth_controller.create_user(user)

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, request: Request):
    return await auth_controller.authenticate_user(user, request)

@router.post("/logout")
async def logout(request: Request):
    return await auth_controller.logout_user(request)

@router.get("/me", response_model=UserResponse)
async def check_session(request: Request):
    return await auth_controller.get_current_user(request)
