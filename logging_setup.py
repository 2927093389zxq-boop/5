import logging
import sys
import json
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

def setup_logging(level: str = "INFO", json_mode: bool = False):
    """
    统一日志初始化:
    - 主文件 logs/app.log 按日轮转
    - 可选 JSON 格式
    """
    root = logging.getLogger()
    if root.handlers:
        return  # 避免重复初始化

    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt_text = "%(asctime)s %(levelname)s %(name)s %(message)s"

    if json_mode:
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                base = {
                    "time": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "msg": record.getMessage()
                }
                return json.dumps(base, ensure_ascii=False)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(fmt_text)

    file_handler = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)