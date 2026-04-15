"""
AI 绘图服务
"""
import os
import uuid
import base64
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

from models.drawing import TaskStatus
from utils.logger import log_ai_drawing_event, log_error
from config import settings


class DrawingService:
    """AI 绘图服务"""

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        os.makedirs(settings.IMAGES_DIR, exist_ok=True)

    def create_task(self, request_data: Dict[str, Any]) -> str:
        """创建绘图任务，返回 task_id"""
        task_id = str(uuid.uuid4())

        self.tasks[task_id] = {
            "task_id": task_id,
            "prompt": request_data["prompt"],
            "cfg_scale": request_data.get("cfg_scale", 5),
            "aspect_ratio": request_data.get("aspect_ratio", "16:9"),
            "seed": request_data.get("seed", 0),
            "steps": request_data.get("steps", 50),
            "negative_prompt": request_data.get("negative_prompt", ""),
            "status": TaskStatus.QUEUED.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error_message": None,
            "image_files": [],
        }

        log_ai_drawing_event(task_id, "Task created", f"Prompt: '{request_data['prompt'][:50]}...'")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: str,
                          result: Any = None, error_message: str = None,
                          image_files: List = None):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error_message is not None:
                self.tasks[task_id]["error_message"] = error_message
            if image_files is not None:
                self.tasks[task_id]["image_files"] = image_files

    def call_nvidia_api(self, task_id: str, request_data: Dict[str, Any]):
        """调用 NVIDIA API 生成图片（同步调用，建议后台执行）"""
        api_key = settings.NVIDIA_API_KEY
        if not api_key:
            self.update_task_status(task_id, TaskStatus.FAILED.value,
                                   error_message="NVIDIA_API_KEY environment variable not set")
            log_error("CONFIG_ERROR", f"Task {task_id}: NVIDIA_API_KEY not set")
            return

        # 更新状态为处理中
        self.update_task_status(task_id, TaskStatus.PROCESSING.value)
        log_ai_drawing_event(task_id, "Calling NVIDIA API",
                            f"Prompt: '{request_data['prompt'][:50]}...'")

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            }

            response = requests.post(
                settings.NVIDIA_API_URL,
                headers=headers,
                json=request_data,
                timeout=120
            )
            response.raise_for_status()
            response_body = response.json()

            log_ai_drawing_event(task_id, "NVIDIA API response received")

            # 解析并保存图片
            saved_images = self._save_images(task_id, response_body)

            self.update_task_status(
                task_id,
                TaskStatus.COMPLETED.value,
                result=response_body,
                image_files=saved_images
            )
            log_ai_drawing_event(task_id, "Completed", f"Saved {len(saved_images)} images")

        except requests.exceptions.Timeout:
            error_msg = "NVIDIA API timeout"
            self.update_task_status(task_id, TaskStatus.FAILED.value, error_message=error_msg)
            log_error("NVIDIA_API_TIMEOUT", f"Task {task_id}: {error_msg}")

        except requests.exceptions.RequestException as e:
            error_msg = f"NVIDIA API error: {str(e)}"
            self.update_task_status(task_id, TaskStatus.FAILED.value, error_message=error_msg)
            log_error("NVIDIA_API_ERROR", f"Task {task_id}: {error_msg}")

        except Exception as e:
            error_msg = f"Internal error: {str(e)}"
            self.update_task_status(task_id, TaskStatus.FAILED.value, error_message=error_msg)
            log_error("INTERNAL_ERROR", f"Task {task_id}: {error_msg}", e)

    def _save_images(self, task_id: str, response_body: Dict) -> List[Dict]:
        """解析并保存图片"""
        saved_images = []
        image_data_list = response_body.get("images") or response_body.get("image")

        if not image_data_list:
            return saved_images

        if not isinstance(image_data_list, list):
            image_data_list = [image_data_list]

        for idx, image_data in enumerate(image_data_list):
            if not isinstance(image_data, str):
                log_ai_drawing_event(task_id, f"Non-string image data at index {idx}", "Skipping")
                continue

            # 统一添加 base64 前缀并解码
            try:
                # 处理有无 data URI 前缀的情况
                if "," in image_data:
                    # 有 data URI 前缀，如 "data:image/jpeg;base64,/9j/4AAQ..."
                    b64_data = image_data.split(",", 1)[1]
                else:
                    # 没有前缀，直接是 base64 字符串
                    b64_data = image_data

                image_bytes = base64.b64decode(b64_data)
            except Exception as e:
                log_ai_drawing_event(task_id, f"Failed to decode image {idx}", str(e))
                continue

            # NVIDIA SD3 返回 JPEG 格式
            filename = f"{task_id}_{idx}.jpg"
            filepath = os.path.join(settings.IMAGES_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            saved_images.append({
                "filename": filename,
                "filepath": filepath,
                "url": f"/ai/draw/{task_id}/download/{filename}",
                "size_bytes": len(image_bytes),
                "format": "jpeg"
            })

            log_ai_drawing_event(task_id, "Image saved", f"{filename} ({len(image_bytes)} bytes)")

        return saved_images

    def get_history(self) -> Dict:
        """获取所有任务历史"""
        tasks = list(self.tasks.values())
        tasks.sort(key=lambda x: x["created_at"], reverse=True)

        completed = [t for t in tasks if t["status"] == TaskStatus.COMPLETED.value]
        failed = [t for t in tasks if t["status"] == TaskStatus.FAILED.value]

        return {
            "tasks": tasks,
            "total": len(tasks),
            "completed_count": len(completed),
            "failed_count": len(failed)
        }


# 全局单例
drawing_service = DrawingService()