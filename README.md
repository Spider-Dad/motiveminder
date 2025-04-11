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
# Модель GigaChat для генерации изображений (по умолчанию: GigaChat-Max)
GIGACHAT_MODEL=GigaChat-Max
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

## Работа с часовыми поясами

Бот использует библиотеку `pytz` для корректной работы с часовыми поясами и не зависит от системного времени сервера:

- Переменная `TIMEZONE` определяет, в каком часовом поясе указано время в расписании `SCHEDULE`
- Все преобразования времени происходят автоматически
- Бот будет отправлять сообщения в одно и то же время по часовому поясу, указанному в `TIMEZONE`, независимо от того, в каком часовом поясе находится сервер
- При переходе на летнее/зимнее время корректировки также происходят автоматически

Например, если указано:
- `TIMEZONE=Europe/Moscow` (UTC+3)
- `SCHEDULE=monday:0900` (9:00 по московскому времени)

То сообщения будут отправляться в 9:00 по московскому времени вне зависимости от часового пояса сервера:
- На сервере с UTC+0: задача выполнится в 6:00 по серверному времени
- На сервере с UTC-5: задача выполнится в 1:00 по серверному времени
- На сервере с UTC+8: задача выполнится в 14:00 по серверному времени

## Запуск

```
python main.py
```

## Тестирование

Проект содержит комплексный набор тестов, покрывающих все основные компоненты:

```
pytest                 # Запуск всех тестов
pytest -v              # Подробный вывод
pytest --cov=.         # Тесты с отчетом о покрытии кода
```

Виды тестов:
- **Юнит-тесты**: тестирование отдельных компонентов
  - `test_image_service.py` - тесты сервиса генерации изображений
  - `test_quotes_service.py` - тесты сервиса получения цитат
  - `test_scheduler.py` - тесты планировщика задач
  - `test_telegram_bot.py` - тесты Telegram бота
  - `test_translator_service.py` - тесты сервиса перевода

- **Интеграционные тесты**: тестирование взаимодействия между компонентами
  - `test_integration.py` - общие интеграционные тесты
  - `test_config_integration.py` - тесты интеграции конфигурации
  - `test_env_config_integration.py` - тесты интеграции переменных окружения
  - `test_main_integration.py` - тесты интеграции основного модуля
  - `test_scheduler_integration.py` - тесты интеграции планировщика

Общее покрытие кода тестами составляет более 90%

## Генерация изображений

Для генерации изображений используется GigaChat API:

1. По умолчанию используется модель `GigaChat-Max` для лучшего качества
2. Если генерация не удалась, автоматически выполняется повторная попытка с базовой моделью `GigaChat`
3. Для отключения генерации изображений установите `ENABLE_IMAGE_GENERATION=false`

## Развертывание на Amvera

Проект можно развернуть на платформе [Amvera](https://amvera.ru) с помощью файла конфигурации `amvera.yaml`:

1. Создайте новый проект на Amvera
2. Подключите репозиторий GitHub к проекту
3. Amvera автоматически определит файл `amvera.yaml` и настроит проект
4. Добавьте переменные окружения в настройках проекта Amvera (те же, что и в файле `.env`)
5. Запустите приложение

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
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Общие фикстуры для тестов
│   ├── test_config_integration.py    # Тесты интеграции конфигурации
│   ├── test_env_config_integration.py # Тесты интеграции переменных окружения
│   ├── test_integration.py  # Общие интеграционные тесты
│   ├── test_main_integration.py # Тесты интеграции основного модуля
│   ├── test_scheduler_integration.py # Тесты интеграции планировщика
│   ├── test_image_service.py # Тесты сервиса изображений
│   ├── test_quotes_service.py # Тесты сервиса цитат
│   ├── test_scheduler.py    # Тесты планировщика
│   ├── test_telegram_bot.py # Тесты Telegram бота
│   └── test_translator_service.py # Тесты сервиса перевода
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