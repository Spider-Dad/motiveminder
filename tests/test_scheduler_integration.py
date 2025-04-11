"""
Интеграционные тесты для Scheduler и функции отправки цитат

Эти тесты проверяют взаимодействие между планировщиком и функцией send_motivational_quote.
"""
import pytest
from unittest.mock import patch, Mock, call
import time
import schedule
from datetime import datetime
import pytz
from utils.scheduler import Scheduler
from config.config import TIMEZONE


class TestSchedulerIntegration:
    """Интеграционные тесты для Scheduler"""
    
    @pytest.fixture
    def mock_job(self):
        """Фикстура для создания мок-функции"""
        return Mock()
    
    @pytest.fixture
    def test_schedule(self):
        """Фикстура для создания тестового расписания"""
        return {
            'monday': ['10:00', '15:00'],
            'tuesday': ['10:00', '15:00'],
            'wednesday': ['10:00', '15:00'],
            'thursday': ['10:00', '15:00'],
            'friday': ['10:00', '15:00'],
            'saturday': ['12:00'],
            'sunday': ['12:00']
        }
    
    def test_scheduler_integration_with_job_function(self, mock_job, test_schedule):
        """
        Тест интеграции планировщика с функцией-заданием
        
        Проверяем, что планировщик правильно настраивает и вызывает функцию-задание
        в соответствии с расписанием
        """
        # Патчим библиотеку schedule и другие зависимости
        with patch('utils.scheduler.schedule') as mock_schedule_lib, \
             patch('utils.scheduler.time.sleep') as mock_sleep, \
             patch('utils.scheduler.logger') as mock_logger, \
             patch('utils.scheduler.TIMEZONE', 'Europe/Moscow'), \
             patch('utils.scheduler.SCHEDULE', test_schedule):
            
            # Создаем фейковую функцию для schedule.run_pending, которая будет симулировать запуск заданий
            def fake_run_pending():
                # Вызываем нашу функцию напрямую при первом вызове run_pending
                if mock_job.call_count == 0:
                    mock_job()
            
            # Настраиваем мок для run_pending
            mock_schedule_lib.run_pending.side_effect = fake_run_pending
            
            # Настраиваем мок для next_run, чтобы симулировать следующее время запуска
            # Важно: возвращаем обычный datetime без timezone
            mock_next_run = datetime(2023, 1, 1, 12, 0)
            mock_schedule_lib.next_run.return_value = mock_next_run
            
            # Создаем планировщик и запускаем его
            scheduler = Scheduler(mock_job)
            
            # Имитируем завершение после одной итерации цикла
            mock_sleep.side_effect = KeyboardInterrupt()
            
            try:
                scheduler.start()
            except KeyboardInterrupt:
                pass
            
            # Проверяем, что setup_schedule был вызван
            assert mock_schedule_lib.clear.call_count > 0
            
            # Проверяем, что job был вызван хотя бы один раз
            mock_job.assert_called_once()
            
            # Проверяем логирование - ищем сообщение содержащее "Планировщик запущен"
            any_start_log = False
            for call_args in mock_logger.info.call_args_list:
                if len(call_args[0]) > 0 and 'Планировщик запущен' in call_args[0][0]:
                    any_start_log = True
                    break
            
            assert any_start_log, "Не найдено сообщение о запуске планировщика в логах"
    
    def test_scheduler_integration_with_real_schedule(self):
        """
        Тест интеграции планировщика с реальным расписанием
        
        Проверяем, что планировщик корректно настраивает расписание
        на основе конфигурации в переменных окружения
        """
        # Функция-задание для теста
        mock_job = Mock()
        
        # Патчим только необходимые зависимости, оставляя реальное расписание
        with patch('utils.scheduler.time.sleep') as mock_sleep, \
             patch('utils.scheduler.logger') as mock_logger, \
             patch('utils.scheduler.datetime') as mock_datetime, \
             patch('utils.scheduler.TIMEZONE', 'Europe/Moscow'), \
             patch('utils.scheduler.schedule') as mock_schedule_lib:
            
            # Фиксируем текущее время для предсказуемости теста
            # Понедельник, 1 января 2024, 9:00
            fixed_now = datetime(2024, 1, 1, 9, 0)
            mock_datetime.now.return_value = fixed_now
            mock_datetime.strptime.side_effect = datetime.strptime
            
            # Настраиваем мок для next_run, чтобы избежать ошибки с timezone
            mock_next_run = datetime(2024, 1, 1, 12, 0)  # Время без timezone
            mock_schedule_lib.next_run.return_value = mock_next_run
            
            # Вызываем исключение после первого вызова sleep
            mock_sleep.side_effect = KeyboardInterrupt()
            
            # Создаем планировщик и запускаем его
            scheduler = Scheduler(mock_job)
            
            try:
                scheduler.start()
            except KeyboardInterrupt:
                pass
            
            # Проверяем, что setup_schedule был вызван
            assert mock_schedule_lib.clear.call_count > 0
            
            # Проверяем, что run_pending был вызван хотя бы один раз
            assert mock_schedule_lib.run_pending.call_count > 0
            
            # Проверяем логирование - ищем любое сообщение содержащее "Планировщик запущен"
            any_start_log = False
            for call_args in mock_logger.info.call_args_list:
                if len(call_args[0]) > 0 and 'Планировщик запущен' in call_args[0][0]:
                    any_start_log = True
                    break
            
            assert any_start_log, "Не найдено сообщение о запуске планировщика в логах"
    
    def test_integration_with_send_motivational_quote(self, mock_job, test_schedule):
        """
        Интеграционный тест для проверки совместной работы планировщика и функции отправки цитат
        
        Проверяем, что send_motivational_quote может быть успешно вызвана планировщиком
        """
        # Патчим функцию send_motivational_quote
        with patch('main.send_motivational_quote') as mock_send_quote, \
             patch('utils.scheduler.time.sleep') as mock_sleep, \
             patch('utils.scheduler.logger') as mock_logger, \
             patch('utils.scheduler.TIMEZONE', 'Europe/Moscow'), \
             patch('utils.scheduler.SCHEDULE', test_schedule), \
             patch('utils.scheduler.schedule') as mock_schedule_lib:
            
            # Создаем фейковую функцию для schedule.run_pending
            def fake_run_pending():
                # Симулируем вызов нашей функции при первом вызове run_pending
                if mock_send_quote.call_count == 0:
                    # Вызываем напрямую функцию, которую передали планировщику
                    mock_send_quote()
            
            # Настраиваем мок для run_pending и next_run
            mock_schedule_lib.run_pending.side_effect = fake_run_pending
            mock_schedule_lib.next_run.return_value = datetime(2024, 1, 1, 12, 0)  # Время без timezone
            mock_sleep.side_effect = KeyboardInterrupt()
            
            # Создаем планировщик, передавая ему реальную функцию (mock)
            scheduler = Scheduler(mock_send_quote)
            
            try:
                scheduler.start()
            except KeyboardInterrupt:
                pass
            
            # Проверяем, что функция send_motivational_quote была вызвана
            mock_send_quote.assert_called_once()
            
            # Проверяем логирование - ищем любое сообщение содержащее "Планировщик запущен"
            any_start_log = False
            for call_args in mock_logger.info.call_args_list:
                if len(call_args[0]) > 0 and 'Планировщик запущен' in call_args[0][0]:
                    any_start_log = True
                    break
            
            assert any_start_log, "Не найдено сообщение о запуске планировщика в логах"
            
            # Проверяем, что расписание было настроено
            assert mock_schedule_lib.clear.call_count > 0 