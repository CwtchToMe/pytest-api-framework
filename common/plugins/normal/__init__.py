"""
普通插件 - 可禁用
"""

from .allure_plugin import AllurePlugin
from .logging_plugin import LoggingPlugin

__all__ = ["LoggingPlugin", "AllurePlugin"]
