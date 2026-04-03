"""
核心插件 - 限流器插件

功能：
1. 防止 API 被限流或封禁
2. 基于滑动窗口的限流算法
3. 自动等待可用配额
"""
import logging
import time
from typing import Optional, Any, Dict

from ..base import CorePlugin


logger = logging.getLogger(__name__)


class RateLimiterPlugin(CorePlugin):
    """
    限流器插件 - 核心插件
    """
    
    def __init__(self, max_calls: int = 100, period: float = 60):
        from common.rate_limiter import RateLimiter
        self._limiter = RateLimiter(max_calls=max_calls, period=period)
    
    @property
    def name(self) -> str:
        return "rate_limiter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "限流器 - 防止 API 被限流或封禁"
    
    @property
    def author(self) -> str:
        return "System"
    
    def before_request(self, method: str, url: str, **kwargs) -> Optional[Any]:
        """请求前获取令牌"""
        if not self._limiter.acquire():
            wait_time = 0.1
            logger.debug(f"请求被限流，等待 {wait_time}s 后重试")
            self._limiter.wait()
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取限流器统计信息"""
        return {
            "max_calls": self._limiter.max_calls,
            "period": self._limiter.period,
            "current_calls": len(self._limiter.calls)
        }
