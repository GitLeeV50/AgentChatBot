# Logging manager

import logging
from utils.path_handler import get_abs_path
import os
from datetime import datetime

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")

# 确保日志的目录存在
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志的格式配置  error info debug
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
        name: str = "app",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file: str = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加Handler
    if logger.handlers:
        return logger

    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    # 文件Handler
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger


# 预置常用日志器
logger = get_logger("app")          # 通用业务日志 -> logs/app.log
error_logger = get_logger("errors") # 错误日志 -> logs/errors.log
llm_logger = get_logger("llm_calls") # LLM 调用日志 -> logs/llm_calls.log