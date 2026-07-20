"""
HTTP 请求基类封装 - 集成插件系统与自动重试

设计理念：
1. 通过插件系统实现日志、Allure 附件等横切关注点
2. 插件可选启用，默认启用
3. 自动重试机制应对临时性网络故障
"""

import logging
from typing import Any, Dict, Optional

import allure
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.config import config

logger = logging.getLogger(__name__)


class BaseRequests:
    """
    API 请求基类 - 集成插件系统与自动重试

    特性：
    1. 插件系统（日志、Allure 附件）
    2. 自动重试机制（针对 429/5xx）
    3. 统一的响应处理
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        enable_plugins: bool = True,
    ):
        """
        初始化 BaseRequests

        Args:
            base_url: API 基础 URL（如果不提供则从配置读取）
            max_retries: 最大重试次数
            backoff_factor: 重试间隔因子
            enable_plugins: 是否启用插件系统
        """
        self.session = requests.Session()
        self.base_url = base_url or config.API_BASE_URL
        self.enable_plugins = enable_plugins

        if enable_plugins:
            from common.plugins import get_plugin_manager

            self.plugin_manager = get_plugin_manager()
            logger.info(
                f"插件系统已启用，已注册插件: {[p.name for p in self.plugin_manager.get_all_plugins()]}"
            )
        else:
            self.plugin_manager = None

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
                "POST",
            ],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(
            f"初始化 BaseRequests，API 基础 URL: {self.base_url}，最大重试次数: {max_retries}"
        )

    def _execute_with_plugins(self, method: str, url: str, request_func, **kwargs):
        """
        通过插件系统执行请求

        Args:
            method: HTTP 方法
            url: 请求 URL
            request_func: 实际请求函数
            **kwargs: 请求参数

        Returns:
            响应对象
        """
        if self.plugin_manager:
            cached_results = self.plugin_manager.execute_hook(
                "before_request", method, url, **kwargs
            )
            if cached_results:
                return cached_results[0]

        try:
            response = request_func()

            if self.plugin_manager:
                self.plugin_manager.execute_hook(
                    "after_request", response, method, url, **kwargs
                )

            return response

        except Exception as e:
            if self.plugin_manager:
                self.plugin_manager.execute_hook(
                    "on_request_error", e, method, url, **kwargs
                )
            raise

    def _handle_response(
        self, response: requests.Response, endpoint: str
    ) -> requests.Response:
        """
        统一处理响应

        Args:
            response: 响应对象
            endpoint: 请求端点

        Returns:
            处理后的响应对象
        """
        if response.status_code >= 400:
            logger.error(
                f"请求失败: {endpoint} | 状态码: {response.status_code} | 响应: {response.text[:200]}"
            )

        return response

    @allure.step("发送 GET 请求: {endpoint}")
    def get(self, endpoint, params=None, **kwargs):
        """GET 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} | 参数: {params}")

        def request_func():
            try:
                response = self.session.get(
                    url, params=params, timeout=config.API_TIMEOUT, **kwargs
                )
                return self._handle_response(response, url)
            except requests.exceptions.RequestException as e:
                logger.error(f"GET 请求异常: {url} | 错误: {e}")
                raise

        return self._execute_with_plugins(
            "GET", url, request_func, params=params, **kwargs
        )

    @allure.step("发送 POST 请求: {endpoint}")
    def post(self, endpoint, json=None, data=None, **kwargs):
        """POST 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url} | 数据: {json or data}")

        def request_func():
            try:
                response = self.session.post(
                    url, json=json, data=data, timeout=config.API_TIMEOUT, **kwargs
                )
                return self._handle_response(response, url)
            except requests.exceptions.RequestException as e:
                logger.error(f"POST 请求异常: {url} | 错误: {e}")
                raise

        return self._execute_with_plugins(
            "POST", url, request_func, json=json, data=data, **kwargs
        )

    @allure.step("发送 PUT 请求: {endpoint}")
    def put(self, endpoint, json=None, **kwargs):
        """PUT 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT {url} | 数据: {json}")

        def request_func():
            try:
                response = self.session.put(
                    url, json=json, timeout=config.API_TIMEOUT, **kwargs
                )
                return self._handle_response(response, url)
            except requests.exceptions.RequestException as e:
                logger.error(f"PUT 请求异常: {url} | 错误: {e}")
                raise

        return self._execute_with_plugins("PUT", url, request_func, json=json, **kwargs)

    @allure.step("发送 DELETE 请求: {endpoint}")
    def delete(self, endpoint, **kwargs):
        """DELETE 请求"""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE {url}")

        def request_func():
            try:
                response = self.session.delete(
                    url, timeout=config.API_TIMEOUT, **kwargs
                )
                return self._handle_response(response, url)
            except requests.exceptions.RequestException as e:
                logger.error(f"DELETE 请求异常: {url} | 错误: {e}")
                raise

        return self._execute_with_plugins("DELETE", url, request_func, **kwargs)

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.debug("BaseRequests 会话已关闭")
