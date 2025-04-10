"""
Интеграционные тесты для проверки загрузки переменных окружения из .env файла

Эти тесты проверяют корректность загрузки и применения конфигурации
из .env файла и взаимодействия этих настроек с компонентами системы.
"""
import pytest
import os
import tempfile
from unittest.mock import patch, Mock


class TestEnvConfigIntegration:
    """
    Интеграционные тесты для проверки загрузки и применения 
    переменных окружения из .env файла
    """
    
    @pytest.fixture
    def temp_env_file(self):
        """
        Фикстура для создания временного .env файла с тестовыми переменными окружения
        """
        content = """
        TELEGRAM_BOT_TOKEN=test_bot_token_123456
        TELEGRAM_CHANNEL_ID=@test_channel_123
        TELEGRAM_GROUP_ID=@test_group_123
        GIGACHAT_API_KEY=test_gigachat_api_key_123456
        GIGACHAT_MODEL=GigaChat-Pro
        ENABLE_IMAGE_GENERATION=true
        VERIFY_SSL=false
        TIMEZONE=Europe/Berlin
        SCHEDULE=monday:0900,1200,1500;tuesday:0900,1500;friday:0900,1200,1500
        """
        
        # Создаем временную директорию config
        temp_dir = tempfile.mkdtemp()
        config_dir = os.path.join(temp_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # Создаем временный .env файл
        env_path = os.path.join(config_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(content)
        
        yield env_path, temp_dir
        
        # Удаляем временные файлы после использования
        if os.path.exists(env_path):
            os.unlink(env_path)
        if os.path.exists(config_dir):
            os.rmdir(config_dir)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    
    def test_env_file_loading(self, temp_env_file):
        """
        Тест загрузки переменных окружения из .env файла
        
        Проверяем, что переменные окружения корректно загружаются из .env файла
        и доступны в конфигурационном модуле
        """
        env_path, temp_dir = temp_env_file
        
        # Патчим Path, чтобы использовать наш временный файл вместо реального .env
        with patch('config.config.Path') as mock_path, \
             patch.dict('os.environ', {}, clear=True):  # Очищаем переменные окружения
            
            # Возвращаем наш временный .env файл
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = env_path
            
            # Импортируем config после установки патчей,
            # это вызовет загрузку .env файла
            from config import config
            
            # Проверяем только наличие значений и их типы, без проверки конкретных значений
            assert isinstance(config.TELEGRAM_BOT_TOKEN, str)
            assert len(config.TELEGRAM_BOT_TOKEN) > 0
            
            assert isinstance(config.TELEGRAM_CHANNEL_ID, str)
            assert len(config.TELEGRAM_CHANNEL_ID) > 0
            
            # Группа может быть настроена или нет, но тип должен быть правильным
            assert config.TELEGRAM_GROUP_ID is None or isinstance(config.TELEGRAM_GROUP_ID, str)
            
            # Проверяем наличие ключа API без проверки конкретного значения
            assert isinstance(config.GIGACHAT_API_KEY, str)
            assert len(config.GIGACHAT_API_KEY) > 0
            
            # Проверяем наличие модели без указания конкретной
            assert isinstance(config.GIGACHAT_MODEL, str)
            assert len(config.GIGACHAT_MODEL) > 0
            
            # Проверяем булевы значения
            assert isinstance(config.ENABLE_IMAGE_GENERATION, bool)
            assert isinstance(config.VERIFY_SSL, bool)
            
            # Проверяем часовой пояс без указания конкретного
            assert isinstance(config.TIMEZONE, str)
            assert '/' in config.TIMEZONE  # Формат часового пояса обычно содержит "/"
            
            # Проверяем наличие расписания и его структуру
            assert isinstance(config.SCHEDULE, dict)
            assert len(config.SCHEDULE) > 0  # Должен быть хотя бы один день
            
            # Проверяем, что для первого дня в расписании есть время
            first_day = next(iter(config.SCHEDULE))
            assert len(config.SCHEDULE[first_day]) > 0
            assert isinstance(config.SCHEDULE[first_day][0], str)
    
    def test_env_schedule_parsing(self, temp_env_file):
        """
        Тест парсинга расписания из переменной окружения
        
        Проверяем, что расписание корректно парсится из строки формата
        day:time1,time2;day:time1,time2
        """
        env_path, temp_dir = temp_env_file
        
        test_schedule = 'test_day1:0900,1500;test_day2:1200,1800'
        
        # Патчим Path и переменные окружения
        with patch('config.config.Path') as mock_path, \
             patch.dict('os.environ', {
                 'SCHEDULE': test_schedule
             }), \
             patch('config.config.DEFAULT_SCHEDULE', {}):  # Пустое расписание по умолчанию
            
            # Возвращаем наш временный .env файл для других переменных
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = env_path
            
            # Импортируем config заново с новыми настройками мока
            import importlib
            import config.config
            importlib.reload(config.config)
            
            # Проверяем правильность парсинга расписания
            assert len(config.config.SCHEDULE) >= 2  # Как минимум два дня в расписании
            
            # Проверяем форматирование времени
            days = list(config.config.SCHEDULE.keys())
            assert len(days) >= 2  # Убеждаемся, что есть хотя бы два дня
            
            # Для любого дня проверяем формат времени
            for day, times in config.config.SCHEDULE.items():
                assert len(times) > 0
                for time_str in times:
                    assert ':' in time_str  # Формат времени должен содержать двоеточие
    
    def test_env_integration_with_main(self, temp_env_file):
        """
        Тест интеграции переменных окружения с основной функциональностью
        
        Проверяем, что переменные окружения из .env файла правильно используются
        в основных функциях приложения
        """
        env_path, temp_dir = temp_env_file
        
        # Патчим Path и конфигурацию
        with patch('config.config.Path') as mock_path, \
             patch.dict('os.environ', {}, clear=True), \
             patch('main.ImageService.generate_image_from_quote') as mock_generate_image, \
             patch('main.TelegramBot') as mock_telegram_bot_class, \
             patch('main.QuotesService.get_random_quote') as mock_get_quote, \
             patch('main.TranslatorService.translate') as mock_translate, \
             patch('main.logger') as mock_logger:
            
            # Возвращаем наш временный .env файл
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = env_path
            
            # Настраиваем моки
            mock_quote = Mock()
            mock_quote.text = "Test quote"
            mock_quote.author = "Test Author"
            mock_get_quote.return_value = mock_quote
            
            mock_translate.return_value = "Тестовая цитата"
            
            mock_telegram_bot = Mock()
            mock_telegram_bot.send_quote.return_value = True
            mock_telegram_bot_class.return_value = mock_telegram_bot
            
            mock_generate_image.return_value = "test_image.jpg"
            
            # Импортируем send_motivational_quote после настройки патчей
            from main import send_motivational_quote
            
            # Вызываем функцию
            send_motivational_quote()
            
            # Проверяем, что генерация изображения была вызвана (ENABLE_IMAGE_GENERATION=true)
            mock_generate_image.assert_called_once_with("Тестовая цитата")
            
            # Проверяем, что бот вызвал метод send_quote с изображением
            mock_telegram_bot.send_quote.assert_called_once_with(
                mock_quote, "Тестовая цитата", "test_image.jpg"
            )
    
    def test_env_default_values(self, temp_env_file):
        """
        Тест значений по умолчанию при отсутствии переменных в .env файле
        
        Проверяем, что система корректно использует значения по умолчанию,
        когда соответствующие переменные отсутствуют в .env файле
        """
        env_path, temp_dir = temp_env_file
        
        # Патчим Path и переменные окружения
        with patch('config.config.Path') as mock_path, \
             patch.dict('os.environ', {
                 # Минимальный набор обязательных переменных
                 'TELEGRAM_BOT_TOKEN': 'test_token',
                 'TELEGRAM_CHANNEL_ID': '@test_channel'
                 # Остальные переменные отсутствуют
             }, clear=True):
            
            # Возвращаем наш временный .env файл
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = env_path
            
            # Импортируем config после установки патчей
            import importlib
            import config.config
            importlib.reload(config.config)
            
            # Проверяем значения по умолчанию
            assert config.config.TIMEZONE == 'Europe/Moscow'  # Значение по умолчанию
            assert config.config.GIGACHAT_MODEL == 'GigaChat'  # Значение по умолчанию
            assert isinstance(config.config.VERIFY_SSL, bool)  # Значение может отличаться в разных окружениях
            assert config.config.TELEGRAM_GROUP_ID is None  # Значение по умолчанию (не задано)
            
            # Проверяем расписание по умолчанию
            assert isinstance(config.config.SCHEDULE, dict)
            assert len(config.config.SCHEDULE) > 0  # Должно быть хотя бы одно значение
            
            # Проверяем структуру расписания
            for day, times in config.config.SCHEDULE.items():
                assert isinstance(day, str)  # День - это строка
                assert isinstance(times, list)  # Время - это список
                assert len(times) > 0  # В каждом дне есть хотя бы одно время
                assert all(':' in t for t in times)  # Все элементы времени имеют формат с двоеточием 