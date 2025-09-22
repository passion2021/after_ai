from loguru import logger
import traceback
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError
import json


async def global_exception_handler(request, exc):
    exc_info = f'{type(exc).__name__}: {str(exc)}'
    logger.error(f"\n{exc_info}\n{request.url} {request.method}\n{traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"code": 500, "message": "Server Error",
                                                  "data": {"error": exc_info}})


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 获取错误详情
    error_details = exc.errors()

    # 获取异常堆栈信息
    stack_trace = traceback.format_exc()
    # 将堆栈信息与错误一起记录
    custom_error = {
        "code": 1024,
        "message": str(error_details[0].get("msg")),
        "data": error_details,
    }
    # 记录日志
    logger.error(f"{json.dumps(custom_error)}\n{stack_trace}")
    # 返回自定义的错误响应
    return JSONResponse(status_code=400, content=custom_error)


exception_handlers = {
    Exception: global_exception_handler,
    RequestValidationError: validation_exception_handler
}
