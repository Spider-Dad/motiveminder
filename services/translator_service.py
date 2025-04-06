import requests
import logging
from cachetools import TTLCache
from config.config import MYMEMORY_API_URL, MYMEMORY_EMAIL

logger = logging.getLogger(__name__)

class TranslatorService:
    # Кэш для хранения переводов (TTL - 24 часа)
    _cache = TTLCache(maxsize=100, ttl=86400)
    
    @classmethod
    def translate(cls, text, source_lang='en', target_lang='ru'):
        """
        Переводит текст с использованием MyMemory API
        """
        cache_key = f"{source_lang}:{target_lang}:{text}"
        
        # Проверяем кэш
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        # Если перевода нет в кэше, запрашиваем API
        try:
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}'
            }
            
            # Добавляем email, если он указан (для увеличения лимита запросов)
            if MYMEMORY_EMAIL:
                params['de'] = MYMEMORY_EMAIL
                
            response = requests.get(MYMEMORY_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and 'responseData' in data and 'translatedText' in data['responseData']:
                translated_text = data['responseData']['translatedText']
                # Сохраняем в кэш
                cls._cache[cache_key] = translated_text
                return translated_text
            else:
                logger.error(f"Unexpected response format from MyMemory API: {data}")
                return text
                
        except requests.RequestException as e:
            logger.error(f"Error translating text using MyMemory API: {e}")
            return text 