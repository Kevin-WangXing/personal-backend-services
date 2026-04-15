""" Remove.bg 抠图模型 """
from pydantic import BaseModel, HttpUrl
from typing import Optional


class RemoveBgRequest(BaseModel):
    """抠图请求"""
    image_url: Optional[str] = None  # 图片URL（二选一）


class RemoveBgImageFile(BaseModel):
    """抠图结果图片"""
    filename: str
    url: str
    size_bytes: int
    format: str  # png


class RemoveBgResponse(BaseModel):
    """抠图响应"""
    task_id: str
    status: str  # completed / failed
    message: str
    download_url: Optional[str] = None
    image: Optional[RemoveBgImageFile] = None