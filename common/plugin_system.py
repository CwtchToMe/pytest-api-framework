"""
插件系统 - 入口模块

"硬逻辑 + 软钩子" 组合模式：
- 核心插件：强制加载，不可禁用
- 普通插件：可选加载，可禁用

详细文档请参考：docs/插件系统指南.md
"""
from common.plugins import (
    Plugin,
    CorePlugin,
    PluginType,
    PluginState,
    PluginInfo,
    PluginManager,
    CircuitBreakerPlugin,
    RateLimiterPlugin,
    LoggingPlugin,
    MetricsPlugin,
    CachePlugin,
    get_plugin_manager,
    register_plugin,
)


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
