import requests
import logging
from config.config import ZENQUOTES_API_URL

logger = logging.getLogger(__name__)

class Quote:
    def __init__(self, text, author):
        self.text = text
        self.author = author

    def __str__(self):
        return f'"{self.text}" - {self.author}'

class QuotesService:
    @staticmethod
    def get_random_quote() -> Quote:
        """
        Получает случайную цитату из API ZenQuotes
        """
        try:
            response = requests.get(ZENQUOTES_API_URL)
            response.raise_for_status()  # Проверка на ошибки HTTP
            
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                quote_data = data[0]
                return Quote(
                    text=quote_data.get('q', 'No quote available'),
                    author=quote_data.get('a', 'Unknown')
                )
            else:
                logger.error("Unexpected response format from ZenQuotes API")
                return Quote("Life is what happens when you're busy making other plans.", "John Lennon")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching quote from ZenQuotes API: {e}")
            # Возвращаем запасную цитату в случае ошибки
            return Quote("Life is what happens when you're busy making other plans.", "John Lennon") 