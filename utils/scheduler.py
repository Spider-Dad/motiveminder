import time
import logging
import schedule
import pytz
from datetime import datetime, timedelta
from config.config import SCHEDULE, TIMEZONE

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, job_function):
        """
        Инициализирует планировщик с расписанием по дням недели и времени
        
        :param job_function: Функция, которая будет выполняться по расписанию
        """
        self.job_function = job_function
        self.timezone = pytz.timezone(TIMEZONE)
        self.schedule = SCHEDULE
        self.days_of_week = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }
        self._setup_schedule()
        
    def _convert_to_utc(self, time_str):
        """
        Конвертирует локальное время в UTC для правильного планирования
        
        :param time_str: Время в формате "HH:MM"
        :return: Время в UTC в формате "HH:MM"
        """
        # Создаем сегодняшнюю дату с указанным временем в локальной временной зоне
        local_dt = self.timezone.localize(
            datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time_str}", "%Y-%m-%d %H:%M")
        )
        # Конвертируем в UTC
        utc_dt = local_dt.astimezone(pytz.UTC)
        return utc_dt.strftime("%H:%M")
        
    def _setup_schedule(self):
        """
        Настраивает расписание выполнения задачи по дням недели и времени
        """
        # Очищаем текущее расписание
        schedule.clear()
        
        # Настраиваем расписание по дням недели
        for day, times in self.schedule.items():
            if day.lower() not in self.days_of_week:
                logger.warning(f"Неизвестный день недели: {day}. Пропускаем.")
                continue
                
            for time_str in times:
                try:
                    # Сначала конвертируем время из настройки в UTC
                    utc_time = self._convert_to_utc(time_str)
                    
                    # Теперь получаем локальное системное время, соответствующее этому UTC времени
                    # Это нужно, потому что schedule воспринимает время как локальное системное
                    utc_dt = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {utc_time}", "%Y-%m-%d %H:%M")
                    utc_dt = pytz.UTC.localize(utc_dt)
                    
                    # Конвертируем UTC время в локальное системное
                    system_local_dt = utc_dt.astimezone(datetime.now().astimezone().tzinfo)
                    system_time = system_local_dt.strftime("%H:%M")
                    
                    # Для каждого времени добавляем задачу в расписание,
                    # используя время, соответствующее локальному системному времени
                    if day.lower() == 'monday':
                        schedule.every().monday.at(system_time).do(self.job_function)
                    elif day.lower() == 'tuesday':
                        schedule.every().tuesday.at(system_time).do(self.job_function)
                    elif day.lower() == 'wednesday':
                        schedule.every().wednesday.at(system_time).do(self.job_function)
                    elif day.lower() == 'thursday':
                        schedule.every().thursday.at(system_time).do(self.job_function)
                    elif day.lower() == 'friday':
                        schedule.every().friday.at(system_time).do(self.job_function)
                    elif day.lower() == 'saturday':
                        schedule.every().saturday.at(system_time).do(self.job_function)
                    elif day.lower() == 'sunday':
                        schedule.every().sunday.at(system_time).do(self.job_function)
                        
                    logger.info(f"Запланирована отправка цитаты в {day} в {time_str} (UTC: {utc_time}, Системное: {system_time})")
                except Exception as e:
                    logger.error(f"Ошибка при настройке расписания для {day} в {time_str}: {e}")
    
    def _get_next_run_time(self):
        """
        Получает следующее время запуска задачи в локальной временной зоне
        """
        next_run = schedule.next_run()
        if next_run:
            # next_run возвращается как naive datetime в системном часовом поясе
            # Нам нужно преобразовать его в aware datetime в целевом часовом поясе
            
            # 1. Преобразуем в aware datetime в системном часовом поясе
            # Получаем текущее время как aware datetime, чтобы определить системный часовой пояс
            now = datetime.now().astimezone()
            system_tz = now.tzinfo
            
            # Создаем aware datetime с системным часовым поясом
            next_run_system = datetime(
                next_run.year, next_run.month, next_run.day,
                next_run.hour, next_run.minute, next_run.second,
                tzinfo=system_tz
            )
            
            # 2. Преобразуем в целевой часовой пояс (TIMEZONE)
            local_next_run = next_run_system.astimezone(self.timezone)
            
            return local_next_run.strftime("%Y-%m-%d %H:%M:%S %Z")
        return "не запланировано"
                
    def start(self):
        """
        Запускает планировщик
        """
        logger.info(f"Планировщик запущен с часовым поясом {TIMEZONE}")
        logger.info(f"Следующее выполнение: {self._get_next_run_time()}")
        
        # Запускаем бесконечный цикл для выполнения задач
        last_log_time = datetime.now()
        while True:
            schedule.run_pending()
            
            # Логируем активность каждые 5 минут
            now = datetime.now()
            if (now - last_log_time).total_seconds() > 300:  # 5 минут = 300 секунд
                logger.info(f"Планировщик активен. Следующее выполнение: {self._get_next_run_time()}")
                last_log_time = now
                
            time.sleep(1) 