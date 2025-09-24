# urls.py
from fastapi import FastAPI
from routers.agent import router as agent_router
from routers.qa import router as qa_router


def register_routers(app: FastAPI):
    """注册路由"""
    app.include_router(agent_router)
    app.include_router(qa_router)
