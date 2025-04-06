import logging
from services.quotes_service import QuotesService
from services.translator_service import TranslatorService
from bot.telegram_bot import TelegramBot
from utils.scheduler import Scheduler

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
    logger.info("Starting to send motivational quote")
    
    # Получаем случайную цитату
    quote = QuotesService.get_random_quote()
    logger.info(f"Retrieved quote: {quote}")
    
    # Переводим цитату на русский язык
    translated_text = TranslatorService.translate(quote.text)
    logger.info(f"Translated quote: {translated_text}")
    
    # Отправляем цитату в Telegram
    telegram_bot = TelegramBot()
    result = telegram_bot.send_quote(quote, translated_text)
    
    if result:
        logger.info("Quote successfully sent")
    else:
        logger.error("Failed to send quote")

def main():
    """
    Основная функция запуска бота
    """
    try:
        logger.info("Starting MotivateMe bot")
        
        # Создаем планировщик и запускаем его
        scheduler = Scheduler(send_motivational_quote)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")

if __name__ == "__main__":
    main() 