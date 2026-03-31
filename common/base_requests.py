"""
HTTP 请求基类封装 - 支持自动重试、熔断、限流、插件等企业级特性
"""
import requests
import allure
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
from config.config import config

logger = logging.getLogger(__name__)


class BaseRequests:
    """API 请求基类 - 支持企业级特性"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        enable_circuit_breaker: bool = False,
        enable_rate_limiter: bool = False,
        enable_plugins: bool = False
    ):
        """
        初始化 BaseRequests
        
        Args:
            base_url: API 基础 URL（如果不提供则从配置读取）
            max_retries: 最大重试次数
            backoff_factor: 重试间隔因子
            enable_circuit_breaker: 是否启用熔断器
            enable_rate_limiter: 是否启用限流器
            enable_plugins: 是否启用插件系统
        """
        self.session = requests.Session()
        self.base_url = base_url or config.API_BASE_URL
        
        # 初始化熔断器
        self.enable_circuit_breaker = enable_circuit_breaker
        if enable_circuit_breaker:
            from common.circuit_breaker import get_circuit_breaker_manager
            self.circuit_breaker_manager = get_circuit_breaker_manager()
            self.circuit_breaker = self.circuit_breaker_manager.get('api_requests')
            logger.info("熔断器已启用")
        else:
            self.circuit_breaker = None
        
        # 初始化限流器
        self.enable_rate_limiter = enable_rate_limiter
        if enable_rate_limiter:
            from common.rate_limiter import RateLimiter
            self.rate_limiter = RateLimiter(
                max_calls=100,  # 每分钟最多 100 个请求
                period=60
            )
            logger.info("限流器已启用")
        else:
            self.rate_limiter = None
        
        # 初始化插件管理器
        self.enable_plugins = enable_plugins
        if enable_plugins:
            from common.plugin_system import get_plugin_manager
            self.plugin_manager = get_plugin_manager()
            logger.info("插件系统已启用")
        else:
            self.plugin_manager = None
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"初始化 BaseRequests，API 基础 URL: {self.base_url}，最大重试次数: {max_retries}")
    
    def _prepare_request(self, method: str, url: str, **kwargs):
        """准备请求（限流、插件钩子）"""
        # 限流
        if self.rate_limiter:
            while not self.rate_limiter.acquire():
                logger.debug("请求被限流，等待中...")
                time.sleep(0.1)
        
        # 插件钩子 - 请求前
        if self.plugin_manager:
            self.plugin_manager.execute_hook('before_request', method, url, **kwargs)
    
    def _handle_response(self, response: requests.Response, endpoint: str) -> requests.Response:
        """
        统一处理响应
        
        Args:
            response: 响应对象
            endpoint: 请求端点
            
        Returns:
            处理后的响应对象
        """
        # 插件钩子 - 请求后
        if self.plugin_manager:
            self.plugin_manager.execute_hook('after_request', response, endpoint)
        
        if response.status_code >= 400:
            logger.error(f"请求失败: {endpoint} | 状态码: {response.status_code} | 响应: {response.text[:200]}")
        
        return response
    
    @allure.step("发送 GET 请求: {endpoint}")
    def get(self, endpoint, params=None, **kwargs):
        """GET 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} | 参数: {params}")
        
        # 准备请求
        self._prepare_request('GET', url, params=params, **kwargs)
        
        # 熔断保护
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                self._get_internal,
                url,
                params,
                **kwargs
            )
        else:
            return self._get_internal(url, params, **kwargs)
    
    def _get_internal(self, url, params, **kwargs):
        """内部 GET 请求实现"""
        try:
            response = self.session.get(url, params=params, timeout=config.API_TIMEOUT, **kwargs)
            return self._handle_response(response, url)
        except requests.exceptions.RequestException as e:
            logger.error(f"GET 请求异常: {url} | 错误: {e}")
            raise
    
    @allure.step("发送 POST 请求: {endpoint}")
    def post(self, endpoint, json=None, data=None, **kwargs):
        """POST 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url} | 数据: {json or data}")
        
        # 准备请求
        self._prepare_request('POST', url, json=json, data=data, **kwargs)
        
        # 熔断保护
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                self._post_internal,
                url,
                json,
                data,
                **kwargs
            )
        else:
            return self._post_internal(url, json, data, **kwargs)
    
    def _post_internal(self, url, json, data, **kwargs):
        """内部 POST 请求实现"""
        try:
            response = self.session.post(url, json=json, data=data, timeout=config.API_TIMEOUT, **kwargs)
            return self._handle_response(response, url)
        except requests.exceptions.RequestException as e:
            logger.error(f"POST 请求异常: {url} | 错误: {e}")
            raise
    
    @allure.step("发送 PUT 请求: {endpoint}")
    def put(self, endpoint, json=None, **kwargs):
        """PUT 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT {url} | 数据: {json}")
        
        # 准备请求
        self._prepare_request('PUT', url, json=json, **kwargs)
        
        # 熔断保护
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                self._put_internal,
                url,
                json,
                **kwargs
            )
        else:
            return self._put_internal(url, json, **kwargs)
    
    def _put_internal(self, url, json, **kwargs):
        """内部 PUT 请求实现"""
        try:
            response = self.session.put(url, json=json, timeout=config.API_TIMEOUT, **kwargs)
            return self._handle_response(response, url)
        except requests.exceptions.RequestException as e:
            logger.error(f"PUT 请求异常: {url} | 错误: {e}")
            raise
    
    @allure.step("发送 DELETE 请求: {endpoint}")
    def delete(self, endpoint, **kwargs):
        """DELETE 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE {url}")
        
        # 准备请求
        self._prepare_request('DELETE', url, **kwargs)
        
        # 熔断保护
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                self._delete_internal,
                url,
                **kwargs
            )
        else:
            return self._delete_internal(url, **kwargs)
    
    def _delete_internal(self, url, **kwargs):
        """内部 DELETE 请求实现"""
        try:
            response = self.session.delete(url, timeout=config.API_TIMEOUT, **kwargs)
            return self._handle_response(response, url)
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE 请求异常: {url} | 错误: {e}")
            raise
    
    def close(self):
        """关闭会话"""
        self.session.close()
        logger.debug("BaseRequests 会话已关闭")
