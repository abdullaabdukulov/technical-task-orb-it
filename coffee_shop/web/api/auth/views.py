from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.exceptions import UserAlreadyExists

from coffee_shop.services.auth.otp import OTPService
from coffee_shop.web.api.auth.dependencies import (
    UserManager,
    access_backend,
    api_users,
    current_active_user,
    current_refresh_user,
    get_otp_service,
    get_user_manager,
    refresh_backend,
)
from coffee_shop.web.api.auth.schemas import (
    LoginResponse,
    RefreshResponse,
    UserCreate,
    UserRead,
    VerifyRequest,
)

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/signup", response_model=UserRead)
async def signup(
    user_create: UserCreate,
    user_manager=Depends(api_users.get_user_manager),
):
    try:
        user = await user_manager.create(user_create, safe=True)
        return user
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager=Depends(api_users.get_user_manager),
):
    user = await user_manager.authenticate(form_data)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_strategy = access_backend.get_strategy()
    access_token = await access_strategy.write_token(user)

    refresh_strategy = refresh_backend.get_strategy()
    refresh_token = await refresh_strategy.write_token(user)

    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/refresh", response_model=RefreshResponse)
async def refresh(current_user=Depends(current_refresh_user)):
    access_strategy = access_backend.get_strategy()
    new_access_token = await access_strategy.write_token(current_user)
    return RefreshResponse(access_token=new_access_token)


@router.get("/protected", response_model=UserRead)
async def protected_route(user: UserRead = Depends(current_active_user)):
    return user


@router.post("/verify")
async def verify_email(
    data: VerifyRequest,
    otp_service: OTPService = Depends(get_otp_service),
    user_manager: UserManager = Depends(get_user_manager),
):
    verified = await otp_service.verify_otp(f"user:otp:{data.email}", data.code)
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user = await user_manager.mark_user_verified(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "verified"}
