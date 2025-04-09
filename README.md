# MotiveMinder Bot 🚀

[![Python Tests](https://github.com/Spider-Dad/motiveminder/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Spider-Dad/motiveminder/actions/workflows/python-tests.yml)

Telegram-бот, который автоматически отправляет мотивационные цитаты в канал по расписанию. Бот получает случайные цитаты из внешнего API (ZenQuotes), переводит их на русский язык с помощью MyMemory API и отправляет в Telegram-канал через Telegram Bot API.

> **Проект основан на [telegram-quotes-bot-](https://github.com/che1nov/telegram-quotes-bot-) от [@che1nov](https://github.com/che1nov)**. Выражаю искреннюю благодарность автору за отличную идею и реализацию!

## Пример работы
Посмотреть бот в действии можно здесь: [t.me/motiveminder](https://t.me/motiveminder)   

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
git clone https://github.com/yourusername/MotiveMinder.git
cd MotiveMinder
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

# ID группы для отправки цитат (опционально)
TELEGRAM_GROUP_ID=-100your_group_id

# Email для MyMemory API (опционально, для увеличения лимита запросов)
MYMEMORY_EMAIL=your_email@example.com

# Ключ API GigaChat в формате Base64 (client_id:client_secret)
GIGACHAT_API_KEY=your_base64_encoded_gigachat_key
# Модель GigaChat для генерации изображений (по умолчанию: GigaChat)
GIGACHAT_MODEL=GigaChat
ENABLE_IMAGE_GENERATION=true
VERIFY_SSL=false

# Настройки часового пояса
TIMEZONE=Europe/Moscow

# Расписание отправки цитат
# Формат: день:время1,время2;день:время2,время2
# Дни недели: monday, tuesday, wednesday, thursday, friday, saturday, sunday
# Время в формате HHMM (24-часовой формат без двоеточия)
SCHEDULE=monday:0900,1200,1500,1800,2100;tuesday:0900,1200,1500,1800,2100;wednesday:0900,1200,1500,1800,2100;thursday:0900,1200,1500,1800,2100;friday:0900,1200,1500,1800,2100;saturday:1200,1800;sunday:1200,1800
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
MotiveMinder/
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