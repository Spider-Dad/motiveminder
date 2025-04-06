import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения из .env файла
env_path = Path('.') / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

# Получаем настройки из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
MYMEMORY_EMAIL = os.getenv('MYMEMORY_EMAIL')

# Настройки расписания
SCHEDULE_MINUTES = int(os.getenv('SCHEDULE_MINUTES', 30))

# URL для API
ZENQUOTES_API_URL = 'https://zenquotes.io/api/random'
MYMEMORY_API_URL = 'https://api.mymemory.translated.net/get'

# Проверка необходимых настроек
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment variables!")

if not TELEGRAM_CHANNEL_ID:
    raise ValueError("TELEGRAM_CHANNEL_ID not set in environment variables!") 