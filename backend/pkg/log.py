import yaml
import logging
from pathlib import Path

log_path = "./log"
log_fmt = "%(asctime)s %(levelname)s %(pathname)s.%(lineno)d %(message)s"
log_datefmt = "%Y/%m/%d %I:%M:%S"

def load_setting(setting_path=""):
    setting = dict()
    if (not Path(setting_path).exists()):
        raise Exception(f"'{setting_path}' setting not exists")
    with Path(setting_path).open("r", encoding="utf8") as f:
        for line in f.readlines():
            line = line.replace("\n", "").replace("\t", "").replace("\r", "").replace(" ", "")
            if (line[0] == "#"):
                continue
            else:
                line_split = line.split("#")
                key = line_split[0].split("=")[0].upper()
                value = line_split[0].split("=")[1]
                setting[key] = value
    return setting


def get_logger(**kwargs):
    params = locals()["kwargs"]
    name = params.get("name")
    logger_name = params.get("logger_name", "")
    log_level = params["log_level"] if "log_level" in params else params.get("setting", {"LOG_LEVEL":"INFO"})["LOG_LEVEL"]

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.getLevelName(log_level))
    formatter = logging.Formatter(log_fmt, datefmt=log_datefmt)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.getLevelName(log_level))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler(str(Path(log_path, f"{name}.log")), mode="w")
    handler.setLevel(logging.getLevelName(log_level))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
