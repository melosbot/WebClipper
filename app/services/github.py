import os
import time
import logging
import requests
from github import Github
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

class GitHubService:
    """GitHub 服务，处理文件上传和访问"""
    
    def __init__(self):
        self.github_client = Github(settings.GITHUB_TOKEN)
        self.repo = None
        
    def _get_repo(self):
        """获取 GitHub 仓库实例"""
        if not self.repo:
            self.repo = self.github_client.get_repo(settings.GITHUB_REPO)
        return self.repo
        
    def upload_file(self, file_path: Path) -> tuple:
        """
        上传文件到 GitHub Pages
        
        Args:
            file_path: 本地文件路径
            
        Returns:
            tuple: (文件名, GitHub Pages URL)
        """
        try:
            filename = os.path.basename(file_path)
            
            logger.info(f"正在上传文件 {filename} 到 GitHub...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            repo = self._get_repo()
            file_path_in_repo = f"clips/{filename}"
            
            # 创建或更新文件
            repo.create_file(
                file_path_in_repo,
                f"Add web clip: {filename}",
                content,
                branch="main"
            )
            
            # 构建 GitHub Pages URL
            repo_name = settings.GITHUB_REPO.split('/')[1]
            github_url = f"https://{settings.GITHUB_PAGES_DOMAIN}/{repo_name}/clips/{filename}"
            
            # 等待 GitHub Pages 部署
            self._wait_for_pages_deployment(github_url)
            
            logger.info(f"文件已成功上传到 {github_url}")
            return filename, github_url
            
        except Exception as e:
            logger.error(f"GitHub 上传失败: {str(e)}")
            raise
            
    def _wait_for_pages_deployment(self, url: str) -> bool:
        """
        等待 GitHub Pages 部署完成
        
        Args:
            url: GitHub Pages URL
            
        Returns:
            bool: 是否成功部署
        """
        logger.info(f"等待 GitHub Pages 部署: {url}")
        
        max_retries = settings.GITHUB_PAGES_MAX_RETRIES
        for attempt in range(max_retries):
            try:
                logger.debug(f"检查部署状态 (尝试 {attempt+1}/{max_retries})...")
                response = requests.get(url)
                
                if response.status_code == 200:
                    logger.info(f"GitHub Pages 部署完成 (尝试 {attempt+1})")
                    return True
                    
                # 非 200 状态码，继续等待
                logger.debug(f"部署未完成，状态码: {response.status_code}")
                
            except Exception as e:
                logger.debug(f"检查部署时出错: {str(e)}")
                
            # 休眠 5 秒再重试
            time.sleep(5)
            
        logger.warning(f"GitHub Pages 部署超时，将继续处理")
        return False