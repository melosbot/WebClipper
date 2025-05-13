import logging
import uvicorn
import os
from pathlib import Path

from app.config import settings
from app import create_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 设置 httpx 日志级别为 WARNING，隐藏请求日志
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("web_clipper")

def start_server(host=None, port=None):
    """启动 Web Clipper 服务器"""
    host = host or settings.HOST
    port = port or settings.PORT
    
    # 创建上传目录
    Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
    
    # 打印 API 密钥前几个字符用于调试
    api_key_preview = settings.API_KEY[:5] + "..." if settings.API_KEY else "未设置"
    logger.info(f"API 密钥前缀: {api_key_preview}")
    
    # 创建应用
    app = create_app()
    
    logger.info(f"🚀 启动 Web Clipper API 服务 - 监听地址: {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # 验证设置
    try:
        settings.validate()
    except ValueError as e:
        logger.error(f"⚠️ 配置错误: {e}")
        logger.error("⚠️ 请检查 .env 文件或环境变量配置")
        exit(1)
        
    # 启动服务器
    start_server()