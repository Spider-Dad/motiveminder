import os
import base64
import json
import logging
import requests
import tempfile
import urllib3
import uuid
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config.config import GIGACHAT_API_KEY, VERIFY_SSL, GIGACHAT_MODEL

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
    def extract_image_uuid(content):
        """
        Извлекает UUID изображения из HTML-тега в ответе GigaChat
        
        :param content: Текст ответа от GigaChat
        :return: UUID изображения или None, если не найден
        """
        try:
            # Сначала пробуем использовать Beautiful Soup для парсинга HTML
            soup = BeautifulSoup(content, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.has_attr('src'):
                return img_tag['src']
                
            # Если не получилось, используем регулярное выражение как запасной вариант
            match = re.search(r'<img\s+src="([a-f0-9-]+)"\s+fuse="true"\s*/>', content)
            if match:
                return match.group(1)
                
            # Ищем UUID в тексте, даже без тега img (на случай нестандартного ответа)
            uuid_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', content)
            if uuid_match:
                return uuid_match.group(1)
                
            logger.warning(f"UUID изображения не найден в ответе: {content}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при извлечении UUID изображения: {e}")
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
            
            # Простое сообщение для генерации изображения
            simple_prompt = f"Нарисуй изображение, иллюстрирующее цитату: {quote_text}"
            
            # Добавляем системное сообщение для стилизации
            system_message = "Ты — опытный художник, специализирующийся на создании философских визуализаций. Основной объект — реалистичный персонаж, воплощающий дух мотивационной биографии, находящийся в естественной, вне времени обстановке. Изображение должно быть выполнено в киношном стиле с использованием кинематографичного градиента, легкого движения (развевающиеся волосы, туман, свет) и легких акцентов (птички, лунный свет, отражения), создающих вдохновляющую, светлую и оптимистичную атмосферу. В ключевых моментах избегай абстрактных элементов и буквального отображения текста."
            
            # Запрос к GigaChat API для генерации изображения
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            payload = {
                "model": GIGACHAT_MODEL,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": simple_prompt}
                ],
                "temperature": 1.0,
                "function_call": "auto"
            }
            
            # Отправляем запрос на генерацию
            logger.info(f"Отправка запроса на генерацию изображения в GigaChat (модель: {GIGACHAT_MODEL})")
            response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
            response.raise_for_status()
            
            response_data = response.json()
            logger.debug(f"Ответ GigaChat: {response_data}")
            
            # Проверяем наличие выбора и сообщения
            if (
                'choices' in response_data and 
                len(response_data['choices']) > 0 and 
                'message' in response_data['choices'][0] and
                'content' in response_data['choices'][0]['message']
            ):
                # Получаем содержимое ответа
                content = response_data['choices'][0]['message']['content']
                logger.info(f"Получен ответ от GigaChat: {content}")
                
                # Извлекаем UUID изображения из ответа
                image_uuid = ImageService.extract_image_uuid(content)
                
                if not image_uuid:
                    # Проверяем, есть ли функция text2image в ответе (как альтернативный вариант)
                    if 'function_call' in response_data['choices'][0]['message']:
                        function_call = response_data['choices'][0]['message']['function_call']
                        if function_call['name'] == 'text2image':
                            try:
                                function_args = json.loads(function_call['arguments'])
                                image_uuid = function_args.get('uuid')
                                logger.info(f"UUID изображения найден в function_call: {image_uuid}")
                            except Exception as e:
                                logger.error(f"Ошибка при разборе аргументов функции: {e}")
                                return None
                    else:
                        logger.error("UUID изображения не найден в ответе GigaChat")
                        return None
                
                # Запрашиваем содержимое изображения
                logger.info(f"Получение изображения с UUID: {image_uuid}")
                image_url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{image_uuid}/content"
                image_response = requests.get(
                    image_url,
                    headers=headers,
                    verify=VERIFY_SSL
                )
                
                # Проверка статуса ответа
                if image_response.status_code != 200:
                    logger.error(f"Ошибка при получении изображения: {image_response.status_code} {image_response.text}")
                    return None
                    
                # Проверка наличия содержимого
                if not image_response.content:
                    logger.error("Пустой ответ при получении изображения")
                    return None
                
                # Сохраняем изображение во временный файл
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(image_response.content)
                temp_file.close()
                
                logger.info(f"Изображение сохранено во временный файл: {temp_file.name}")
                return temp_file.name
            else:
                logger.error("Неожиданный формат ответа от GigaChat API")
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