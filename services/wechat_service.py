"""
微信公众号文章解析服务
"""
import re
from typing import Optional
from wechat_article_parser import parse_async
from utils.logger import log_ai_drawing_event, log_error

# 默认浏览器 UA
DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class WechatService:
    """微信公众号文章解析服务"""

    async def fetch_article(
        self,
        url: str,
        user_agent: Optional[str] = None,
        timeout: int = 30,
    ) -> Optional[dict]:
        """
        获取微信公众号文章内容

        Args:
            url: 文章链接
            user_agent: 浏览器 User-Agent，不传则用默认值
            timeout: 请求超时时间（秒）

        返回格式:
        {
            "title": "【微信】文章标题",
            "paragraphs": ["01", "第一段", "02", "第二段", ...]
        }
        """
        ua = user_agent or DEFAULT_UA

        try:
            result = await parse_async(url, timeout=timeout, user_agent=ua)

            if not result.is_valid:
                log_error("WECHAT_PARSE_ERROR", f"Article not valid or blocked: {url}")
                return None

            # 去掉图片引用（保留纯文本）
            md = result.article_markdown
            md = re.sub(r'!\[.*?\]\(.*?\)', '', md)

            # 按行分割，收集非空段落
            lines = md.split('\n')
            paragraphs = []
            for line in lines:
                line = line.strip()
                if line:
                    paragraphs.append(line)

            title = f"【微信】{result.article_title}"

            log_ai_drawing_event("wechat", "Article fetched", title)

            return {
                "title": title,
                "paragraphs": paragraphs,
            }

        except Exception as e:
            log_error("WECHAT_FETCH_ERROR", f"Failed to fetch article: {url}", e)
            return None


# 全局单例
wechat_service = WechatService()