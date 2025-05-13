import logging
import time
import os
import requests
import html2text
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, Tuple, Any

from app.services.github import GitHubService
from app.services.notion import NotionService
from app.services.telegram import TelegramService
from app.services.ai import AIService
from app.utils import parse_filename

logger = logging.getLogger(__name__)

class WebClipperHandler:
    """网页剪藏处理器，协调各个服务"""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.notion_service = NotionService()
        self.telegram_service = TelegramService()
        self.ai_service = AIService()
        
    async def process_file(self, file_path: Path, original_url: str = '') -> Dict[str, str]:
        """
        处理上传的文件
        
        Args:
            file_path: 文件路径
            original_url: 原始URL
            
        Returns:
            dict: 处理结果
        """
        try:
            logger.info("🔄 开始处理新的网页剪藏...")
            
            # 1. 上传到 GitHub Pages
            filename, github_url = self.github_service.upload_file(file_path)
            logger.info(f"📤 GitHub 上传成功: {github_url}")
            
            # 2. 获取页面内容转换为 Markdown
            md_content = self.url_to_markdown(github_url)
            
            # 3. 获取页面标题
            title = self.extract_title_from_markdown(md_content)
            logger.info(f"📑 页面标题: {title}")
            
            # 如果没有提供原始 URL，则从文件名解析
            if not original_url:
                file_info = parse_filename(filename)
                original_url = file_info['original_url']
            
            # 4. 生成摘要和标签
            summary, tags = self.ai_service.generate_summary_and_tags(md_content)
            logger.info(f"📝 摘要: {summary[:100]}...")
            logger.info(f"🏷️ 标签: {', '.join(tags)}")
            
            # 5. 保存到 Notion
            notion_url = self.notion_service.save_page({
                'title': title,
                'original_url': original_url,
                'snapshot_url': github_url,
                'summary': summary,
                'tags': tags,
                'created_at': time.time()
            })
            logger.info(f"📓 Notion 保存成功")
            
            # 6. 发送 Telegram 通知
            notification = (
                f"✨ 新的网页剪藏\n\n"
                f"📑 {title}\n\n"
                f"📝 {summary}\n\n"
                f"🔗 原始链接：{original_url}\n"
                f"📚 快照链接：{github_url}"
            )
            await self.telegram_service.send_notification(notification)
            
            logger.info("=" * 50)
            logger.info("✨ 网页剪藏处理完成!")
            logger.info(f"📍 原始链接: {original_url}")
            logger.info(f"🔗 GitHub预览: {github_url}")
            logger.info(f"📚 Notion笔记: {notion_url}")
            logger.info("=" * 50)
            
            return {
                "status": "success",
                "github_url": github_url,
                "notion_url": notion_url
            }
            
        except Exception as e:
            error_msg = f"❌ 处理失败: {str(e)}"
            logger.error(error_msg)
            logger.error("=" * 50)
            
            # 尝试发送失败通知
            try:
                await self.telegram_service.send_notification(error_msg)
            except:
                pass
                
            raise
            
    def url_to_markdown(self, url: str, max_retries: int = 30) -> str:
        """
        将 URL 转换为 Markdown
        
        Args:
            url: 页面 URL
            max_retries: 最大重试次数
            
        Returns:
            str: Markdown 内容
        """
        try:
            # 首先尝试使用 r.jina.ai 服务
            for attempt in range(max_retries):
                try:
                    md_url = f"https://r.jina.ai/{url}"
                    response = requests.get(md_url, timeout=30)
                    if response.status_code == 200:
                        return response.text
                except Exception as e:
                    logger.debug(f"r.jina.ai 转换失败 (尝试 {attempt+1}): {str(e)}")
                    
                # 休眠后重试
                time.sleep(10)
                
            # 如果 r.jina.ai 失败，使用本地解析
            logger.info("r.jina.ai 转换失败，使用本地解析...")
            return self.extract_content_from_html(url)
            
        except Exception as e:
            logger.error(f"URL 转换为 Markdown 失败: {str(e)}")
            # 失败时仍返回网页 URL 作为内容
            return f"Title: {url} \n\n Content could not be extracted."
    
    def extract_title_from_markdown(self, md_content: str) -> str:
        """
        从 Markdown 内容提取标题
        
        Args:
            md_content: Markdown 内容
            
        Returns:
            str: 页面标题
        """
        # 查找 Title 行
        lines = md_content.splitlines()
        for line in lines:
            if line.startswith("Title:"):
                return line.replace("Title:", "").strip()
                
        # 如果找不到，查找第一个 Markdown 标题
        for line in lines:
            if line.startswith("# "):
                return line.replace("#", "").strip()
                
        return "未知标题"
    
    def extract_content_from_html(self, url: str, max_retries: int = 60) -> str:
        """
        从 HTML 页面提取内容
        
        Args:
            url: 页面 URL
            max_retries: 最大重试次数
            
        Returns:
            str: 提取的内容
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 获取标题
                    title = self._extract_title_from_soup(soup) or os.path.basename(url)
                    
                    # 提取正文内容
                    html2markdown = html2text.HTML2Text()
                    html2markdown.ignore_links = True
                    html2markdown.ignore_images = True
                    content = html2markdown.handle(soup.prettify())
                    
                    return f"Title: {title} \n\n {content}"
                    
            except Exception as e:
                logger.debug(f"HTML 提取失败 (尝试 {attempt+1}): {str(e)}")
                
            # 休眠后重试
            time.sleep(5)
            
        return f"Title: {os.path.basename(url)} \n\n Content could not be extracted."
    
    def _extract_title_from_soup(self, soup: BeautifulSoup) -> str:
        """从 BeautifulSoup 对象提取标题"""
        # 优先使用 title 标签
        if soup.title:
            return soup.title.string
            
        # 其次使用 h1 标签
        if soup.h1:
            return soup.h1.get_text(strip=True)
            
        # 最后尝试其他标题标签
        for tag in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if soup.find(tag):
                return soup.find(tag).get_text(strip=True)
                
        return None