import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения из .env файла
env_path = Path('.') / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

# Получаем настройки из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
MYMEMORY_EMAIL = os.getenv('MYMEMORY_EMAIL')

# Настройки часового пояса
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')

# Настройки расписания
DEFAULT_SCHEDULE = {
    "monday": ["09:00", "12:00", "15:00", "18:00", "21:00"],
    "tuesday": ["09:00", "12:00", "15:00", "18:00", "21:00"],
    "wednesday": ["09:00", "12:00", "15:00", "18:00", "21:00"],
    "thursday": ["09:00", "12:00", "15:00", "18:00", "21:00"],
    "friday": ["09:00", "12:00", "15:00", "18:00", "21:00"],
    "saturday": ["12:00", "18:00"],
    "sunday": ["12:00", "18:00"]
}

# Загружаем расписание из .env или используем значение по умолчанию
schedule_str = os.getenv('SCHEDULE')
if schedule_str:
    try:
        SCHEDULE = json.loads(schedule_str)
    except json.JSONDecodeError:
        print("Ошибка в формате JSON расписания. Используется значение по умолчанию.")
        SCHEDULE = DEFAULT_SCHEDULE
else:
    SCHEDULE = DEFAULT_SCHEDULE

# URL для API
ZENQUOTES_API_URL = 'https://zenquotes.io/api/random'
MYMEMORY_API_URL = 'https://api.mymemory.translated.net/get'

# Проверка необходимых настроек
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment variables!")

if not TELEGRAM_CHANNEL_ID:
    raise ValueError("TELEGRAM_CHANNEL_ID not set in environment variables!") 