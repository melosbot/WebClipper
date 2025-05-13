import time
import logging
from notion_client import Client
from typing import Dict, List, Any

from app.config import settings

logger = logging.getLogger(__name__)

class NotionService:
    """处理 Notion 数据库交互"""
    
    def __init__(self):
        self.client = Client(auth=settings.NOTION_TOKEN)
        
    def save_page(self, data: Dict[str, Any]) -> str:
        """
        将内容保存到 Notion 数据库
        
        Args:
            data: 包含页面信息的字典
            
        Returns:
            str: Notion 页面 URL
        """
        try:
            logger.info(f"保存内容到 Notion: {data['title']}")
            
            # 确保标签有效
            tags = data.get('tags', [])
            if not tags:
                tags = ["未分类"]
                
            # 格式化时间
            current_time = time.strftime(
                '%Y-%m-%dT%H:%M:%S.000Z',
                time.gmtime(data['created_at'])
            )
            
            # 准备 Notion 属性
            properties = {
                "Title": {"title": [{"text": {"content": data['title']}}]},
                "OriginalURL": {"url": data['original_url'] if data['original_url'] else None},
                "SnapshotURL": {"url": data['snapshot_url']},
                "Summary": {"rich_text": [{"text": {"content": data['summary']}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in tags if tag.strip()]},
                "Created": {"date": {"start": current_time}}
            }
            
            # 创建页面
            response = self.client.pages.create(
                parent={"database_id": settings.NOTION_DATABASE_ID},
                properties=properties
            )
            
            logger.info(f"成功保存到 Notion: {response['url']}")
            return response['url']
            
        except Exception as e:
            logger.error(f"保存到 Notion 失败: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Notion API 响应: {e.response.text}")
            raise