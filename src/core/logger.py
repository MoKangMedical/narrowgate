"""
窄门 (NarrowGate) - 日志系统

统一的日志管理，支持控制台和文件输出
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "narrowgate", level: str = "INFO") -> logging.Logger:
    """设置并返回logger实例"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 所有日志
    all_log_file = LOG_DIR / f"narrowgate_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        all_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 文件处理器 - 错误日志
    error_log_file = LOG_DIR / f"error_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的logger"""
    return logging.getLogger(f"narrowgate.{name}")


# 创建默认logger
default_logger = setup_logger()


def info(msg: str, *args, **kwargs):
    default_logger.info(msg, *args, **kwargs)


def debug(msg: str, *args, **kwargs):
    default_logger.debug(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    default_logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    default_logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    default_logger.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    default_logger.exception(msg, *args, **kwargs)