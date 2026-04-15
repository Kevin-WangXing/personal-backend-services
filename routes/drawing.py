"""
AI 绘图路由
"""
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse

from models.drawing import (
    DrawingRequest,
    DrawingTaskResponse,
    DrawingTaskStatusResponse,
    DrawingHistoryResponse,
    DrawingHistoryItem,
    ImageFile,
    DownloadResponse,
)
from services.drawing_service import drawing_service
from utils.logger import log_api_access, log_ai_drawing_event
from config import settings


router = APIRouter(prefix="/ai/draw", tags=["AI 绘图"])


def _build_task_response(task_id: str, task: dict) -> DrawingTaskResponse:
    """构建任务创建响应"""
    download_url = f"/ai/draw/{task_id}/download"
    status_url = f"/ai/draw/{task_id}/status"
    individual_urls = [
        f"/ai/draw/{task_id}/download/{img['filename']}"
        for img in task.get("image_files", [])
    ]
    return DrawingTaskResponse(
        task_id=task_id,
        status=task["status"],
        message="Drawing task created successfully",
        created_at=task["created_at"],
        download_url=download_url,
        status_url=status_url,
        individual_download_urls=individual_urls,
    )


def _build_status_response(task_id: str, task: dict) -> DrawingTaskStatusResponse:
    """构建任务状态响应"""
    prompt = task["prompt"]
    if len(prompt) > 100:
        prompt = prompt[:100] + "..."

    image_files = [
        ImageFile(
            filename=img["filename"],
            url=img["url"],
            size_bytes=img["size_bytes"],
            format=img["format"],
        )
        for img in task.get("image_files", [])
    ]

    return DrawingTaskStatusResponse(
        task_id=task_id,
        prompt=prompt,
        status=task["status"],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        error_message=task.get("error_message"),
        image_count=len(image_files),
        download_links=[img.url for img in image_files],
        image_files=image_files,
    )


@router.post("", response_model=DrawingTaskResponse)
async def create_drawing_task(request: DrawingRequest, background_tasks: BackgroundTasks):
    """创建绘图任务"""
    log_api_access("/ai/draw", "POST", 200)

    request_data = {
        "prompt": request.prompt,
        "cfg_scale": request.cfg_scale,
        "aspect_ratio": request.aspect_ratio,
        "seed": request.seed,
        "steps": request.steps,
        "negative_prompt": request.negative_prompt,
    }

    task_id = drawing_service.create_task(request_data)

    # 后台执行 NVIDIA API 调用
    background_tasks.add_task(
        drawing_service.call_nvidia_api,
        task_id,
        request_data
    )

    task = drawing_service.get_task(task_id)
    return _build_task_response(task_id, task)


@router.get("/{task_id}/status", response_model=DrawingTaskStatusResponse)
async def get_drawing_task_status(task_id: str):
    """查询绘图任务状态"""
    task = drawing_service.get_task(task_id)
    if not task:
        log_api_access(f"/ai/draw/{task_id}/status", "GET", 404)
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    log_api_access(f"/ai/draw/{task_id}/status", "GET", 200)
    return _build_status_response(task_id, task)


@router.get("/{task_id}/download")
async def download_drawing_task(task_id: str):
    """下载绘图任务的图片"""
    task = drawing_service.get_task(task_id)
    if not task:
        log_api_access(f"/ai/draw/{task_id}/download", "GET", 404)
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if task["status"] != "completed":
        log_api_access(f"/ai/draw/{task_id}/download", "GET", 400)
        raise HTTPException(status_code=400, detail=f"Task {task_id} is not completed yet")

    image_files = task.get("image_files", [])
    if not image_files:
        log_api_access(f"/ai/draw/{task_id}/download", "GET", 404)
        raise HTTPException(status_code=404, detail=f"No images found for task {task_id}")

    log_api_access(f"/ai/draw/{task_id}/download", "GET", 200)
    log_ai_drawing_event(task_id, "Download requested", f"Returning {len(image_files)} images")

    # 单张图片直接返回文件
    if len(image_files) == 1:
        img = image_files[0]
        return FileResponse(
            path=img["filepath"],
            filename=img["filename"],
            media_type="image/jpeg"
        )

    # 多张图片返回下载链接列表
    images = [
        ImageFile(
            filename=img["filename"],
            url=img["url"],
            size_bytes=img["size_bytes"],
            format=img["format"],
        )
        for img in image_files
    ]

    return DownloadResponse(
        task_id=task_id,
        image_count=len(images),
        images=images,
        message="Multiple images generated, please download individually",
        individual_downloads=[img.url for img in images],
    )


@router.get("/{task_id}/download/{filename}")
async def download_specific_image(task_id: str, filename: str):
    """下载特定图片"""
    task = drawing_service.get_task(task_id)
    if not task:
        log_api_access(f"/ai/draw/{task_id}/download/{filename}", "GET", 404)
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if task["status"] != "completed":
        log_api_access(f"/ai/draw/{task_id}/download/{filename}", "GET", 400)
        raise HTTPException(status_code=400, detail=f"Task {task_id} is not completed yet")

    # 查找指定文件
    target_file = None
    for img in task.get("image_files", []):
        if img["filename"] == filename:
            target_file = img
            break

    if not target_file or not os.path.exists(target_file["filepath"]):
        log_api_access(f"/ai/draw/{task_id}/download/{filename}", "GET", 404)
        raise HTTPException(status_code=404, detail=f"Image {filename} not found")

    log_api_access(f"/ai/draw/{task_id}/download/{filename}", "GET", 200)
    return FileResponse(
        path=target_file["filepath"],
        filename=filename,
        media_type="image/jpeg"
    )


@router.get("/history", response_model=DrawingHistoryResponse)
async def get_drawing_history():
    """获取绘图历史"""
    log_api_access("/ai/draw/history", "GET", 200)

    history = drawing_service.get_history()
    tasks = []

    for task in history["tasks"]:
        prompt = task["prompt"]
        if len(prompt) > 100:
            prompt = prompt[:100] + "..."

        download_available = (
            task["status"] == "completed"
            and len(task.get("image_files", [])) > 0
        )

        download_urls = []
        if download_available:
            download_urls = [img["url"] for img in task["image_files"]]

        tasks.append(DrawingHistoryItem(
            task_id=task["task_id"],
            prompt=prompt,
            status=task["status"],
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            image_count=len(task.get("image_files", [])),
            download_available=download_available,
            download_urls=download_urls,
        ))

    log_ai_drawing_event("history", "History requested", f"Returning {len(tasks)} tasks")

    return DrawingHistoryResponse(
        tasks=tasks,
        total=history["total"],
        completed_count=history["completed_count"],
        failed_count=history["failed_count"],
    )