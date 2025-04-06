import logging
import pytz
import os
from datetime import datetime
from services.quotes_service import QuotesService
from services.translator_service import TranslatorService
from services.image_service import ImageService
from bot.telegram_bot import TelegramBot
from utils.scheduler import Scheduler
from config.config import TIMEZONE, ENABLE_IMAGE_GENERATION

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def send_motivational_quote():
    """
    Основная функция для получения, перевода и отправки мотивационной цитаты
    """
    # Получаем текущее время в заданном часовом поясе
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    logger.info(f"Запуск отправки мотивационной цитаты в {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Получаем случайную цитату
    quote = QuotesService.get_random_quote()
    logger.info(f"Получена цитата: {quote}")
    
    # Переводим цитату на русский язык
    translated_text = TranslatorService.translate(quote.text)
    logger.info(f"Переведенная цитата: {translated_text}")
    
    # Генерируем изображение на основе цитаты (если включено)
    image_path = None
    if ENABLE_IMAGE_GENERATION:
        logger.info("Генерация изображения на основе цитаты...")
        image_path = ImageService.generate_image_from_quote(translated_text)
        if image_path:
            logger.info(f"Изображение успешно создано: {image_path}")
        else:
            logger.warning("Не удалось создать изображение для цитаты")
    
    # Отправляем цитату с изображением (если есть) в Telegram
    telegram_bot = TelegramBot()
    result = telegram_bot.send_quote(quote, translated_text, image_path)
    
    if result:
        logger.info("Цитата успешно отправлена")
    else:
        logger.error("Не удалось отправить цитату")

def main():
    """
    Основная функция запуска бота
    """
    try:
        logger.info("Запуск MotivateMe бота")
        logger.info(f"Используемый часовой пояс: {TIMEZONE}")
        logger.info(f"Генерация изображений: {'включена' if ENABLE_IMAGE_GENERATION else 'отключена'}")
        
        # Создаем планировщик и запускаем его
        scheduler = Scheduler(send_motivational_quote)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.error(f"Бот остановлен из-за ошибки: {e}")

if __name__ == "__main__":
    main() 