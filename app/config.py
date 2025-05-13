import os
import secrets
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Settings:
    # 服务器设置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "65331"))
    
    # GitHub 设置
    GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_PAGES_DOMAIN: str = os.getenv("GITHUB_PAGES_DOMAIN", "")
    GITHUB_PAGES_MAX_RETRIES: int = int(os.getenv("GITHUB_PAGES_MAX_RETRIES", "60"))
    
    # Notion 设置
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    
    # Telegram 设置
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # OpenAI 设置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_MAX_RETRIES: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
    
    # API 安全
    API_KEY: str = os.getenv("API_KEY", "")
    
    # 文件限制
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(30 * 1024 * 1024)))
    ALLOWED_EXTENSIONS: List[str] = os.getenv("ALLOWED_EXTENSIONS", ".html,.htm").split(",")
    
    # 派生设置
    UPLOAD_DIR: Path = Path("uploads")
    
    def __init__(self):
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        
        # 如果没有设置 API_KEY，生成一个
        if not self.API_KEY:
            self.API_KEY = secrets.token_urlsafe(32)
            print(f"⚠️ 未设置 API_KEY，已生成临时密钥: {self.API_KEY}")
            print("⚠️ 请在生产环境中设置一个固定的 API_KEY")
    
    def validate(self):
        """验证必要的设置是否存在"""
        missing = []
        essential_vars = [
            "GITHUB_REPO", "GITHUB_TOKEN", "GITHUB_PAGES_DOMAIN",
            "NOTION_DATABASE_ID", "NOTION_TOKEN", 
            "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID",
            "OPENAI_API_KEY"
        ]
        
        for var in essential_vars:
            if not getattr(self, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing)}")

# 单例设置对象
settings = Settings()