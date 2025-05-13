import logging
import openai
from typing import Tuple, List

from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI 服务，处理内容摘要和标签生成"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = settings.OPENAI_MODEL
        self.max_retries = settings.OPENAI_MAX_RETRIES
        
    def generate_summary_and_tags(self, content: str) -> Tuple[str, List[str]]:
        """
        使用 AI 生成文本摘要和标签
        
        Args:
            content: 网页内容
            
        Returns:
            tuple: (摘要, 标签列表)
        """
        try:
            # 限制内容长度，避免发送过多令牌
            truncated_content = content[:5000] + "..." if len(content) > 5000 else content
            
            logger.info(f"使用 AI 模型 '{self.model}' 生成摘要和标签")
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 构建提示
            prompt = f"""请为以下网页(已转换为Markdown格式)内容生成简短摘要和相关标签。 
            请严格按照以下格式返回(英文网页请以中文返回)：
            摘要：[100字以内的摘要]
            标签：tag1，tag2，tag3，tag4，tag5

            网页(已转换为markdown格式)内容：
            {truncated_content}"""
            
            # 重试机制
            for attempt in range(self.max_retries):
                try:
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    result = response.choices[0].message.content
                    
                    # 解析结果
                    return self._parse_ai_response(result)
                    
                except Exception as e:
                    logger.warning(f"AI 调用失败 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                    if attempt < self.max_retries - 1:
                        continue
                    raise
                    
        except Exception as e:
            logger.error(f"生成摘要和标签失败: {str(e)}")
            return "无法生成摘要", ["未分类"]
            
    def _parse_ai_response(self, response: str) -> Tuple[str, List[str]]:
        """
        解析 AI 响应
        
        Args:
            response: AI 响应文本
            
        Returns:
            tuple: (摘要, 标签列表)
        """
        try:
            parts = response.split('\n')
            
            # 查找摘要行
            summary_part = next((p for p in parts if p.startswith('摘要：')), None)
            if not summary_part:
                return "无法解析摘要", ["未分类"]
                
            # 查找标签行
            tags_part = next((p for p in parts if p.startswith('标签：')), None)
            if not tags_part:
                return summary_part.replace('摘要：', '').strip(), ["未分类"]
                
            # 处理摘要
            summary = summary_part.replace('摘要：', '').strip()
            
            # 处理标签
            tags_str = tags_part.replace('标签：', '').strip()
            tags = [
                tag.strip()[:20]  # 限制标签长度
                for tag in tags_str.replace('，', ',').split(',')
                if tag.strip()
            ]
            
            return summary, tags
            
        except Exception as e:
            logger.error(f"解析 AI 响应失败: {str(e)}")
            return "无法解析摘要", ["未分类"]