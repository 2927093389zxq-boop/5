"""
日志记录模块
Logging Module
"""
import logging
import os
from datetime import datetime

# 确保日志目录存在 / Ensure log directory exists
os.makedirs("logs", exist_ok=True)

# 配置日志 / Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('scrapers')


def log_info(message: str):
    """记录信息日志 / Log info message"""
    logger.info(message)


def log_error(message: str):
    """记录错误日志 / Log error message"""
    logger.error(message)


def log_warning(message: str):
    """记录警告日志 / Log warning message"""
    logger.warning(message)


def log_debug(message: str):
    """记录调试日志 / Log debug message"""
    logger.debug(message)
