import logging
import telegram
from config.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from services.quotes_service import Quote

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        self.channel_id = TELEGRAM_CHANNEL_ID
        logger.info(f"Telegram bot initialized for channel {self.channel_id}")
        
    def send_quote(self, quote: Quote, translated_text: str = None):
        """
        Отправляет цитату в Telegram канал
        """
        try:
            # Формируем текст сообщения
            if translated_text:
                message = f'🔥 *{translated_text}*\n\n'
                message += f'🌐 "{quote.text}"\n\n'
                message += f'👤 _{quote.author}_'
            else:
                message = f'🔥 *"{quote.text}"*\n\n'
                message += f'👤 _{quote.author}_'
                
            # Отправляем сообщение
            self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            
            logger.info(f"Quote sent to channel {self.channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending quote to Telegram: {e}")
            return False 