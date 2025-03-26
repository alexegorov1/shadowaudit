import logging
import sys
from datetime import datetime

class LoggerFactory:
    def __init__(self, config):
        self._log_level = self._get_level(config.get("log_level", "INFO"))
        self._output_path = config.get("output_path", None)
        self._suppress_stdout = config.get("suppress_stdout", False)

    def create_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(self._log_level)
        logger.propagate = False

        if not logger.handlers:
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")

            if not self._suppress_stdout:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

            if self._output_path:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                file_name = f"{self._output_path}/shadowaudit_{timestamp}.log"
                file_handler = logging.FileHandler(file_name, encoding="utf-8")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

        return logger

    def _get_level(self, level_name):
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        return levels.get(level_name.upper(), logging.INFO)
