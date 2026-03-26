from fastapi import APIRouter, status, Request, UploadFile, File
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

@router.post("/profile-image", response_model=UserResponse)
async def upload_profile_image(request: Request, file: UploadFile = File(...)):
    return await auth_controller.update_profile_image(file, request)

@router.post("/withdraw", response_model=UserResponse)
async def withdraw(request: Request):
    """회원 탈퇴 예약 (7일 후 계정 영구 삭제)"""
    return await auth_controller.withdraw_user(request)

@router.delete("/withdraw", response_model=UserResponse)
async def cancel_withdraw(request: Request):
    """회원 탈퇴 취소 (delete_date 초기화)"""
    return await auth_controller.cancel_withdraw_user(request)
