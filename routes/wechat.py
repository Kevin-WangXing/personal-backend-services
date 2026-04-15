"""
微信公众号文章路由
"""
from fastapi import APIRouter, HTTPException

from models.wechat import WechatArticleRequest, WechatParagraphs
from services.wechat_service import wechat_service
from utils.logger import log_api_access

router = APIRouter(prefix="/wechat", tags=["微信公众号文章"])


@router.post("/article", response_model=list)
async def get_wechat_article(request: WechatArticleRequest):
    """
    根据微信公众号文章链接获取文章内容

    支持传入 User-Agent 请求头模拟浏览器访问，提升解析成功率

    请求体:
    {
        "wechat_url": "https://mp.weixin.qq.com/s/xxxx"
    }

    响应: [{
        "title": "【微信】文章标题",
        "paragraphs": ["01", "段落1", "02", "段落2", ...]
    }]
    """
    log_api_access("/wechat/article", "POST", 200)

    # 简单校验 URL
    if "mp.weixin.qq.com" not in request.wechat_url:
        log_api_access("/wechat/article", "POST", 400)
        raise HTTPException(status_code=400, detail="Invalid WeChat article URL")

    result = await wechat_service.fetch_article(url=request.wechat_url)

    if result is None:
        log_api_access("/wechat/article", "POST", 500)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch article, may need browser-like User-Agent"
        )

    return [WechatParagraphs(**result)]