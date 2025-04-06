import time
import logging
import schedule
from datetime import datetime
from config.config import SCHEDULE_MINUTES

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, job_function):
        """
        Инициализирует планировщик
        
        :param job_function: Функция, которая будет выполняться по расписанию
        """
        self.job_function = job_function
        self.schedule_minutes = SCHEDULE_MINUTES
        self._setup_schedule()
        
    def _setup_schedule(self):
        """
        Настраивает расписание выполнения задачи
        """
        # Выполняем задачу каждые X минут
        schedule.every(self.schedule_minutes).minutes.do(self.job_function)
        
        logger.info(f"Scheduled job to run every {self.schedule_minutes} minutes")
        
    def start(self):
        """
        Запускает планировщик
        """
        logger.info("Scheduler started")
        
        # Запускаем задачу один раз при старте
        self.job_function()
        
        # Запускаем бесконечный цикл для выполнения задач
        while True:
            schedule.run_pending()
            time.sleep(1) 