"""
Tests for ImageService
"""
import pytest
from unittest.mock import Mock, patch
import json
import requests
from services.image_service import ImageService, GIGACHAT_MODEL

@pytest.fixture(autouse=True)
def reset_globals():
    """Сбрасываем глобальные переменные перед каждым тестом"""
    import services.image_service as image_service
    image_service.access_token = None
    image_service.token_expiry = None

@pytest.fixture
def mock_response():
    """Фикстура для мокирования response"""
    response = Mock()
    response.raise_for_status = Mock()
    return response

class TestImageService:
    """Тесты для ImageService"""

    def test_extract_image_uuid_from_content(self):
        """Тест извлечения UUID из текстового контента"""
        # Тест с тегом img
        content = '<img src="12345-67890" fuse="true"/>'
        assert ImageService.extract_image_uuid(content) == "12345-67890"
        
        # Тест с UUID в формате v4
        content = "Изображение с UUID: 123e4567-e89b-12d3-a456-426614174000"
        assert ImageService.extract_image_uuid(content) == "123e4567-e89b-12d3-a456-426614174000"
        
        # Тест с некорректным контентом
        content = "Текст без UUID"
        assert ImageService.extract_image_uuid(content) is None

    def test_get_access_token_success(self, mock_response):
        """Тест успешного получения токена доступа"""
        with patch('services.image_service.requests.post') as mock_post:
            # Мокаем успешный ответ
            mock_response.json.return_value = {"access_token": "test-token"}
            mock_post.return_value = mock_response
            
            token = ImageService.get_access_token()
            assert token == "test-token"
            mock_post.assert_called_once()

    def test_get_access_token_failure(self, mock_response):
        """Тест неудачного получения токена доступа"""
        with patch('services.image_service.requests.post') as mock_post:
            # Мокаем ответ без токена
            mock_response.json.return_value = {"error": "unauthorized"}
            mock_post.return_value = mock_response
            
            token = ImageService.get_access_token()
            assert token is None
            mock_post.assert_called_once()

    @pytest.mark.parametrize("model,should_retry", [
        ("GigaChat-Pro", True),
        ("GigaChat", False),
    ])
    def test_generate_image_retry_logic(self, mock_response, model, should_retry):
        """Тест логики повторных попыток генерации изображения"""
        with patch('services.image_service.requests.post') as mock_post, \
             patch('services.image_service.requests.get') as mock_get, \
             patch('services.image_service.GIGACHAT_MODEL', model):
            
            # Мокаем ответ для получения токена
            token_response = Mock()
            token_response.json.return_value = {"access_token": "test-token"}
            
            # Первый ответ для генерации
            first_response = Mock()
            first_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '<img src="success-12345" fuse="true"/>'
                    }
                }]
            }
            
            # Настраиваем поведение mock_post
            mock_post.side_effect = [token_response, first_response]
            
            # Мокаем запрос изображения
            image_response = Mock()
            image_response.status_code = 200
            image_response.content = b"fake_image_data"
            mock_get.return_value = image_response
            
            result = ImageService.generate_image_from_quote("test quote")
            
            assert result is not None
            assert result.endswith('.jpg')
            mock_get.assert_called_once() # Убедимся, что изображение было запрошено

    def test_generate_image_function_call_response(self, mock_response):
        """Тест обработки ответа в формате function_call"""
        with patch('services.image_service.requests.post') as mock_post, \
             patch('services.image_service.requests.get') as mock_get:
            # Мокаем ответ для получения токена
            token_response = Mock()
            token_response.json.return_value = {"access_token": "test-token"}
            
            # Мокаем ответ с function_call
            function_response = Mock()
            function_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '<img src="func-call-uuid" fuse="true"/>',
                        "function_call": {
                            "name": "text2image",
                            "arguments": json.dumps({"uuid": "func-call-uuid"})
                        }
                    }
                }]
            }
            
            mock_post.side_effect = [token_response, function_response]
            
            # Мокаем запрос изображения
            image_response = Mock()
            image_response.status_code = 200
            image_response.content = b"fake_image_data"
            mock_get.return_value = image_response
            
            result = ImageService.generate_image_from_quote("test quote")
            assert result is not None
            assert result.endswith('.jpg')
            mock_get.assert_called_once()

    def test_generate_image_invalid_response(self, mock_response):
        """Тест обработки некорректного ответа API"""
        with patch('services.image_service.requests.post') as mock_post, \
             patch('services.image_service.requests.get') as mock_get:
            # Мокаем ответ для получения токена
            token_response = Mock()
            token_response.json.return_value = {"access_token": "test-token"}
            
            # Мокаем некорректный ответ
            invalid_response = Mock()
            invalid_response.json.return_value = {"invalid": "response"}
            
            mock_post.side_effect = [token_response, invalid_response]
            
            result = ImageService.generate_image_from_quote("test quote")
            assert result is None
            mock_get.assert_not_called() # Изображение не должно запрашиваться

    def test_generate_image_api_error(self):
        """Тест обработки ошибки API"""
        # Мокируем только нужные методы requests
        with patch('services.image_service.requests.post') as mock_post, \
             patch('services.image_service.requests.get') as mock_get:

            # Мокаем ответ для получения токена
            token_response = Mock()
            token_response.json.return_value = {"access_token": "test-token"}

            # Имитируем ошибку API при втором вызове post
            # Первый вызов (получение токена) вернет token_response
            # Второй вызов (генерация изображения) вызовет исключение
            mock_post.side_effect = [
                token_response,
                requests.exceptions.RequestException("API Error")
            ]

            # Вызываем метод, который должен вызвать ошибку
            result = ImageService.generate_image_from_quote("test quote")

            # Проверяем, что вернулся None из-за ошибки
            assert result is None
            # Проверяем, что mock_get не был вызван, так как ошибка произошла раньше
            mock_get.assert_not_called()
            # Проверяем, что mock_post был вызван дважды
            assert mock_post.call_count == 2 