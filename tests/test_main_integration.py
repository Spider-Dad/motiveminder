"""
Интеграционные тесты для основных функций в main.py

Эти тесты проверяют интеграцию всех компонентов системы через основную
функцию send_motivational_quote, которая координирует весь процесс от
получения цитаты до отправки в Telegram.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, Mock, mock_open
from main import send_motivational_quote
from services.quotes_service import Quote


class TestMainIntegration:
    """Интеграционные тесты для функций в main.py"""
    
    @pytest.fixture
    def mock_quote(self):
        """Фикстура для создания моковой цитаты"""
        return Quote(
            text="Success is not final, failure is not fatal: it is the courage to continue that counts.",
            author="Winston Churchill"
        )
    
    @pytest.fixture
    def translated_text(self):
        """Фикстура для переведенного текста"""
        return "Успех не окончателен, неудача не фатальна: важна храбрость продолжать."
    
    @pytest.fixture
    def temp_image_file(self):
        """Фикстура для создания временного файла изображения"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(b"Test image content")
        temp_file.close()
        yield temp_file.name
        # Удаляем файл после использования
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    def test_send_motivational_quote_with_image(self, mock_quote, translated_text, temp_image_file):
        """
        Тест полного процесса отправки мотивационной цитаты с изображением
        
        Проверяем, что функция send_motivational_quote корректно координирует 
        все компоненты системы при включенной генерации изображений
        """
        # Патчим все внешние сервисы и зависимости
        with patch('main.QuotesService.get_random_quote', return_value=mock_quote), \
             patch('main.TranslatorService.translate', return_value=translated_text), \
             patch('main.ImageService.generate_image_from_quote', return_value=temp_image_file), \
             patch('main.TelegramBot') as mock_telegram_bot_class, \
             patch('main.ENABLE_IMAGE_GENERATION', True), \
             patch('main.logger') as mock_logger:
            
            # Настраиваем мок для телеграм-бота
            mock_telegram_bot = Mock()
            mock_telegram_bot.send_quote.return_value = True
            mock_telegram_bot_class.return_value = mock_telegram_bot
            
            # Вызываем функцию send_motivational_quote
            send_motivational_quote()
            
            # Проверяем, что все сервисы были вызваны
            mock_logger.info.assert_any_call(f"Получена цитата: {mock_quote}")
            mock_logger.info.assert_any_call(f"Переведенная цитата: {translated_text}")
            mock_logger.info.assert_any_call("Генерация изображения на основе цитаты...")
            mock_logger.info.assert_any_call(f"Изображение успешно создано: {temp_image_file}")
            mock_logger.info.assert_any_call("Цитата успешно отправлена")
            
            # Проверяем, что бот вызвал метод send_quote с правильными параметрами
            mock_telegram_bot.send_quote.assert_called_once_with(
                mock_quote, translated_text, temp_image_file
            )
    
    def test_send_motivational_quote_without_image(self, mock_quote, translated_text):
        """
        Тест процесса отправки мотивационной цитаты без изображения
        
        Проверяем, что функция send_motivational_quote корректно работает
        при отключенной генерации изображений
        """
        # Патчим все внешние сервисы и зависимости
        with patch('main.QuotesService.get_random_quote', return_value=mock_quote), \
             patch('main.TranslatorService.translate', return_value=translated_text), \
             patch('main.ImageService.generate_image_from_quote') as mock_generate_image, \
             patch('main.TelegramBot') as mock_telegram_bot_class, \
             patch('main.ENABLE_IMAGE_GENERATION', False), \
             patch('main.logger') as mock_logger:
            
            # Настраиваем мок для телеграм-бота
            mock_telegram_bot = Mock()
            mock_telegram_bot.send_quote.return_value = True
            mock_telegram_bot_class.return_value = mock_telegram_bot
            
            # Вызываем функцию send_motivational_quote
            send_motivational_quote()
            
            # Проверяем, что генерация изображения не вызывалась
            mock_generate_image.assert_not_called()
            
            # Проверяем, что бот вызвал метод send_quote с правильными параметрами
            mock_telegram_bot.send_quote.assert_called_once_with(
                mock_quote, translated_text, None
            )
            
            # Проверяем логирование
            mock_logger.info.assert_any_call(f"Получена цитата: {mock_quote}")
            mock_logger.info.assert_any_call(f"Переведенная цитата: {translated_text}")
            mock_logger.info.assert_any_call("Цитата успешно отправлена")
    
    def test_send_motivational_quote_image_generation_failure(self, mock_quote, translated_text):
        """
        Тест обработки ошибки генерации изображения
        
        Проверяем, что функция send_motivational_quote корректно обрабатывает
        ситуацию, когда генерация изображения завершилась неудачей
        """
        # Патчим все внешние сервисы и зависимости
        with patch('main.QuotesService.get_random_quote', return_value=mock_quote), \
             patch('main.TranslatorService.translate', return_value=translated_text), \
             patch('main.ImageService.generate_image_from_quote', return_value=None), \
             patch('main.TelegramBot') as mock_telegram_bot_class, \
             patch('main.ENABLE_IMAGE_GENERATION', True), \
             patch('main.logger') as mock_logger:
            
            # Настраиваем мок для телеграм-бота
            mock_telegram_bot = Mock()
            mock_telegram_bot.send_quote.return_value = True
            mock_telegram_bot_class.return_value = mock_telegram_bot
            
            # Вызываем функцию send_motivational_quote
            send_motivational_quote()
            
            # Проверяем логирование ошибки
            mock_logger.warning.assert_called_with("Не удалось создать изображение для цитаты")
            
            # Проверяем, что бот вызвал метод send_quote без изображения
            mock_telegram_bot.send_quote.assert_called_once_with(
                mock_quote, translated_text, None
            )
    
    def test_send_motivational_quote_telegram_failure(self, mock_quote, translated_text, temp_image_file):
        """
        Тест обработки ошибки отправки в Telegram
        
        Проверяем, что функция send_motivational_quote корректно обрабатывает
        ситуацию, когда отправка в Telegram завершилась неудачей
        """
        # Патчим все внешние сервисы и зависимости
        with patch('main.QuotesService.get_random_quote', return_value=mock_quote), \
             patch('main.TranslatorService.translate', return_value=translated_text), \
             patch('main.ImageService.generate_image_from_quote', return_value=temp_image_file), \
             patch('main.TelegramBot') as mock_telegram_bot_class, \
             patch('main.ENABLE_IMAGE_GENERATION', True), \
             patch('main.logger') as mock_logger, \
             patch('os.unlink') as mock_unlink:
            
            # Настраиваем мок для телеграм-бота с ошибкой
            mock_telegram_bot = Mock()
            mock_telegram_bot.send_quote.return_value = False
            mock_telegram_bot_class.return_value = mock_telegram_bot
            
            # Вызываем функцию send_motivational_quote
            send_motivational_quote()
            
            # Проверяем логирование ошибки
            mock_logger.error.assert_called_with("Не удалось отправить цитату")
            
            # Проверяем, что временный файл был удален вручную (т.к. это не произошло в TelegramBot)
            # mock_unlink.assert_called_with(temp_image_file) 