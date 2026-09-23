from fastapi import APIRouter

from app.api import demo, reports, routes

api_router = APIRouter()
api_router.include_router(routes.router)
api_router.include_router(reports.router)
api_router.include_router(demo.router)
