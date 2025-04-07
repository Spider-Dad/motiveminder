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
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
MYMEMORY_EMAIL = os.getenv('MYMEMORY_EMAIL')

# Настройки для GigaChat API
GIGACHAT_API_KEY = os.getenv('GIGACHAT_API_KEY')
ENABLE_IMAGE_GENERATION = os.getenv('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true'
VERIFY_SSL = os.getenv('VERIFY_SSL', 'true').lower() == 'true'

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
        SCHEDULE = {}
        # Парсим строку формата day:time1,time2;day:time1,time2
        for day_schedule in schedule_str.split(';'):
            if ':' in day_schedule:
                day, times = day_schedule.split(':')
                # Преобразуем время из формата HHMM в HH:MM
                formatted_times = []
                for time in times.split(','):
                    if len(time) == 4:
                        formatted_time = f"{time[:2]}:{time[2:]}"
                        formatted_times.append(formatted_time)
                SCHEDULE[day.lower()] = formatted_times
        if not SCHEDULE:
            raise ValueError("Empty schedule")
    except Exception as e:
        print(f"Ошибка в формате расписания: {e}. Используется значение по умолчанию.")
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

# Проверка настроек GigaChat при включенной генерации изображений
if ENABLE_IMAGE_GENERATION and not GIGACHAT_API_KEY:
    print("ВНИМАНИЕ: GIGACHAT_API_KEY не установлен. Генерация изображений будет отключена.")
    ENABLE_IMAGE_GENERATION = False 