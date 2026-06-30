import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from config import LOGS_DIR, APP_NAME, APP_VERSION


LOG_FILE = Path(LOGS_DIR) / "radar_mm.log"


def get_logger(name="radar"):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()


def log_start():
    logger.info(f"Iniciando {APP_NAME} {APP_VERSION}")


def log_end():
    logger.info("Ejecucion finalizada")


def log_error(contexto, error):
    logger.error(f"{contexto}: {str(error)}")


def log_event(evento, data=None):
    if data is None:
        logger.info(evento)
    else:
        logger.info(f"{evento} | {data}")


def execution_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
