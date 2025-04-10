"""
Tests for Scheduler
"""
import pytest
from unittest.mock import Mock, patch, call, MagicMock
import pytz
import time
import schedule
from datetime import datetime, timedelta
from utils.scheduler import Scheduler


class TestScheduler:
    """Тесты для класса Scheduler"""
    
    @pytest.fixture
    def mock_job(self):
        """Фикстура - мок для функции задания"""
        return Mock()
    
    @pytest.fixture
    def mock_schedule(self):
        """Фикстура - расписание для тестов"""
        return {
            'monday': ['09:00', '12:00'],
            'tuesday': ['09:00'],
            'unknown_day': ['10:00']  # Для тестирования обработки неизвестного дня
        }
    
    @pytest.fixture
    def test_timezone(self):
        """Фикстура - тестовый часовой пояс"""
        return 'Europe/Moscow'
    
    def test_init(self, mock_job, mock_schedule, test_timezone):
        """Тест инициализации планировщика"""
        with patch('utils.scheduler.SCHEDULE', mock_schedule), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch.object(Scheduler, '_setup_schedule') as mock_setup:
            scheduler = Scheduler(mock_job)
            
            # Проверяем, что параметры установлены правильно
            assert scheduler.job_function == mock_job
            assert scheduler.timezone == pytz.timezone(test_timezone)
            assert scheduler.schedule == mock_schedule
            assert 'monday' in scheduler.days_of_week
            assert scheduler.days_of_week['monday'] == 0
            assert scheduler.days_of_week['sunday'] == 6
            # Проверяем, что метод _setup_schedule вызван
            mock_setup.assert_called_once()
    
    def test_convert_to_utc(self, mock_job, test_timezone):
        """Тест преобразования времени в UTC"""
        with patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch('utils.scheduler.SCHEDULE', {}), \
             patch.object(Scheduler, '_setup_schedule'):
            
            scheduler = Scheduler(mock_job)
            
            # Для тестирования конвертации фиксируем текущую дату
            mock_now = datetime(2023, 1, 1, 0, 0)  # 1 января 2023 00:00
            
            with patch('utils.scheduler.datetime') as mock_datetime:
                mock_datetime.now.return_value = mock_now
                mock_datetime.strptime.side_effect = datetime.strptime
                
                # Тестируем конвертацию при разнице с UTC +3 (Москва)
                local_time = "12:00"
                utc_time = scheduler._convert_to_utc(local_time)
                # Для Москвы (UTC+3) 12:00 -> 09:00 UTC
                assert utc_time == "09:00"
    
    def test_setup_schedule(self, mock_job, mock_schedule, test_timezone):
        """Тест настройки расписания"""
        with patch('utils.scheduler.SCHEDULE', mock_schedule), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch('utils.scheduler.schedule') as mock_schedule_lib, \
             patch.object(Scheduler, '_convert_to_utc', return_value="09:00"):
            
            # Моки для дней недели и метода do
            mock_monday = Mock()
            mock_tuesday = Mock()
            mock_do = Mock()
            
            # Настраиваем цепочку mock -> every -> day -> at -> do
            mock_monday.at.return_value.do = mock_do
            mock_tuesday.at.return_value.do = mock_do
            
            # Устанавливаем моки для дней недели
            mock_schedule_lib.every.return_value.monday = mock_monday
            mock_schedule_lib.every.return_value.tuesday = mock_tuesday
            
            # Инициализируем планировщик (это вызовет _setup_schedule)
            scheduler = Scheduler(mock_job)
            
            # Проверяем, что schedule.clear был вызван
            mock_schedule_lib.clear.assert_called_once()
            
            # Проверяем общее количество вызовов at и do
            # В тестовом расписании 2 времени для понедельника и 1 для вторника
            assert mock_monday.at.call_count == 2, "at() должен быть вызван 2 раза для понедельника"
            assert mock_tuesday.at.call_count == 1, "at() должен быть вызван 1 раз для вторника"
            assert mock_do.call_count == 3, "do() должен быть вызван для каждого времени (всего 3 раза)"
            
            # Проверяем вызовы do с нашей job-функцией
            for call_args in mock_do.call_args_list:
                assert call_args[0][0] == mock_job, "do() должен быть вызван с функцией-заданием"
    
    def test_setup_schedule_unknown_day(self, mock_job, test_timezone):
        """Тест обработки неизвестного дня недели в расписании"""
        test_schedule = {'unknown_day': ['10:00']}
        
        with patch('utils.scheduler.SCHEDULE', test_schedule), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch('utils.scheduler.schedule'), \
             patch('utils.scheduler.logger') as mock_logger:
            
            scheduler = Scheduler(mock_job)
            
            # Должно быть предупреждение о неизвестном дне
            mock_logger.warning.assert_called_once_with("Неизвестный день недели: unknown_day. Пропускаем.")
    
    def test_setup_schedule_exception(self, mock_job, test_timezone):
        """Тест обработки исключения при настройке расписания"""
        test_schedule = {'monday': ['invalid_time']}
        
        with patch('utils.scheduler.SCHEDULE', test_schedule), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch('utils.scheduler.schedule'), \
             patch.object(Scheduler, '_convert_to_utc', side_effect=Exception("Invalid time format")), \
             patch('utils.scheduler.logger') as mock_logger:
            
            scheduler = Scheduler(mock_job)
            
            # Должно быть сообщение об ошибке при настройке расписания
            mock_logger.error.assert_called_once_with(
                "Ошибка при настройке расписания для monday в invalid_time: Invalid time format"
            )
    
    def test_get_next_run_time_with_scheduled_task(self, mock_job, test_timezone):
        """Тест получения времени следующего запуска с запланированной задачей"""
        with patch('utils.scheduler.SCHEDULE', {}), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch.object(Scheduler, '_setup_schedule'), \
             patch('utils.scheduler.schedule') as mock_schedule_lib:
            
            # Создаем фиксированную дату для следующего запуска
            # Например, 1 января 2023 года, 12:00 UTC
            next_run_utc = datetime(2023, 1, 1, 12, 0)
            
            # Mock для schedule.next_run()
            mock_schedule_lib.next_run.return_value = next_run_utc
            
            scheduler = Scheduler(mock_job)
            
            # Получаем следующее время запуска
            next_run_str = scheduler._get_next_run_time()
            
            # Проверяем, что schedule.next_run() был вызван
            mock_schedule_lib.next_run.assert_called_once()
            
            # В результате должна быть строка с датой и временем в локальном часовом поясе
            # Для Москвы (UTC+3) 12:00 UTC -> 15:00 MSK
            # Точный формат зависит от локали, но должна быть дата, время и часовой пояс
            assert "2023-01-01" in next_run_str
            assert "15:00:00" in next_run_str
            assert "MSK" in next_run_str or "+0300" in next_run_str
    
    def test_get_next_run_time_without_scheduled_task(self, mock_job, test_timezone):
        """Тест получения времени следующего запуска без запланированных задач"""
        with patch('utils.scheduler.SCHEDULE', {}), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch.object(Scheduler, '_setup_schedule'), \
             patch('utils.scheduler.schedule') as mock_schedule_lib:
            
            # Mock для schedule.next_run() - возвращаем None (нет запланированных задач)
            mock_schedule_lib.next_run.return_value = None
            
            scheduler = Scheduler(mock_job)
            
            # Получаем следующее время запуска
            next_run_str = scheduler._get_next_run_time()
            
            # Проверяем, что schedule.next_run() был вызван
            mock_schedule_lib.next_run.assert_called_once()
            
            # Результат должен быть "не запланировано"
            assert next_run_str == "не запланировано"
    
    def test_start(self, mock_job, test_timezone):
        """Тест запуска планировщика"""
        with patch('utils.scheduler.SCHEDULE', {}), \
             patch('utils.scheduler.TIMEZONE', test_timezone), \
             patch.object(Scheduler, '_setup_schedule'), \
             patch.object(Scheduler, '_get_next_run_time', return_value="2023-01-01 12:00:00 MSK"), \
             patch('utils.scheduler.logger') as mock_logger, \
             patch('utils.scheduler.schedule') as mock_schedule_lib, \
             patch('utils.scheduler.time') as mock_time:
            
            # Создаем счетчик для time.sleep, чтобы выйти из бесконечного цикла после 3 итераций
            sleep_count = 0
            
            def mock_sleep(seconds):
                nonlocal sleep_count
                sleep_count += 1
                if sleep_count >= 3:
                    raise KeyboardInterrupt("Тест завершен")
            
            # Устанавливаем мок для time.sleep
            mock_time.sleep.side_effect = mock_sleep
            
            # Устанавливаем мок для datetime.now() для проверки логирования
            with patch('utils.scheduler.datetime') as mock_datetime:
                # Первый вызов datetime.now() вернет начальную дату
                # Последующие вызовы вернут даты, разнесенные на 6 минут
                mock_datetime.now.side_effect = [
                    datetime(2023, 1, 1, 12, 0),  # Начальная дата
                    datetime(2023, 1, 1, 12, 0),  # Первая итерация
                    datetime(2023, 1, 1, 12, 6),  # Вторая итерация (через 6 минут)
                    datetime(2023, 1, 1, 12, 12)  # Третья итерация (через 12 минут)
                ]
                
                scheduler = Scheduler(mock_job)
                
                # Запускаем планировщик (он выйдет из цикла после 3 итераций благодаря нашему моку)
                try:
                    scheduler.start()
                except KeyboardInterrupt:
                    pass
                
                # Проверяем, что логи были записаны правильно
                mock_logger.info.assert_has_calls([
                    call(f"Планировщик запущен с часовым поясом {test_timezone}"),
                    call("Следующее выполнение: 2023-01-01 12:00:00 MSK"),
                    call("Планировщик активен. Следующее выполнение: 2023-01-01 12:00:00 MSK")
                ])
                
                # Проверяем, что schedule.run_pending() был вызван для каждой итерации
                assert mock_schedule_lib.run_pending.call_count == 3
                
                # Проверяем, что time.sleep был вызван для каждой итерации с аргументом 1
                assert mock_time.sleep.call_count == 3
                assert all(call.args == (1,) for call in mock_time.sleep.call_args_list) 