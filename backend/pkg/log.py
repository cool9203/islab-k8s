import yaml
import logging
from pathlib import Path

log_path = "./log"
log_fmt = "%(asctime)s %(levelname)s %(pathname)s.%(lineno)d %(message)s"
log_datefmt = "%Y/%m/%d %I:%M:%S"

def get_logger(**kwargs):
    params = locals()["kwargs"]
    log_file_name = params.get("log_file_name")
    logger_name = params.get("logger_name", "")
    log_level = params.get("log_level", "INFO")

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.getLevelName(log_level))
    formatter = logging.Formatter(log_fmt, datefmt=log_datefmt)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.getLevelName(log_level))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler(str(Path(log_path, f"{log_file_name}.log")), mode="w")
    handler.setLevel(logging.getLevelName(log_level))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
