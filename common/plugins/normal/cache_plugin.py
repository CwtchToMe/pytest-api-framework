"""
普通插件 - 缓存插件

功能：缓存 GET 请求
"""
import logging
import time
from typing import Optional, Any, Dict

from ..base import Plugin


logger = logging.getLogger(__name__)


class CachePlugin(Plugin):
    """缓存插件 - 缓存GET请求"""
    
    def __init__(self, cache_ttl: int = 300):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = cache_ttl
        self._cache_times: Dict[str, float] = {}
    
    @property
    def name(self) -> str:
        return "cache"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "缓存GET请求"
    
    @property
    def author(self) -> str:
        return "System"
    
    def _get_cache_key(self, method: str, url: str, **kwargs) -> str:
        """生成缓存键"""
        return f"{method}_{url}_{str(kwargs)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._cache_times:
            return False
        return time.time() - self._cache_times[cache_key] < self.cache_ttl
    
    def before_request(self, method: str, url: str, **kwargs) -> Optional[Any]:
        """检查缓存"""
        if method.upper() != 'GET':
            return None
        
        cache_key = self._get_cache_key(method, url, **kwargs)
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            logger.debug(f"缓存命中: {url}")
            return self.cache[cache_key]
        return None
    
    def after_request(self, response, method: str, url: str, **kwargs):
        """缓存响应"""
        if method.upper() == 'GET' and hasattr(response, 'status_code') and response.status_code == 200:
            cache_key = self._get_cache_key(method, url, **kwargs)
            self.cache[cache_key] = response
            self._cache_times[cache_key] = time.time()
            logger.debug(f"已缓存: {url}")
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self._cache_times.clear()
        logger.info("缓存已清空")
