"""
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置"""

    # 服务器
    HOST = "0.0.0.0"
    PORT = 9000

    # NVIDIA API
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_API_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"

    # 存储
    STORAGE_DIR = "storage"
    IMAGES_DIR = os.path.join(STORAGE_DIR, "images")
    LOGS_DIR = "logs"

    # 绘图默认值
    DEFAULT_CFG_SCALE = 5
    DEFAULT_ASPECT_RATIO = "16:9"
    DEFAULT_STEPS = 50


settings = Settings()