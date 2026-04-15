"""
微信公众号文章模型
"""
from pydantic import BaseModel, Field
from typing import List


class WechatArticleRequest(BaseModel):
    """微信公众号文章请求"""
    wechat_url: str = Field(..., description="微信公众号文章链接")


class WechatParagraphs(BaseModel):
    """微信公众号文章段落响应"""
    title: str = Field(..., description="文章标题，带【微信】前缀")
    paragraphs: List[str] = Field(..., description="文章段落列表")