import os
import base64
import json
import logging
import requests
import tempfile
import urllib3
import uuid
from datetime import datetime, timedelta
from config.config import GIGACHAT_API_KEY, VERIFY_SSL

# Отключаем предупреждения о небезопасных запросах, если проверка SSL отключена
if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Глобальные переменные для хранения токена
access_token = None
token_expiry = None

class ImageService:
    @staticmethod
    def get_access_token():
        """
        Получает токен доступа к GigaChat API
        
        :return: Токен доступа или None в случае ошибки
        """
        global access_token, token_expiry
        
        # Проверяем, есть ли действующий токен
        if access_token and token_expiry and datetime.now() < token_expiry:
            logger.info("Используем существующий токен доступа")
            return access_token
            
        try:
            rq_uid = str(uuid.uuid4())
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": rq_uid,
                "Authorization": f"Basic {GIGACHAT_API_KEY}"
            }
            
            payload = {
                "scope": "GIGACHAT_API_PERS"
            }
            
            logger.info("Получение токена доступа к GigaChat API")
            response = requests.post(url, headers=headers, data=payload, verify=VERIFY_SSL)
            response.raise_for_status()
            
            data = response.json()
            if 'access_token' in data:
                access_token = data['access_token']
                # Устанавливаем срок действия токена на 30 минут
                token_expiry = datetime.now() + timedelta(minutes=30)
                logger.info("Токен доступа получен успешно")
                return access_token
            else:
                logger.error("Токен доступа не найден в ответе от GigaChat API")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении токена доступа: {e}")
            return None
            
    @staticmethod
    def generate_image_from_quote(quote_text):
        """
        Генерирует изображение на основе цитаты с помощью GigaChat API
        
        :param quote_text: Текст переведенной цитаты
        :return: Путь к временному файлу с изображением или None в случае ошибки
        """
        try:
            # Получаем токен доступа
            access_token = ImageService.get_access_token()
            if not access_token:
                logger.error("Не удалось получить токен доступа к GigaChat API")
                return None
            
            prompt = f"""Создай кинематографичное изображение, которое передает философскую цитату от известных людей, 
            которые знали, как менять реальность: {quote_text}. Визуализация должна быть в мотивирующем биографическом стиле, 
            с фокусом на современный мир. Используй высоко абстрактные формы, такие как свет, тени и цвета для передачи глубокого смысла. 
            Атмосфера должна быть спокойной, медитативной, умиротворяющей, с персонажами в раздумьях или медитации. 
            Добавь лёгкое движение (например, развевающиеся волосы, туман, мягкие световые переходы), чтобы создать кинематографичный эффект. 
            Включи символику (светящийся объект, рука, книга) для усиления смысловой нагрузки, 
            но избегай буквального изображения цитаты или авторов. 
            Используй кинематографичный градиент для цветовой палитры, чтобы передать атмосферу глубины и мотивации."""
            
            # Запрос к GigaChat API для генерации изображения
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            payload = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "top_p": 0.1,
                "n": 1,
                "stream": False,
                "max_tokens": 1500,
                "function_call": "auto"
            }
            
            # Отправляем запрос на генерацию
            logger.info("Отправка запроса на генерацию изображения в GigaChat")
            response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Проверяем, вызвал ли GigaChat функцию text2image
            if (
                'choices' in response_data and 
                len(response_data['choices']) > 0 and 
                'function_call' in response_data['choices'][0]['message'] and
                response_data['choices'][0]['message']['function_call']['name'] == 'text2image'
            ):
                # Получаем аргументы функции text2image
                function_args = json.loads(response_data['choices'][0]['message']['function_call']['arguments'])
                image_uuid = function_args.get('uuid')
                
                if not image_uuid:
                    logger.error("UUID изображения не найден в ответе GigaChat")
                    return None
                
                # Запрашиваем содержимое изображения
                logger.info(f"Получение изображения с UUID: {image_uuid}")
                image_url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{image_uuid}/content"
                image_response = requests.post(
                    image_url,
                    headers=headers,
                    verify=VERIFY_SSL
                )
                image_response.raise_for_status()
                
                # Сохраняем изображение во временный файл
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(image_response.content)
                temp_file.close()
                
                logger.info(f"Изображение сохранено во временный файл: {temp_file.name}")
                return temp_file.name
            else:
                logger.error("GigaChat не вызвал функцию text2image или вернул неожиданный формат ответа")
                logger.debug(f"Ответ GigaChat: {response_data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к GigaChat API: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON ответа: {e}")
            return None
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при генерации изображения: {e}")
            return None 