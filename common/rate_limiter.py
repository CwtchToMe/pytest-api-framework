"""
请求限流器 - 防止API被限流或封禁

实现令牌桶算法和漏桶算法
"""
import time
import threading
import logging
from typing import Optional, Callable
from functools import wraps


logger = logging.getLogger(__name__)


class RateLimiter:
    """请求限流器 - 令牌桶算法"""
    
    def __init__(self, max_calls: int, period: float):
        """
        初始化限流器
        
        Args:
            max_calls: 最大调用次数
            period: 时间周期（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self._lock = threading.Lock()
        logger.info(f"限流器初始化: {max_calls}次/{period}秒")
    
    def __call__(self, func: Callable):
        """
        装饰器：限流函数调用
        
        Args:
            func: 要限流的函数
            
        Returns:
            包装后的函数
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                now = time.time()
                # 清理过期的调用记录
                self.calls = [t for t in self.calls if now - t < self.period]
                
                if len(self.calls) >= self.max_calls:
                    # 计算需要等待的时间
                    oldest_call = self.calls[0]
                    wait_time = self.period - (now - oldest_call)
                    logger.warning(f"达到限流阈值，等待 {wait_time:.2f} 秒")
                    time.sleep(wait_time)
                    self.calls = []
                
                self.calls.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def acquire(self) -> bool:
        """
        尝试获取令牌
        
        Returns:
            bool: 是否成功获取令牌
        """
        with self._lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < self.period]
            
            if len(self.calls) >= self.max_calls:
                return False
            
            self.calls.append(now)
            return True
    
    def wait(self):
        """等待直到可以获取令牌"""
        while not self.acquire():
            oldest_call = self.calls[0]
            wait_time = self.period - (time.time() - oldest_call)
            if wait_time > 0:
                time.sleep(wait_time)


class TokenBucket:
    """令牌桶算法"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量（最大令牌数）
            refill_rate: 令牌补充速率（令牌/秒）
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()
        logger.info(f"令牌桶初始化: 容量={capacity}, 补充速率={refill_rate}/秒")
    
    def _refill(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 需要消费的令牌数
            
        Returns:
            bool: 是否成功消费
        """
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def wait_for_token(self, tokens: int = 1):
        """等待直到有足够的令牌"""
        while not self.consume(tokens):
            # 计算需要等待的时间
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            time.sleep(wait_time)


class LeakyBucket:
    """漏桶算法"""
    
    def __init__(self, capacity: int, leak_rate: float):
        """
        初始化漏桶
        
        Args:
            capacity: 桶容量
            leak_rate: 漏水速率（请求/秒）
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water_level = 0
        self.last_leak = time.time()
        self._lock = threading.Lock()
        logger.info(f"漏桶初始化: 容量={capacity}, 漏水速率={leak_rate}/秒")
    
    def _leak(self):
        """漏水"""
        now = time.time()
        elapsed = now - self.last_leak
        leaked = elapsed * self.leak_rate
        
        self.water_level = max(0, self.water_level - leaked)
        self.last_leak = now
    
    def add(self, amount: int = 1) -> bool:
        """
        向桶中添加水（请求）
        
        Args:
            amount: 添加的水量
            
        Returns:
            bool: 是否成功添加
        """
        with self._lock:
            self._leak()
            
            if self.water_level + amount <= self.capacity:
                self.water_level += amount
                return True
            
            return False
    
    def wait_for_space(self, amount: int = 1):
        """等待直到有足够的空间"""
        while not self.add(amount):
            # 计算需要等待的时间
            space_needed = amount - (self.capacity - self.water_level)
            wait_time = space_needed / self.leak_rate
            time.sleep(wait_time)


# 全局限流器实例
_global_rate_limiter: Optional[RateLimiter] = None
_global_token_bucket: Optional[TokenBucket] = None
_global_leaky_bucket: Optional[LeakyBucket] = None


def get_rate_limiter(max_calls: int = 10, period: float = 1.0) -> RateLimiter:
    """
    获取全局限流器实例
    
    Args:
        max_calls: 最大调用次数
        period: 时间周期
        
    Returns:
        RateLimiter: 限流器实例
    """
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(max_calls, period)
    return _global_rate_limiter


def get_token_bucket(capacity: int = 10, refill_rate: float = 1.0) -> TokenBucket:
    """
    获取全局令牌桶实例
    
    Args:
        capacity: 桶容量
        refill_rate: 补充速率
        
    Returns:
        TokenBucket: 令牌桶实例
    """
    global _global_token_bucket
    if _global_token_bucket is None:
        _global_token_bucket = TokenBucket(capacity, refill_rate)
    return _global_token_bucket


def get_leaky_bucket(capacity: int = 10, leak_rate: float = 1.0) -> LeakyBucket:
    """
    获取全局漏桶实例
    
    Args:
        capacity: 桶容量
        leak_rate: 漏水速率
        
    Returns:
        LeakyBucket: 漏桶实例
    """
    global _global_leaky_bucket
    if _global_leaky_bucket is None:
        _global_leaky_bucket = LeakyBucket(capacity, leak_rate)
    return _global_leaky_bucket