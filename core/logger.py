import logging
import sys
import os
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

        if logger.handlers:
            return logger

        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")

        if not self._suppress_stdout:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if self._output_path:
            try:
                os.makedirs(self._output_path, exist_ok=True)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                file_name = f"{self._output_path}/shadowaudit_{timestamp}.log"
                file_handler = logging.FileHandler(file_name, encoding="utf-8")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                fallback_handler = logging.StreamHandler(sys.stderr)
                fallback_handler.setFormatter(formatter)
                logger.addHandler(fallback_handler)
                logger.error(f"[LOGGER INIT ERROR] Failed to initialize file logger: {e}")

        return logger

    def _get_level(self, level_name):
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        return levels.get(level_name.upper(), logging.INFO)
