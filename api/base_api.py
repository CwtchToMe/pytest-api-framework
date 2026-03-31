"""
API 基础类 - 类似 Page Object 模式的 API 封装

这个模块提供了 API 调用的基础抽象，使得：
1. 所有 API 调用有统一的入口
2. 易于维护 API 端点和参数
3. 便于添加通用的错误处理和日志记录
"""
import logging
import allure
from typing import Optional, Dict, Any
from common.base_requests import BaseRequests


logger = logging.getLogger(__name__)


class BaseApi:
    """API 基础类 - 所有 API 操作的通用父类"""
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        enable_circuit_breaker: bool = False,
        enable_rate_limiter: bool = False,
        enable_plugins: bool = False
    ):
        """
        初始化 API 基类
        
        Args:
            base_url: 基础 URL
            timeout: 请求超时时间
            enable_circuit_breaker: 是否启用熔断器
            enable_rate_limiter: 是否启用限流器
            enable_plugins: 是否启用插件系统
        """
        self.base_url = base_url
        self.timeout = timeout
        self.requests = BaseRequests(
            base_url=base_url,
            enable_circuit_breaker=enable_circuit_breaker,
            enable_rate_limiter=enable_rate_limiter,
            enable_plugins=enable_plugins
        )
    
    def _log_request(self, method: str, url: str, **kwargs):
        """记录请求信息"""
        logger.info(f"{method} {url}")
        if 'json' in kwargs:
            logger.debug(f"Request body: {kwargs['json']}")
    
    def _log_response(self, response):
        """记录响应信息"""
        logger.info(f"Response Status: {response.status_code}")
        
        # 安全地记录响应内容
        try:
            if hasattr(response, 'text'):
                text = response.text
                if isinstance(text, str):
                    logger.debug(f"Response body: {text[:500]}")
                else:
                    logger.debug(f"Response body: {text}")
        except Exception as e:
            logger.debug(f"Response body: Unable to read response text - {e}")
    
    @allure.step("GET 请求: {url}")
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送 GET 请求"""
        self._log_request("GET", f"{self.base_url}{url}")
        
        response = self.requests.get(
            url,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    @allure.step("POST 请求: {url}")
    def post(self, url: str, json_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """发送 POST 请求"""
        self._log_request("POST", f"{self.base_url}{url}", json=json_data)
        
        response = self.requests.post(
            url,
            json=json_data,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    @allure.step("PUT 请求: {url}")
    def put(self, url: str, json_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """发送 PUT 请求"""
        self._log_request("PUT", f"{self.base_url}{url}", json=json_data)
        
        response = self.requests.put(
            url,
            json=json_data,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    @allure.step("DELETE 请求: {url}")
    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送 DELETE 请求"""
        self._log_request("DELETE", f"{self.base_url}{url}")
        
        response = self.requests.delete(
            url,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def close(self):
        """关闭请求客户端"""
        if hasattr(self.requests, 'close'):
            self.requests.close()
