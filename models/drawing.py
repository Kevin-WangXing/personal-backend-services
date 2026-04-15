"""
数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DrawingRequest(BaseModel):
    """AI 绘图请求"""
    prompt: str = Field(..., description="绘图描述文本")
    cfg_scale: float = Field(default=5, ge=1, le=10, description="引导强度")
    aspect_ratio: str = Field(default="16:9", description="宽高比")
    seed: int = Field(default=0, description="随机种子，0表示随机")
    steps: int = Field(default=50, ge=1, le=100, description="采样步数")
    negative_prompt: str = Field(default="", description="反向提示词")


class ImageFile(BaseModel):
    """图片文件信息"""
    filename: str
    url: str
    size_bytes: int
    format: str = "jpeg"


class DrawingTaskResponse(BaseModel):
    """绘图任务响应（创建时）"""
    task_id: str
    status: str
    message: str
    created_at: str
    download_url: str
    status_url: str
    individual_download_urls: List[str]


class DrawingTaskStatusResponse(BaseModel):
    """绘图任务状态响应"""
    task_id: str
    prompt: str
    status: str
    created_at: str
    updated_at: str
    error_message: Optional[str] = None
    image_count: int = 0
    download_links: List[str] = []
    image_files: List[ImageFile] = []


class DrawingHistoryItem(BaseModel):
    """历史记录项"""
    task_id: str
    prompt: str
    status: str
    created_at: str
    updated_at: str
    image_count: int
    download_available: bool
    download_urls: List[str] = []


class DrawingHistoryResponse(BaseModel):
    """绘图历史响应"""
    tasks: List[DrawingHistoryItem]
    total: int
    completed_count: int
    failed_count: int


class DownloadResponse(BaseModel):
    """下载响应（多图时返回的 JSON）"""
    task_id: str
    image_count: int
    images: List[ImageFile]
    message: str
    individual_downloads: List[str]


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str