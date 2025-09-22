# urls.py
from fastapi import FastAPI
from routers.agent import router as agent_router


def register_routers(app: FastAPI):
    """注册路由"""
    app.include_router(agent_router)
