"""请求日志中间件

记录每个请求的详细信息和处理时间
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} {response.status_code} {duration:.2f}ms"
        )

        return response
