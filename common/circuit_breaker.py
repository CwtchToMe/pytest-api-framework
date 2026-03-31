"""
熔断器模式实现 - 提高系统稳定性

当服务出现故障时，熔断器会快速失败，避免级联故障
"""
import time
import threading
import logging
from typing import Callable, Optional, Any
from functools import wraps
from enum import Enum


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 关闭状态：正常工作
    OPEN = "open"          # 开启状态：熔断中
    HALF_OPEN = "half_open"  # 半开状态：尝试恢复


class CircuitBreakerError(Exception):
    """熔断器异常"""
    pass


class CircuitBreaker:
    """熔断器 - 实现熔断器模式"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: Exception = Exception,
        name: str = "default"
    ):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值，达到此值后熔断
            timeout: 熔断超时时间（秒）
            expected_exception: 预期的异常类型
            name: 熔断器名称
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
        self._lock = threading.Lock()
        
        logger.info(f"熔断器 '{name}' 初始化成功 (阈值: {failure_threshold}, 超时: {timeout}s)")
    
    def _should_attempt_reset(self) -> bool:
        """判断是否应该尝试重置熔断器"""
        if self.last_failure_time is None:
            return False
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout
    
    def _record_success(self):
        """记录成功"""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                logger.info(f"熔断器 '{self.name}' 已恢复到关闭状态")
            elif self.state == CircuitState.CLOSED:
                self.failures = 0
    
    def _record_failure(self):
        """记录失败"""
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"熔断器 '{self.name}' 已开启 (失败次数: {self.failures})")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        调用函数，带熔断保护
        
        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数返回值
            
        Raises:
            CircuitBreakerError: 当熔断器开启时抛出
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"熔断器 '{self.name}' 进入半开状态，尝试恢复")
                else:
                    error_msg = f"熔断器 '{self.name}' 处于开启状态，拒绝调用"
                    logger.error(error_msg)
                    raise CircuitBreakerError(error_msg)
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.expected_exception as e:
            self._record_failure()
            logger.error(f"函数调用失败: {e}")
            raise
        except Exception as e:
            # 非预期异常，不计数
            logger.error(f"函数调用发生未预期异常: {e}")
            raise
    
    def get_state(self) -> CircuitState:
        """获取当前状态"""
        with self._lock:
            return self.state
    
    def get_failures(self) -> int:
        """获取失败次数"""
        with self._lock:
            return self.failures
    
    def reset(self):
        """手动重置熔断器"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.last_failure_time = None
            logger.info(f"熔断器 '{self.name}' 已手动重置")


def circuit_breaker(
    failure_threshold: int = 5,
    timeout: int = 60,
    expected_exception: Exception = Exception,
    name: str = "default"
):
    """
    熔断器装饰器
    
    Args:
        failure_threshold: 失败阈值
        timeout: 熔断超时时间（秒）
        expected_exception: 预期的异常类型
        name: 熔断器名称
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        breaker = CircuitBreaker(failure_threshold, timeout, expected_exception, name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        wrapper.breaker = breaker
        return wrapper
    
    return decorator


class CircuitBreakerManager:
    """熔断器管理器 - 管理多个熔断器"""
    
    def __init__(self):
        """初始化熔断器管理器"""
        self.circuit_breakers = {}
        self._lock = threading.Lock()
        logger.info("熔断器管理器初始化成功")
    
    def register(self, name: str, circuit_breaker: CircuitBreaker):
        """
        注册熔断器
        
        Args:
            name: 熔断器名称
            circuit_breaker: 熔断器实例
        """
        with self._lock:
            self.circuit_breakers[name] = circuit_breaker
            logger.info(f"已注册熔断器: {name}")
    
    def get(self, name: str, **kwargs) -> CircuitBreaker:
        """
        获取或创建熔断器
        
        Args:
            name: 熔断器名称
            **kwargs: 熔断器参数
            
        Returns:
            CircuitBreaker: 熔断器实例
        """
        with self._lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(name=name, **kwargs)
            return self.circuit_breakers[name]
    
    def call(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """
        使用指定熔断器调用函数
        
        Args:
            name: 熔断器名称
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数返回值
        """
        breaker = self.get(name)
        return breaker.call(func, *args, **kwargs)
    
    def get_all_states(self) -> dict:
        """
        获取所有熔断器的状态
        
        Returns:
            dict: 熔断器状态字典
        """
        with self._lock:
            return {
                name: {
                    'state': breaker.get_state().value,
                    'failures': breaker.get_failures()
                }
                for name, breaker in self.circuit_breakers.items()
            }
    
    def reset_all(self):
        """重置所有熔断器"""
        with self._lock:
            for breaker in self.circuit_breakers.values():
                breaker.reset()
        logger.info("所有熔断器已重置")


# 全局熔断器管理器实例
_global_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """
    获取全局熔断器管理器实例
    
    Returns:
        CircuitBreakerManager: 熔断器管理器实例
    """
    global _global_circuit_breaker_manager
    if _global_circuit_breaker_manager is None:
        _global_circuit_breaker_manager = CircuitBreakerManager()
    return _global_circuit_breaker_manager


class RetryWithCircuitBreaker:
    """带熔断器的重试机制"""
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        """
        初始化带熔断器的重试机制
        
        Args:
            max_retries: 最大重试次数
            backoff_factor: 退避因子
            circuit_breaker: 熔断器实例
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.circuit_breaker = circuit_breaker
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        调用函数，带重试和熔断保护
        
        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数返回值
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if self.circuit_breaker:
                    return self.circuit_breaker.call(func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except CircuitBreakerError:
                # 熔断器异常，不重试
                raise
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    logger.warning(f"第 {attempt + 1} 次尝试失败，{wait_time}s 后重试: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"所有重试均失败: {e}")
                    raise
        
        if last_exception:
            raise last_exception