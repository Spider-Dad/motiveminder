import logging
import os
import telegram
from config.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from services.quotes_service import Quote

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        self.channel_id = TELEGRAM_CHANNEL_ID
        logger.info(f"Telegram bot initialized for channel {self.channel_id}")
        
    def send_quote(self, quote: Quote, translated_text: str = None, image_path: str = None):
        """
        Отправляет цитату в Telegram канал с изображением (если доступно)
        
        :param quote: Объект цитаты
        :param translated_text: Переведенный текст цитаты
        :param image_path: Путь к изображению (если есть)
        :return: True в случае успеха, False в случае ошибки
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
            
            # Если есть изображение, отправляем фото с подписью
            if image_path and os.path.exists(image_path):
                logger.info(f"Отправка изображения с цитатой из {image_path}")
                
                with open(image_path, 'rb') as photo:
                    self.bot.send_photo(
                        chat_id=self.channel_id,
                        photo=photo,
                        caption=message,
                        parse_mode=telegram.ParseMode.MARKDOWN
                    )
                
                # Удаляем временный файл с изображением
                try:
                    os.unlink(image_path)
                    logger.info(f"Временный файл {image_path} удален")
                except Exception as e:
                    logger.warning(f"Не удалось удалить временный файл {image_path}: {e}")
            else:
                # Если изображения нет, отправляем только текст
                logger.info("Отправка цитаты без изображения")
                self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
            
            logger.info(f"Цитата отправлена в канал {self.channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке цитаты в Telegram: {e}")
            return False 