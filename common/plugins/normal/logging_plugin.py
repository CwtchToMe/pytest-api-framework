"""
普通插件 - 日志插件

功能：记录所有请求和测试日志
"""
import logging
from typing import Optional, Any

from ..base import Plugin


logger = logging.getLogger(__name__)


class LoggingPlugin(Plugin):
    """日志插件 - 记录所有请求和测试"""
    
    @property
    def name(self) -> str:
        return "logging"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "记录请求和测试日志"
    
    @property
    def author(self) -> str:
        return "System"
    
    def before_request(self, method: str, url: str, **kwargs) -> Optional[Any]:
        logger.info(f"[请求前] {method} {url}")
        return None
    
    def after_request(self, response, method: str, url: str, **kwargs):
        status = getattr(response, 'status_code', 'N/A')
        logger.info(f"[请求后] {method} {url} | 状态: {status}")
    
    def on_request_error(self, error: Exception, method: str, url: str, **kwargs):
        logger.error(f"[请求错误] {method} {url} | 错误: {error}")
    
    def before_test(self, test_name: str):
        logger.info(f"[测试前] {test_name}")
    
    def after_test(self, test_name: str, result):
        logger.info(f"[测试后] {test_name} | 结果: {result}")
    
    def on_test_failure(self, test_name: str, error):
        logger.error(f"[测试失败] {test_name} | 错误: {error}")
    
    def on_test_success(self, test_name: str):
        logger.info(f"[测试成功] {test_name}")
