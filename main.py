from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger
from settings import *
from exc_handler import exception_handlers
from urls import register_routers
import os

logger.add(f"{LOG_DIR}/app.log", rotation="1 week", retention="1 month", compression="zip")
app = FastAPI(title="知识库", exception_handlers=exception_handlers)

# 注册路由
register_routers(app)

# 添加静态文件服务
if os.path.exists("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

# 添加QA表单页面路由
@app.get("/qa-form", include_in_schema=False)
async def qa_form():
    """QA添加表单页面"""
    return FileResponse("web/qa_form.html")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18000)
    # uvicorn main:app --host 0.0.0.0 --port 18000 --reload

