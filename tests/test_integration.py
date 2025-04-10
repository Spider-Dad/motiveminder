"""
Интеграционные тесты для системы MotivateMe

Эти тесты проверяют взаимодействие между различными компонентами системы:
- QuotesService
- TranslatorService
- ImageService
- TelegramBot
"""
import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from services.quotes_service import QuotesService, Quote
from services.translator_service import TranslatorService
from services.image_service import ImageService
from bot.telegram_bot import TelegramBot
from config.config import ENABLE_IMAGE_GENERATION


class TestQuoteToTelegramFlow:
    """Интеграционные тесты для проверки потока от получения цитаты до отправки в Telegram"""
    
    @pytest.fixture
    def mock_quote(self):
        """Фикстура для создания реальной цитаты без использования API"""
        return Quote(
            text="Life is what happens when you're busy making other plans.",
            author="John Lennon"
        )
    
    @pytest.fixture
    def translated_text(self):
        """Фикстура для переведенного текста"""
        return "Жизнь — это то, что происходит, когда вы заняты другими планами."
    
    @pytest.fixture
    def temp_image_file(self):
        """Фикстура для создания временного файла изображения"""
        # Создаем временный файл с простым содержимым
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(b"Test image content")
        temp_file.close()
        yield temp_file.name
        # Удаляем файл после использования
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    def test_quotes_to_translator_integration(self, mock_quote):
        """
        Тест интеграции между сервисом цитат и сервисом переводов
        
        Проверяем, что полученная от QuotesService цитата может быть корректно
        обработана TranslatorService для перевода
        """
        with patch('services.translator_service.requests.get') as mock_get:
            # Настраиваем мок для сервиса перевода
            mock_response = Mock()
            mock_response.json.return_value = {
                "responseStatus": 200,
                "responseData": {
                    "translatedText": "Жизнь — это то, что происходит, когда вы заняты другими планами."
                }
            }
            mock_get.return_value = mock_response
            
            # Используем реальный QuotesService но с заглушкой get_random_quote
            with patch.object(QuotesService, 'get_random_quote', return_value=mock_quote):
                # Получаем цитату
                quote = QuotesService.get_random_quote()
                
                # Переводим текст цитаты, используя реальный TranslatorService
                translated_text = TranslatorService.translate(quote.text)
                
                # Проверяем результаты
                assert quote.text == "Life is what happens when you're busy making other plans."
                assert quote.author == "John Lennon"
                assert translated_text == "Жизнь — это то, что происходит, когда вы заняты другими планами."
                
                # Проверяем, что запрос на перевод был выполнен с правильными параметрами
                mock_get.assert_called_once()
                args, kwargs = mock_get.call_args
                assert kwargs['params']['q'] == quote.text
                assert kwargs['params']['langpair'] == 'en|ru'

    def test_translator_to_image_integration(self, translated_text, temp_image_file):
        """
        Тест интеграции между сервисом переводов и сервисом генерации изображений
        
        Проверяем, что переведенный текст может быть использован для генерации изображения
        """
        # Патчим только конкретные методы ImageService для избежания реальных вызовов API
        mock_file = Mock()
        mock_file.name = temp_image_file
        
        with patch.object(ImageService, 'get_access_token', return_value="mock_token"), \
             patch.object(ImageService, 'extract_image_uuid', return_value="mock-uuid"), \
             patch('services.image_service.requests.post') as mock_post, \
             patch('services.image_service.requests.get') as mock_get, \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            
            # Настраиваем мок для временного файла
            mock_tempfile.return_value = mock_file
            
            # Настраиваем мок для ответа API с изображением
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '<img src="mock-uuid" fuse="true"/>'
                    }
                }]
            }
            mock_post.return_value = mock_post_response
            
            # Настраиваем мок для получения содержимого изображения
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.content = b"Test image content"
            mock_get.return_value = mock_get_response
            
            # Генерируем изображение на основе переведенного текста
            image_path = ImageService.generate_image_from_quote(translated_text)
            
            # Проверяем результаты
            assert image_path == temp_image_file
            
            # Проверяем, что запросы к API были выполнены с правильными параметрами
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert kwargs['json']['messages'][1]['content'] == f"Нарисуй изображение, иллюстрирующее цитату: {translated_text}"
            
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert "mock-uuid" in args[0]

    def test_image_to_telegram_integration(self, mock_quote, translated_text, temp_image_file):
        """
        Тест интеграции между сервисом генерации изображений и отправкой в Telegram
        
        Проверяем, что цитата с переводом и сгенерированным изображением может быть
        отправлена через TelegramBot
        """
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class:
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату с переводом и изображением
            result = bot.send_quote(quote=mock_quote, translated_text=translated_text, image_path=temp_image_file)
            
            # Проверяем результаты
            assert result is True
            
            # Проверяем, что вызов send_photo был выполнен с правильными параметрами
            mock_bot.send_photo.assert_called_once()
            args, kwargs = mock_bot.send_photo.call_args
            assert kwargs['chat_id'] is not None
            assert kwargs['caption'] is not None
            assert translated_text in kwargs['caption']
            assert mock_quote.text in kwargs['caption']
            assert mock_quote.author in kwargs['caption']

    def test_full_quote_to_telegram_flow(self, mock_quote, translated_text, temp_image_file):
        """
        Полный интеграционный тест потока от получения цитаты до отправки в Telegram
        
        Этот тест имитирует полный поток, но с минимальным количеством моков,
        чтобы проверить взаимодействие между компонентами
        """
        # Патчим внешние вызовы API
        with patch.object(QuotesService, 'get_random_quote', return_value=mock_quote), \
             patch.object(TranslatorService, 'translate', return_value=translated_text), \
             patch.object(ImageService, 'generate_image_from_quote', return_value=temp_image_file), \
             patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('main.ENABLE_IMAGE_GENERATION', True):
            
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Импортируем send_motivational_quote после настройки патчей
            from main import send_motivational_quote
            
            # Вызываем функцию
            send_motivational_quote()
            
            # Проверяем, что все ожидаемые методы были вызваны
            mock_bot.send_photo.assert_called_once() 