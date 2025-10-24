# from fastapi import APIRouter, HTTPException, status

# from coffee_shop.db.models.users import (
#     UserCreate,  # type: ignore
#     UserRead,  # type: ignore
#     UserUpdate,  # type: ignore
#     api_users,  # type: ignore
#     # auth_jwt,  # type: ignore
# )

# router = APIRouter()


# router.include_router(
#     api_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
#
# router.include_router(
#     api_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )
