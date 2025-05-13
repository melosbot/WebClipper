import logging
import re

logger = logging.getLogger(__name__)

def parse_filename(filename: str) -> dict:
    """
    从文件名解析URL
    filename format: {random_prefix}_url.html (其中url中的/被替换为$)
    
    Args:
        filename: 文件名
        
    Returns:
        dict: 包含解析结果的字典
    """
    try:
        # 移除 .html 后缀
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # 移除随机前缀（如果存在）
        if '_' in name_without_ext:
            name_without_ext = name_without_ext.split('_', 1)[1]
        
        # 恢复URL中的斜杠
        original_url = name_without_ext.replace('$', '/')
        
        # 如果解析出的 URL 合理，记录日志
        if '.' in original_url:
            logger.info(f"从文件名解析出原始URL: {original_url}")
        else:
            logger.warning(f"从文件名解析的URL可能不正确: {original_url}")
        
        return {
            'original_url': original_url
        }
    except Exception as e:
        logger.error(f"解析文件名失败: {str(e)}")
        return {
            'original_url': ''
        }

def sanitize_filename(filename: str) -> str:
    """
    净化文件名，确保文件名符合要求
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 净化后的文件名
    """
    # 移除不安全字符
    sanitized = re.sub(r'[^\w\-. ]', '_', filename)
    
    # 限制长度
    if len(sanitized) > 240:  # 安全边界，小于文件系统通常的 255 限制
        sanitized = sanitized[:240]
    
    return sanitized