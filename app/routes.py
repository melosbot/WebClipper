import secrets
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services.clipper import WebClipperHandler

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

# 初始化处理器和认证
security = HTTPBearer()
clipper = WebClipperHandler()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 Bearer 令牌"""
    token = credentials.credentials
    if token != settings.API_KEY:
        logger.warning(f"无效的认证令牌: {token[:5]}...")
        raise HTTPException(
            status_code=401,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# 同时支持带斜杠和不带斜杠的路由
@router.post("/upload")
@router.post("/upload/")
async def upload_file(
    request: Request,
    token: str = Depends(verify_token)
):
    """文件上传接口"""
    limiter = request.app.state.limiter
    
    @limiter.limit("10/minute")
    async def rate_limited_upload(request: Request):
        try:
            logger.info("收到文件上传请求")
            form = await request.form()
            original_url = form.get('url', '')
            
            # 获取文件内容
            file = None
            for field_name, field_value in form.items():
                if hasattr(field_value, 'filename') and hasattr(field_value, 'read'):
                    file = field_value
                    break
            
            if not file:
                raise HTTPException(
                    status_code=400,
                    detail="在表单数据中找不到文件内容"
                )
            
            filename = file.filename
            logger.info(f"准备处理文件: {filename}")
            content = await file.read()
            
            # 验证文件
            file_ext = Path(filename).suffix.lower()
            if not file_ext:
                filename += '.html'
            elif file_ext not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件类型不支持。支持的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                )
            
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件太大。最大支持: {settings.MAX_FILE_SIZE/1024/1024}MB"
                )
            
            # 保存文件
            safe_filename = f"{secrets.token_hex(8)}_{filename}"
            file_path = settings.UPLOAD_DIR / safe_filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            try:
                logger.info("开始处理文件")
                result = await clipper.process_file(file_path, original_url)
                return result
            finally:
                if file_path.exists():
                    file_path.unlink()
                    
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"上传失败: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    
    return await rate_limited_upload(request)

@router.get("/test-auth")
async def test_auth(token: str = Depends(verify_token)):
    """测试授权端点"""
    return {"message": "认证成功", "api_key_prefix": token[:5] + "..." if token else ""}