"""
插件系统 - "硬逻辑 + 软钩子" 组合模式

核心插件：强制加载，不可禁用
普通插件：可选加载，可禁用
"""
from .base import Plugin, CorePlugin, PluginType, PluginState, PluginInfo
from .manager import PluginManager

from .core.circuit_breaker import CircuitBreakerPlugin
from .core.rate_limiter import RateLimiterPlugin
from .normal.logging_plugin import LoggingPlugin
from .normal.metrics_plugin import MetricsPlugin
from .normal.cache_plugin import CachePlugin


__all__ = [
    'Plugin',
    'CorePlugin',
    'PluginType',
    'PluginState',
    'PluginInfo',
    'PluginManager',
    'CircuitBreakerPlugin',
    'RateLimiterPlugin',
    'LoggingPlugin',
    'MetricsPlugin',
    'CachePlugin',
    'get_plugin_manager',
    'register_plugin',
]


_global_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """
    获取全局插件管理器实例
    
    自动加载：
    1. 核心插件（强制加载）：熔断器、限流器
    2. 普通插件（可选）：日志、指标、缓存
    
    Returns:
        PluginManager: 插件管理器实例
    """
    global _global_plugin_manager
    if _global_plugin_manager is None:
        _global_plugin_manager = PluginManager()
        
        _global_plugin_manager.register(
            CircuitBreakerPlugin(failure_threshold=5, timeout=60),
            force=True
        )
        _global_plugin_manager.register(
            RateLimiterPlugin(max_calls=100, period=60),
            force=True
        )
        
        _global_plugin_manager.register(LoggingPlugin())
        _global_plugin_manager.register(MetricsPlugin())
        _global_plugin_manager.register(CachePlugin())
        
        for plugin_name in _global_plugin_manager.plugins.keys():
            _global_plugin_manager.enable(plugin_name)
    
    return _global_plugin_manager


def register_plugin(plugin: Plugin):
    """
    便捷函数：注册插件
    
    Args:
        plugin: 插件实例
    """
    manager = get_plugin_manager()
    manager.register(plugin)
