""" Remove.bg 抠图路由 """
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from models.removebg import RemoveBgRequest, RemoveBgResponse, RemoveBgImageFile
from services.removebg_service import removebg_service
from utils.logger import log_api_access

router = APIRouter(prefix="/removebg", tags=["Remove.bg 抠图"])

STORAGE_DIR = "storage/removebg"


@router.post("", response_model=RemoveBgResponse)
async def remove_background(request: RemoveBgRequest):
    """
    抠图接口 - 去除图片背景
    请求体: { "image_url": "https://..." }
    响应: 抠图结果图片URL（可直接下载）
    """
    log_api_access("/removebg", "POST", 200)

    if not request.image_url:
        log_api_access("/removebg", "POST", 400)
        raise HTTPException(status_code=400, detail="image_url is required")

    result = removebg_service.remove_background(request.image_url)

    if result["status"] == "failed":
        log_api_access("/removebg", "POST", 500)
        raise HTTPException(status_code=500, detail=result["message"])

    image_file = RemoveBgImageFile(
        filename=result["filename"],
        url=result["url"],
        size_bytes=result["size_bytes"],
        format="png",
    )

    return RemoveBgResponse(
        task_id="sync",  # 同步执行，无任务ID
        status="completed",
        message=result["message"],
        download_url=result["url"],
        image=image_file,
    )


@router.get("/download/{filename}")
async def download_result(filename: str):
    """下载抠图结果"""
    # 安全检查：只允许下载 removebg_ 开头的文件
    if not filename.startswith("removebg_"):
        log_api_access(f"/removebg/download/{filename}", "GET", 403)
        raise HTTPException(status_code=403, detail="Invalid filename")

    filepath = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(filepath):
        log_api_access(f"/removebg/download/{filename}", "GET", 404)
        raise HTTPException(status_code=404, detail="File not found")

    log_api_access(f"/removebg/download/{filename}", "GET", 200)
    return FileResponse(path=filepath, filename=filename, media_type="image/png")