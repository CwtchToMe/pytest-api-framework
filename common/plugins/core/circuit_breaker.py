"""
核心插件 - 熔断器插件

功能：
1. 保护系统稳定性，防止级联故障
2. 达到失败阈值后熔断
3. 超时后尝试恢复
"""
import logging
from typing import Optional, Any

from ..base import CorePlugin


logger = logging.getLogger(__name__)


class CircuitBreakerPlugin(CorePlugin):
    """
    熔断器插件 - 核心插件
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        name: str = "api_requests"
    ):
        from common.circuit_breaker import CircuitBreaker, CircuitState
        self._breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            timeout=timeout,
            name=name
        )
        self.CircuitState = CircuitState
    
    @property
    def name(self) -> str:
        return "circuit_breaker"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "熔断器 - 保护系统稳定性，防止级联故障"
    
    @property
    def author(self) -> str:
        return "System"
    
    def before_request(self, method: str, url: str, **kwargs) -> Optional[Any]:
        """请求前检查熔断器状态"""
        state = self._breaker.get_state()
        if state == self.CircuitState.OPEN:
            if not self._breaker._should_attempt_reset():
                from common.circuit_breaker import CircuitBreakerError
                raise CircuitBreakerError(
                    f"熔断器 '{self._breaker.name}' 处于开启状态，拒绝请求: {method} {url}"
                )
        return None
    
    def after_request(self, response, method: str, url: str, **kwargs):
        """请求成功，记录成功"""
        if hasattr(response, 'status_code') and response.status_code < 500:
            self._breaker._record_success()
    
    def on_request_error(self, error: Exception, method: str, url: str, **kwargs):
        """请求失败，记录失败"""
        self._breaker._record_failure()
    
    def get_state(self):
        """获取熔断器状态"""
        return self._breaker.get_state()
    
    def get_failures(self) -> int:
        """获取失败次数"""
        return self._breaker.get_failures()
    
    def reset(self):
        """重置熔断器"""
        self._breaker.reset()
