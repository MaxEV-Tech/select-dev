import logging

logging.basicConfig(level=logging.DEBUG,  # Устанавливаем уровень логирования
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат вывода сообщений
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger("updater")
