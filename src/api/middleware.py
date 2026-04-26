"""
窄门 (NarrowGate) - FastAPI中间件

请求日志、错误追踪等中间件
"""

import time
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logger import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("request")
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        self.logger.info(f"🔵 {method} {path} - 开始 (IP: {client_ip})")
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            status = response.status_code
            status_emoji = "✅" if 200 <= status < 400 else "❌"
            
            self.logger.info(f"{status_emoji} {method} {path} - {status} ({duration:.0f}ms)")
            response.headers["X-Process-Time"] = f"{duration:.0f}ms"
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(f"❌ {method} {path} - 异常: {e} ({duration:.0f}ms)")
            raise


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """错误追踪中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("error")
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            self.logger.error(
                f"🔥 未捕获异常: {request.method} {request.url.path}\n"
                f"   错误类型: {type(e).__name__}\n"
                f"   错误信息: {e}"
            )
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "服务器内部错误",
                    "message": "请稍后重试",
                    "timestamp": datetime.now().isoformat()
                }
            )