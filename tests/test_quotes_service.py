"""
Tests for QuotesService
"""
import pytest
from unittest.mock import Mock, patch
import requests
import json
from services.quotes_service import Quote, QuotesService

class TestQuote:
    """Тесты для класса Quote"""
    
    def test_init(self):
        """Тест инициализации объекта Quote"""
        quote = Quote("Test text", "Test author")
        assert quote.text == "Test text"
        assert quote.author == "Test author"
    
    def test_str(self):
        """Тест строкового представления Quote"""
        quote = Quote("Test text", "Test author")
        assert str(quote) == '"Test text" - Test author'

class TestQuotesService:
    """Тесты для QuotesService"""
    
    def test_get_random_quote_success(self):
        """Тест успешного получения случайной цитаты"""
        # Создаем мок объект для response
        mock_response = Mock()
        # Имитируем успешный ответ API
        mock_response.json.return_value = [
            {
                "q": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                "a": "Winston Churchill"
            }
        ]
        
        # Патчим метод requests.get, чтобы он возвращал наш мок
        with patch('services.quotes_service.requests.get', return_value=mock_response) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван с правильным URL
            mock_get.assert_called_once()
            
            # Проверяем, что объект Quote был создан с правильными данными
            assert quote.text == "Success is not final, failure is not fatal: it is the courage to continue that counts."
            assert quote.author == "Winston Churchill"
    
    def test_get_random_quote_empty_response(self):
        """Тест получения цитаты при пустом ответе API"""
        # Создаем мок объект для response
        mock_response = Mock()
        # Имитируем пустой ответ API
        mock_response.json.return_value = []
        
        # Патчим метод requests.get, чтобы он возвращал наш мок
        with patch('services.quotes_service.requests.get', return_value=mock_response) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван с правильным URL
            mock_get.assert_called_once()
            
            # Проверяем, что возвращена запасная цитата
            assert quote.text == "Life is what happens when you're busy making other plans."
            assert quote.author == "John Lennon"
    
    def test_get_random_quote_invalid_response(self):
        """Тест получения цитаты при некорректном ответе API"""
        # Создаем мок объект для response
        mock_response = Mock()
        # Имитируем некорректный ответ API
        mock_response.json.return_value = {"error": "Invalid response"}
        
        # Патчим метод requests.get, чтобы он возвращал наш мок
        with patch('services.quotes_service.requests.get', return_value=mock_response) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван
            mock_get.assert_called_once()
            
            # Проверяем, что возвращена запасная цитата
            assert quote.text == "Life is what happens when you're busy making other plans."
            assert quote.author == "John Lennon"
    
    def test_get_random_quote_missing_fields(self):
        """Тест получения цитаты при отсутствии полей в ответе API"""
        # Создаем мок объект для response
        mock_response = Mock()
        # Имитируем ответ API с отсутствующими полями
        mock_response.json.return_value = [
            {
                # Нет поля "q"
                "a": "Author without quote"
            }
        ]
        
        # Патчим метод requests.get, чтобы он возвращал наш мок
        with patch('services.quotes_service.requests.get', return_value=mock_response) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван
            mock_get.assert_called_once()
            
            # Проверяем, что возвращены значения по умолчанию для отсутствующих полей
            assert quote.text == "No quote available"
            assert quote.author == "Author without quote"
    
    def test_get_random_quote_http_error(self):
        """Тест получения цитаты при ошибке HTTP"""
        # Патчим метод requests.get, чтобы он вызывал исключение RequestException
        with patch('services.quotes_service.requests.get', side_effect=requests.RequestException("HTTP Error")) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван
            mock_get.assert_called_once()
            
            # Проверяем, что возвращена запасная цитата
            assert quote.text == "Life is what happens when you're busy making other plans."
            assert quote.author == "John Lennon"
    
    def test_get_random_quote_network_error(self):
        """Тест получения цитаты при сетевой ошибке (ConnectionError)"""
        # Патчим метод requests.get, чтобы он вызывал исключение ConnectionError
        with patch('services.quotes_service.requests.get', side_effect=requests.ConnectionError("Connection Error")) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван
            mock_get.assert_called_once()
            
            # Проверяем, что возвращена запасная цитата
            assert quote.text == "Life is what happens when you're busy making other plans."
            assert quote.author == "John Lennon"
    
    def test_get_random_quote_timeout_error(self):
        """Тест получения цитаты при таймауте запроса"""
        # Патчим метод requests.get, чтобы он вызывал исключение Timeout
        with patch('services.quotes_service.requests.get', side_effect=requests.Timeout("Request timed out")) as mock_get:
            quote = QuotesService.get_random_quote()
            
            # Проверяем, что requests.get был вызван
            mock_get.assert_called_once()
            
            # Проверяем, что возвращена запасная цитата
            assert quote.text == "Life is what happens when you're busy making other plans."
            assert quote.author == "John Lennon" 