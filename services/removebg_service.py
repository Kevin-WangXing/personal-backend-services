""" Remove.bg 抠图服务 """
import os
import uuid
import time
import base64
import shutil
import requests
from pathlib import Path
from config import settings
from utils.logger import log_api_access, log_ai_drawing_event

# API endpoint and key
REMOVEBG_API_URL = "https://api.remove.bg/v1.0/removebg"
REMOVEBG_API_KEY = "egRNGjYh31byLBV897nRNdRv"

# 存储路径
STORAGE_DIR = Path("storage/removebg")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class RemoveBgService:
    """Remove.bg 抠图服务（同步调用）"""

    def remove_background(self, image_url: str) -> dict:
        """
        调用 remove.bg API 去除背景
        image_url: 可访问的图片URL
        返回: {
            "status": "completed" | "failed",
            "message": str,
            "filepath": str,       # 本地文件路径
            "filename": str,       # 文件名
            "url": str,            # 下载URL
            "size_bytes": int,
        }
        """
        task_id = str(uuid.uuid4())[:8]
        log_ai_drawing_event(f"removebg-{task_id}", "Start", f"Fetching image from: {image_url[:80]}")

        try:
            # Step 1: 下载源图
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            resp = requests.get(image_url, headers=headers, timeout=30)
            if resp.status_code != 200:
                return {
                    "status": "failed",
                    "message": f"Failed to fetch image, HTTP {resp.status_code}",
                    "filepath": None,
                    "filename": None,
                    "url": None,
                    "size_bytes": 0,
                }

            # 推断格式
            content_type = resp.headers.get("Content-Type", "image/png")
            ext = content_type.split("/")[-1]
            if ext == "jpeg":
                ext = "jpg"
            ext = ext.replace("jpg", "jpg").replace("png", "png")

            # 保存源图（用于传给 remove.bg）
            source_path = STORAGE_DIR / f"source_{task_id}.{ext}"
            with open(source_path, "wb") as f:
                f.write(resp.content)

            log_ai_drawing_event(f"removebg-{task_id}", "Image downloaded",
                                 f"Size: {len(resp.content)} bytes, saved to {source_path}")

            # Step 2: 调用 remove.bg API
            with open(source_path, "rb") as f:
                files = {"image_file": f}
                data = {
                    "format": "png",
                    "type": "auto",
                }
                headers = {
                    "X-Api-Key": REMOVEBG_API_KEY,
                }
                api_resp = requests.post(
                    REMOVEBG_API_URL,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=60
                )

            # 清理源图
            os.remove(source_path)

            if api_resp.status_code != 200:
                error_msg = api_resp.text
                log_ai_drawing_event(f"removebg-{task_id}", "API failed",
                                     f"HTTP {api_resp.status_code}: {error_msg[:200]}")
                return {
                    "status": "failed",
                    "message": f"Remove.bg API error {api_resp.status_code}: {error_msg[:200]}",
                    "filepath": None,
                    "filename": None,
                    "url": None,
                    "size_bytes": 0,
                }

            # Step 3: 保存结果图
            result_filename = f"removebg_{task_id}.png"
            result_path = STORAGE_DIR / result_filename
            with open(result_path, "wb") as f:
                f.write(api_resp.content)

            size = len(api_resp.content)
            url = f"/removebg/download/{result_filename}"

            log_ai_drawing_event(f"removebg-{task_id}", "Success",
                                 f"Result saved: {result_filename}, size: {size} bytes")

            return {
                "status": "completed",
                "message": "Background removed successfully",
                "filepath": str(result_path),
                "filename": result_filename,
                "url": url,
                "size_bytes": size,
            }

        except Exception as e:
            log_ai_drawing_event(f"removebg-{task_id}", "Error", str(e))
            return {
                "status": "failed",
                "message": str(e),
                "filepath": None,
                "filename": None,
                "url": None,
                "size_bytes": 0,
            }


removebg_service = RemoveBgService()