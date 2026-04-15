"""
日志工具
"""
import logging
import os
from datetime import datetime


def setup_logging():
    """初始化日志配置（仅执行一次）"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_date = datetime.now().strftime("%Y%m%d")

    # 避免重复添加 handler
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.INFO)
    root.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 文件 handler
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"app_{log_date}.log"),
        encoding="utf-8"
    )
    file_handler.setFormatter(root.formatter)
    root.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(root.formatter)
    root.addHandler(console_handler)

    # 子 logger
    for logger_name, filename in [
        ("ai_drawing", f"ai_drawing_{log_date}.log"),
        ("api_access", f"api_access_{log_date}.log"),
        ("errors", f"errors_{log_date}.log"),
    ]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            os.path.join(log_dir, filename),
            encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)


def log_api_access(endpoint: str, method: str, status_code: int):
    """记录 API 访问"""
    logger = logging.getLogger("api_access")
    logger.info(f"{method} {endpoint} - Status: {status_code}")


def log_ai_drawing_event(task_id: str, event: str, details: str = None):
    """记录 AI 绘图事件"""
    logger = logging.getLogger("ai_drawing")
    msg = f"Task {task_id}: {event}"
    if details:
        msg += f" - {details}"
    logger.info(msg)


def log_error(error_type: str, message: str, exception: Exception = None):
    """记录错误"""
    logger = logging.getLogger("errors")
    msg = f"{error_type}: {message}"
    if exception:
        msg += f" - Exception: {str(exception)}"
    logger.error(msg)


# 初始化
setup_logging()