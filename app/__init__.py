from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routes import router

def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    # 禁用自动追加斜杠的重定向
    app = FastAPI(
        title="Web Clipper API", 
        version="1.0.0",
        # 关键设置：禁用重定向
        redirect_slashes=False
    )
    
    # 创建限速器
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加路由
    app.include_router(router)
    
    return app