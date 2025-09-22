from fastapi import FastAPI
from loguru import logger
from settings import *
from exc_handler import exception_handlers
from urls import register_routers

logger.add(f"{LOG_DIR}/app.log", rotation="1 week", retention="1 month", compression="zip")
app = FastAPI(title="知识库", exception_handlers=exception_handlers)
register_routers(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18000)
    # uvicorn main:app --host 0.0.0.0 --port 18000 --reload

