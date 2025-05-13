import logging
import telegram
import asyncio

from app.config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    """Telegram 通知服务"""
    
    def __init__(self):
        self.bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        
    async def send_notification(self, message: str) -> None:
        """
        发送 Telegram 通知
        
        Args:
            message: 消息内容
        """
        try:
            logger.info("发送 Telegram 通知...")
            
            # 确保消息不超过最大长度
            if len(message) > 4096:
                message = message[:4093] + "..."
                
            await self.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=telegram.constants.ParseMode.HTML  # 支持 HTML 格式
            )
            
            logger.info("Telegram 通知已发送")
            
        except Exception as e:
            logger.error(f"发送 Telegram 通知失败: {str(e)}")
            # 不抛出异常，避免因通知失败而中断主流程