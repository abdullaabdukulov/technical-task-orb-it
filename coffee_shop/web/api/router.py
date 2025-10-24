from fastapi.routing import APIRouter

from coffee_shop.web.api import auth, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
# api_router.include_router(users.router)
api_router.include_router(auth.router)
