# MotivateMe Bot 🚀

Telegram-бот, который автоматически отправляет мотивационные цитаты в канал по расписанию. Бот получает случайные цитаты из внешнего API (ZenQuotes), переводит их на русский язык с помощью MyMemory API и отправляет в Telegram-канал через Telegram Bot API.

## Возможности

- 📝 Получение случайных мотивационных цитат
- 🌍 Перевод цитат на русский язык
- 📱 Отправка цитат в Telegram-канал по расписанию
- ⏰ Настраиваемая периодичность отправки

## Технологии

- 🐍 Python
- 🤖 python-telegram-bot
- ⏱️ schedule
- 🌐 API (Telegram Bot API, ZenQuotes API, MyMemory API)

## Установка и настройка

1. Клонировать репозиторий:
```
git clone https://github.com/yourusername/MotivateMe_bot.git
cd MotivateMe_bot
```

2. Установить зависимости:
```
pip install -r requirements.txt
```

3. Создать файл с переменными окружения:
```
cp config/.env.example config/.env
```

4. Заполнить файл `.env` своими данными:
```
# Токен Telegram бота, полученный от @BotFather
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# ID канала для отправки цитат
TELEGRAM_CHANNEL_ID=@your_channel_id

# Email для MyMemory API (опционально, для увеличения лимита запросов)
MYMEMORY_EMAIL=your_email@example.com

# Расписание отправки цитат (минуты)
SCHEDULE_MINUTES=30
```

## Запуск

```
python main.py
```

## Структура проекта

```
MotivateMe_bot/
├── bot/
│   └── telegram_bot.py      # Взаимодействие с Telegram Bot API
├── config/
│   ├── .env                 # Переменные окружения
│   ├── .env.example         # Пример .env файла
│   └── config.py            # Загрузка конфигурации
├── services/
│   ├── quotes_service.py    # Получение цитат
│   └── translator_service.py # Перевод цитат
├── utils/
│   └── scheduler.py         # Планировщик задач
├── main.py                  # Основной файл для запуска
└── requirements.txt         # Зависимости проекта
```

## Создание бота в Telegram

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## Создание канала в Telegram

1. Создайте новый канал в Telegram
2. Добавьте вашего бота в качестве администратора с правами на публикацию сообщений
3. Укажите username канала (с символом @) или его ID в файле `.env`

## Лицензия

MIT 