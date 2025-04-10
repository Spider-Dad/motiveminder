"""
Интеграционные тесты для проверки взаимодействия конфигурации с компонентами системы

Эти тесты проверяют, как различные компоненты системы работают с конфигурационными параметрами,
и как изменение конфигурации влияет на поведение системы.
"""
import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from services.image_service import ImageService
from bot.telegram_bot import TelegramBot
from utils.scheduler import Scheduler
from config.config import ENABLE_IMAGE_GENERATION
from datetime import datetime


class TestConfigIntegration:
    """Интеграционные тесты для проверки работы конфигурации с компонентами системы"""
    
    @pytest.fixture
    def temp_token_file(self):
        """Фикстура для создания временного файла с токеном"""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b"test_token_content")
        temp_file.close()
        yield temp_file.name
        # Удаляем файл после использования
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    def test_image_service_config_integration(self, temp_token_file):
        """
        Тест интеграции ImageService с конфигурационными параметрами
        
        Проверяем, что ImageService корректно работает с параметрами конфигурации,
        такими как GIGACHAT_API_KEY, GIGACHAT_MODEL и VERIFY_SSL
        """
        # Патчим только конфигурационные параметры
        with patch('services.image_service.GIGACHAT_API_KEY', 'test_api_key'), \
             patch('services.image_service.GIGACHAT_MODEL', 'GigaChat-Test'), \
             patch('services.image_service.VERIFY_SSL', False), \
             patch('services.image_service.requests.post') as mock_post, \
             patch('services.image_service.requests.get') as mock_get:
            
            # Настраиваем моки для запросов
            mock_post_response = Mock()
            mock_post_response.json.return_value = {"access_token": "test_token"}
            mock_post.return_value = mock_post_response
            
            # Определяем аргументы, которые используются в реальном запросе
            expected_args = {
                'data': {
                    'scope': 'GIGACHAT_API_PERS',
                    'authentication': {
                        'type': 'API_KEY',
                        'api_key': 'test_api_key'
                    }
                }
            }
            
            # Вызываем метод для получения токена
            token = ImageService.get_access_token()
            
            # Проверяем результаты и параметры запроса
            assert token == "test_token"
            
            # Проверяем, что запрос был отправлен
            mock_post.assert_called_once()
            assert mock_post.call_args[1]['verify'] is False  # VERIFY_SSL=False
            
            # Сбрасываем моки
            mock_post.reset_mock()
            
            # Настраиваем моки для генерации изображения
            mock_post_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '<img src="test-uuid" fuse="true"/>'
                    }
                }]
            }
            
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.content = b"test_image_data"
            mock_get.return_value = mock_get_response
            
            with patch.object(ImageService, 'extract_image_uuid', return_value="test-uuid"), \
                 patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                # Настраиваем мок для временного файла
                mock_file = Mock()
                mock_file.name = "test_temp_file.jpg"
                mock_tempfile.return_value = mock_file
                
                # Генерируем изображение
                image_path = ImageService.generate_image_from_quote("Test quote")
                
                # Проверяем, что изображение было успешно "сгенерировано"
                assert image_path == "test_temp_file.jpg"
                
                # Проверяем параметры запроса на генерацию изображения
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                assert 'json' in kwargs
                assert 'model' in kwargs['json']
                assert kwargs['json']['model'] == 'GigaChat-Test'  # Используется GIGACHAT_MODEL
                assert kwargs['verify'] is False  # VERIFY_SSL=False
                
                # Проверяем запрос на получение изображения
                mock_get.assert_called_once()
                args, kwargs = mock_get.call_args
                assert "test-uuid" in args[0]
                assert kwargs['verify'] is False  # VERIFY_SSL=False
    
    def test_telegram_bot_config_integration(self):
        """
        Тест интеграции TelegramBot с конфигурационными параметрами
        
        Проверяем, что TelegramBot корректно работает с параметрами конфигурации,
        такими как TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID и TELEGRAM_GROUP_ID
        """
        # Патчим конфигурационные параметры и класс telegram.Bot
        with patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_bot_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', '@test_group'), \
             patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.logger') as mock_logger:
            
            # Настраиваем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем бота
            bot = TelegramBot()
            
            # Проверяем, что бот был инициализирован с правильными параметрами
            mock_bot_class.assert_called_once_with(token='test_bot_token')
            assert bot.channel_id == '@test_channel'
            assert bot.group_id == '@test_group'
            
            # Проверяем логирование
            mock_logger.info.assert_called_once_with(
                "Telegram bot initialized for channel @test_channel and group @test_group"
            )
    
    def test_enable_image_generation_integration(self):
        """
        Тест влияния параметра ENABLE_IMAGE_GENERATION на работу системы
        
        Проверяем, что при ENABLE_IMAGE_GENERATION=False генерация изображений не происходит
        """
        # Патчим параметр ENABLE_IMAGE_GENERATION и функцию send_motivational_quote
        with patch('main.ENABLE_IMAGE_GENERATION', False), \
             patch('main.QuotesService.get_random_quote') as mock_get_quote, \
             patch('main.TranslatorService.translate') as mock_translate, \
             patch('main.ImageService.generate_image_from_quote') as mock_generate_image, \
             patch('main.TelegramBot') as mock_telegram_bot_class, \
             patch('main.logger') as mock_logger:
            
            # Настраиваем моки
            mock_quote = Mock()
            mock_quote.text = "Test quote"
            mock_quote.author = "Test Author"
            mock_get_quote.return_value = mock_quote
            
            mock_translate.return_value = "Тестовая цитата"
            
            mock_telegram_bot = Mock()
            mock_telegram_bot.send_quote.return_value = True
            mock_telegram_bot_class.return_value = mock_telegram_bot
            
            # Импортируем функцию send_motivational_quote только после настройки патчей
            from main import send_motivational_quote
            
            # Вызываем функцию
            send_motivational_quote()
            
            # Проверяем, что ImageService.generate_image_from_quote не вызывался
            mock_generate_image.assert_not_called()
            
            # Проверяем, что telegram_bot.send_quote был вызван без изображения
            mock_telegram_bot.send_quote.assert_called_once_with(
                mock_quote, "Тестовая цитата", None
            )
    
    def test_scheduler_timezone_config_integration(self):
        """
        Тест интеграции Scheduler с конфигурационным параметром TIMEZONE
        
        Проверяем, что Scheduler корректно использует заданный часовой пояс
        """
        # Патчим параметры и зависимости
        test_timezone = 'Europe/London'  # GMT+0
        with patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch('utils.scheduler.SCHEDULE', {'monday': ['12:00']}), \
             patch('utils.scheduler.schedule') as mock_schedule_lib, \
             patch('utils.scheduler.logger') as mock_logger:
            
            # Функция для теста
            mock_job = Mock()
            
            # Создаем экземпляр планировщика
            scheduler = Scheduler(mock_job)
            
            # Проверяем, что часовой пояс был корректно установлен
            assert scheduler.timezone.zone == test_timezone
            
            # Проверяем метод конвертации времени в UTC
            # Для London (GMT+0) в зимнее время 12:00 -> 12:00 UTC
            with patch('utils.scheduler.datetime') as mock_datetime:
                # Фиксируем дату для предсказуемости (зимнее время)
                mock_now = datetime(2024, 1, 1, 0, 0)
                mock_datetime.now.return_value = mock_now
                mock_datetime.strptime.side_effect = datetime.strptime
                
                # Проверяем конвертацию времени
                utc_time = scheduler._convert_to_utc("12:00")
                assert utc_time == "12:00"  # Для London GMT+0 конвертация не меняет время 