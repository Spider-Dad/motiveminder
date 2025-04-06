# MotivateMe Bot 🚀

Telegram-бот, который автоматически отправляет мотивационные цитаты в канал по расписанию. Бот получает случайные цитаты из внешнего API (ZenQuotes), переводит их на русский язык с помощью MyMemory API и отправляет в Telegram-канал через Telegram Bot API.

## Возможности

- 📝 Получение случайных мотивационных цитат
- 🌍 Перевод цитат на русский язык
- 📱 Отправка цитат в Telegram-канал по расписанию
- 🎨 Генерация изображений для цитат с помощью GigaChat API
- ⏰ Настраиваемая периодичность отправки

## Технологии

- 🐍 Python
- 🤖 python-telegram-bot
- ⏱️ schedule
- 🌐 API (Telegram Bot API, ZenQuotes API, MyMemory API, GigaChat API)

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

# Ключ API GigaChat в формате Base64 (client_id:client_secret)
GIGACHAT_API_KEY=your_base64_encoded_gigachat_key
ENABLE_IMAGE_GENERATION=true
VERIFY_SSL=false

# Настройки часового пояса и расписания
TIMEZONE=Europe/Moscow
SCHEDULE={"monday":["09:00","12:00","15:00","18:00","21:00"],"tuesday":["09:00","12:00","15:00","18:00","21:00"],"wednesday":["09:00","12:00","15:00","18:00","21:00"],"thursday":["09:00","12:00","15:00","18:00","21:00"],"friday":["09:00","12:00","15:00","18:00","21:00"],"saturday":["12:00","18:00"],"sunday":["12:00","18:00"]}
```

## Запуск

```
python main.py
```

## Развертывание на Amvera

Проект можно развернуть на платформе [Amvera](https://amvera.ru) с помощью файла конфигурации `amvera.yaml`:

1. Создайте новый проект на Amvera
2. Подключите репозиторий GitHub к проекту
3. Amvera автоматически определит файл `amvera.yaml` и настроит проект
4. Добавьте переменные окружения в настройках проекта Amvera (те же, что и в файле `.env`)
5. Запустите приложение

**Важно:** Все данные, которые должны сохраняться между перезапусками, должны храниться в директории `/data`, которая указана в `persistenceMount` в файле `amvera.yaml`.

## Структура проекта

```
MotivateMe_bot/
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py      # Взаимодействие с Telegram Bot API
├── config/
│   ├── .env                 # Переменные окружения
│   ├── .env.example         # Пример .env файла
│   └── config.py            # Загрузка конфигурации
├── services/
│   ├── __init__.py
│   ├── quotes_service.py    # Получение цитат
│   ├── translator_service.py # Перевод цитат
│   └── image_service.py     # Генерация изображений
├── utils/
│   ├── __init__.py
│   └── scheduler.py         # Планировщик задач
├── amvera.yaml              # Конфигурация для Amvera
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