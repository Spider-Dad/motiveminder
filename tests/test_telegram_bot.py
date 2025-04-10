"""
Tests for TelegramBot
"""
import pytest
import os
import telegram
from unittest.mock import Mock, patch, mock_open, call
from bot.telegram_bot import TelegramBot
from services.quotes_service import Quote


class TestTelegramBot:
    """Тесты для класса TelegramBot"""
    
    @pytest.fixture
    def mock_quote(self):
        """Фикстура для создания моковой цитаты"""
        return Quote(
            text="Life is what happens when you're busy making other plans.",
            author="John Lennon"
        )
    
    @pytest.fixture
    def translated_text(self):
        """Фикстура для переведенного текста"""
        return "Жизнь - это то, что происходит, когда вы заняты строительством других планов."
    
    @pytest.fixture
    def image_path(self):
        """Фикстура для пути к изображению"""
        return "temp/test_image.jpg"
    
    def test_init(self):
        """Тест инициализации бота"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', '@test_group'), \
             patch('bot.telegram_bot.logger') as mock_logger:
            
            # Инициализируем бота
            bot = TelegramBot()
            
            # Проверяем, что telegram.Bot был вызван с правильным токеном
            mock_bot.assert_called_once_with(token='test_token')
            
            # Проверяем, что атрибуты инициализированы правильно
            assert bot.channel_id == '@test_channel'
            assert bot.group_id == '@test_group'
            
            # Проверяем, что было записано сообщение в лог
            mock_logger.info.assert_called_once_with(
                "Telegram bot initialized for channel @test_channel and group @test_group"
            )
    
    def test_send_quote_no_translation_no_image(self, mock_quote):
        """Тест отправки цитаты без перевода и без изображения"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', None), \
             patch('bot.telegram_bot.logger') as mock_logger:
             
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату
            result = bot.send_quote(quote=mock_quote)
            
            # Проверяем, что сообщение было отформатировано правильно
            expected_message = f'🔥 *"Life is what happens when you\'re busy making other plans."*\n\n'
            expected_message += f'👤 _John Lennon_'
            
            # Проверяем, что вызов bot.send_message был выполнен с правильными параметрами
            mock_bot.send_message.assert_called_once_with(
                chat_id='@test_channel',
                text=expected_message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            
            # Проверяем, что send_photo не вызывался
            mock_bot.send_photo.assert_not_called()
            
            # Проверяем логирование
            mock_logger.info.assert_any_call("Цитата отправлена в @test_channel")
            
            # Функция должна вернуть True при успешной отправке
            assert result is True
    
    def test_send_quote_with_translation_no_image(self, mock_quote, translated_text):
        """Тест отправки цитаты с переводом, но без изображения"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', '@test_group'), \
             patch('bot.telegram_bot.logger') as mock_logger:
             
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату с переводом
            result = bot.send_quote(quote=mock_quote, translated_text=translated_text)
            
            # Проверяем, что сообщение было отформатировано правильно
            expected_message = f'🔥 *{translated_text}*\n\n'
            expected_message += f'🌐 "Life is what happens when you\'re busy making other plans."\n\n'
            expected_message += f'👤 _John Lennon_'
            
            # Проверяем, что вызов bot.send_message был выполнен дважды (для канала и группы)
            assert mock_bot.send_message.call_count == 2
            mock_bot.send_message.assert_has_calls([
                call(
                    chat_id='@test_channel',
                    text=expected_message,
                    parse_mode=telegram.ParseMode.MARKDOWN
                ),
                call(
                    chat_id='@test_group',
                    text=expected_message,
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
            ])
            
            # Проверяем, что send_photo не вызывался
            mock_bot.send_photo.assert_not_called()
            
            # Проверяем логирование
            mock_logger.info.assert_any_call("Цитата отправлена в @test_channel")
            mock_logger.info.assert_any_call("Цитата отправлена в @test_group")
            
            # Функция должна вернуть True при успешной отправке
            assert result is True
    
    def test_send_quote_with_image(self, mock_quote, image_path):
        """Тест отправки цитаты с изображением"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', None), \
             patch('bot.telegram_bot.os.path.exists', return_value=True), \
             patch('bot.telegram_bot.open', mock_open(), create=True) as mock_file, \
             patch('bot.telegram_bot.os.unlink') as mock_unlink, \
             patch('bot.telegram_bot.logger') as mock_logger:
             
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату с изображением
            result = bot.send_quote(quote=mock_quote, image_path=image_path)
            
            # Проверяем, что сообщение было отформатировано правильно
            expected_message = f'🔥 *"Life is what happens when you\'re busy making other plans."*\n\n'
            expected_message += f'👤 _John Lennon_'
            
            # Проверяем, что файл был открыт
            mock_file.assert_called_with(image_path, 'rb')
            
            # Проверяем, что вызов bot.send_photo был выполнен с правильными параметрами
            mock_bot.send_photo.assert_called_once()
            args, kwargs = mock_bot.send_photo.call_args
            assert kwargs['chat_id'] == '@test_channel'
            assert kwargs['caption'] == expected_message
            assert kwargs['parse_mode'] == telegram.ParseMode.MARKDOWN
            
            # Проверяем, что send_message не вызывался
            mock_bot.send_message.assert_not_called()
            
            # Проверяем, что файл был удален после отправки
            mock_unlink.assert_called_once_with(image_path)
            
            # Проверяем логирование
            mock_logger.info.assert_any_call("Цитата отправлена в @test_channel")
            mock_logger.info.assert_any_call(f"Временный файл {image_path} удален")
            
            # Функция должна вернуть True при успешной отправке
            assert result is True
    
    def test_send_quote_send_message_error(self, mock_quote):
        """Тест обработки ошибки при отправке сообщения"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', None), \
             patch('bot.telegram_bot.logger') as mock_logger:
             
            # Создаем мок для экземпляра бота с ошибкой при отправке
            mock_bot = Mock()
            mock_bot.send_message.side_effect = Exception("Error sending message")
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату 
            result = bot.send_quote(quote=mock_quote)
            
            # Проверяем логирование
            mock_logger.error.assert_any_call("Ошибка при отправке в @test_channel: Error sending message")
            
            # Проверяем, что функция вернула True (она перехватила исключение в цикле)
            assert result is True
    
    def test_send_quote_general_error(self):
        """Тест обработки общей ошибки при отправке цитаты"""
        # Простой тест: мы создаем объект, который вызовет ошибку при обращении к атрибутам
        broken_quote = "not a Quote object"
        
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', None), \
             patch('bot.telegram_bot.logger') as mock_logger:
              
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем "сломанную" цитату, которая вызовет ошибку атрибута
            result = bot.send_quote(quote=broken_quote)
            
            # Проверяем, что функция вернула False при общей ошибке
            assert result is False
            
            # Проверяем, что была записана ошибка в лог
            assert mock_logger.error.call_count > 0
            
            # Получаем последний вызов логгера и проверяем сообщение
            last_call = mock_logger.error.call_args_list[-1]
            error_message = last_call[0][0]
            assert "Ошибка при отправке цитаты в Telegram" in error_message
    
    def test_send_quote_image_unlink_error(self, mock_quote, image_path):
        """Тест обработки ошибки при удалении изображения"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', None), \
             patch('bot.telegram_bot.os.path.exists', return_value=True), \
             patch('bot.telegram_bot.open', mock_open(), create=True), \
             patch('bot.telegram_bot.os.unlink', side_effect=Exception("Error deleting file")), \
             patch('bot.telegram_bot.logger') as mock_logger:
             
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату с изображением
            result = bot.send_quote(quote=mock_quote, image_path=image_path)
            
            # Проверяем, что была записана ошибка при удалении файла
            mock_logger.warning.assert_called_once_with(
                f"Не удалось удалить временный файл {image_path}: Error deleting file"
            )
            
            # Функция должна вернуть True, так как основная задача (отправка) была выполнена
            assert result is True
    
    def test_send_quote_nonexistent_image(self, mock_quote, image_path):
        """Тест отправки цитаты с несуществующим изображением"""
        with patch('bot.telegram_bot.telegram.Bot') as mock_bot_class, \
             patch('bot.telegram_bot.TELEGRAM_BOT_TOKEN', 'test_token'), \
             patch('bot.telegram_bot.TELEGRAM_CHANNEL_ID', '@test_channel'), \
             patch('bot.telegram_bot.TELEGRAM_GROUP_ID', None), \
             patch('bot.telegram_bot.os.path.exists', return_value=False), \
             patch('bot.telegram_bot.logger') as mock_logger:
             
            # Создаем мок для экземпляра бота
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            # Инициализируем нашего телеграм-бота
            bot = TelegramBot()
            
            # Отправляем цитату с несуществующим изображением
            result = bot.send_quote(quote=mock_quote, image_path=image_path)
            
            # Проверяем, что была вызвана отправка сообщения (без изображения)
            mock_bot.send_message.assert_called_once()
            
            # Проверяем, что не было попытки отправить фото
            mock_bot.send_photo.assert_not_called()
            
            # Функция должна вернуть True
            assert result is True 