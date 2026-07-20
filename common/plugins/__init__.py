"""
插件系统 - 基于钩子模式的扩展机制

插件可以挂载到 HTTP 请求和测试生命周期中，实现日志、Allure 附件等横切关注点。
"""

from .base import Plugin, PluginInfo, PluginState, PluginType
from .manager import PluginManager
from .normal.allure_plugin import AllurePlugin
from .normal.logging_plugin import LoggingPlugin

__all__ = [
    "Plugin",
    "PluginType",
    "PluginState",
    "PluginInfo",
    "PluginManager",
    "LoggingPlugin",
    "AllurePlugin",
    "get_plugin_manager",
]


_global_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """
    获取全局插件管理器实例

    自动加载：
    - LoggingPlugin：记录请求/测试日志
    - AllurePlugin：将 HTTP 请求/响应附加到 Allure 报告

    Returns:
        PluginManager: 插件管理器实例
    """
    global _global_plugin_manager
    if _global_plugin_manager is None:
        _global_plugin_manager = PluginManager()

        _global_plugin_manager.register(LoggingPlugin())
        _global_plugin_manager.register(AllurePlugin())

        for plugin_name in _global_plugin_manager.plugins.keys():
            _global_plugin_manager.enable(plugin_name)

    return _global_plugin_manager
