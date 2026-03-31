"""
插件系统 - 支持功能扩展而不修改核心代码

提供插件注册、生命周期管理和钩子执行机制
"""
import logging
from typing import Dict, List, Callable, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class PluginState(Enum):
    """插件状态"""
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    state: PluginState = PluginState.LOADED


class Plugin(ABC):
    """插件基类 - 所有插件必须继承此类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    def description(self) -> str:
        """插件描述"""
        return ""
    
    @property
    def author(self) -> str:
        """插件作者"""
        return ""
    
    def on_load(self):
        """插件加载时调用"""
        logger.info(f"插件 '{self.name}' 加载")
    
    def on_enable(self):
        """插件启用时调用"""
        logger.info(f"插件 '{self.name}' 启用")
    
    def on_disable(self):
        """插件禁用时调用"""
        logger.info(f"插件 '{self.name}' 禁用")
    
    def on_unload(self):
        """插件卸载时调用"""
        logger.info(f"插件 '{self.name}' 卸载")
    
    def before_request(self, method: str, url: str, **kwargs):
        """请求前钩子"""
        pass
    
    def after_request(self, response, method: str, url: str, **kwargs):
        """请求后钩子"""
        pass
    
    def before_test(self, test_name: str):
        """测试前钩子"""
        pass
    
    def after_test(self, test_name: str, result):
        """测试后钩子"""
        pass
    
    def on_test_failure(self, test_name: str, error):
        """测试失败钩子"""
        pass
    
    def on_test_success(self, test_name: str):
        """测试成功钩子"""
        pass


class PluginManager:
    """插件管理器 - 管理所有插件的生命周期"""
    
    def __init__(self):
        """初始化插件管理器"""
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[Callable]] = {
            'before_request': [],
            'after_request': [],
            'before_test': [],
            'after_test': [],
            'on_test_failure': [],
            'on_test_success': []
        }
        logger.info("插件管理器初始化成功")
    
    def register(self, plugin: Plugin):
        """
        注册插件
        
        Args:
            plugin: 插件实例
        """
        if plugin.name in self.plugins:
            logger.warning(f"插件 '{plugin.name}' 已存在，将被覆盖")
        
        self.plugins[plugin.name] = plugin
        self.plugin_info[plugin.name] = PluginInfo(
            name=plugin.name,
            version=plugin.version,
            description=plugin.description,
            author=plugin.author
        )
        
        # 调用插件加载钩子
        try:
            plugin.on_load()
            logger.info(f"插件 '{plugin.name}' 注册成功")
        except Exception as e:
            logger.error(f"插件 '{plugin.name}' 加载失败: {e}")
            self.plugin_info[plugin.name].state = PluginState.ERROR
            raise
    
    def unregister(self, name: str):
        """
        注销插件
        
        Args:
            name: 插件名称
        """
        if name not in self.plugins:
            logger.warning(f"插件 '{name}' 不存在")
            return
        
        plugin = self.plugins[name]
        
        try:
            plugin.on_unload()
        except Exception as e:
            logger.error(f"插件 '{name}' 卸载失败: {e}")
        
        del self.plugins[name]
        del self.plugin_info[name]
        
        # 移除钩子
        for hook_list in self.hooks.values():
            hook_list[:] = [h for h in hook_list if h.__self__ is not plugin]
        
        logger.info(f"插件 '{name}' 已注销")
    
    def enable(self, name: str):
        """
        启用插件
        
        Args:
            name: 插件名称
        """
        if name not in self.plugins:
            raise ValueError(f"插件 '{name}' 不存在")
        
        plugin = self.plugins[name]
        plugin.on_enable()
        self.plugin_info[name].state = PluginState.ENABLED
        logger.info(f"插件 '{name}' 已启用")
    
    def disable(self, name: str):
        """
        禁用插件
        
        Args:
            name: 插件名称
        """
        if name not in self.plugins:
            raise ValueError(f"插件 '{name}' 不存在")
        
        plugin = self.plugins[name]
        plugin.on_disable()
        self.plugin_info[name].state = PluginState.DISABLED
        logger.info(f"插件 '{name}' 已禁用")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        获取插件实例
        
        Args:
            name: 插件名称
            
        Returns:
            Plugin: 插件实例，如果不存在则返回 None
        """
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """
        获取所有插件信息
        
        Returns:
            list: 插件信息列表
        """
        return list(self.plugin_info.values())
    
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """
        执行钩子
        
        Args:
            hook_name: 钩子名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if hook_name not in self.hooks:
            logger.warning(f"钩子 '{hook_name}' 不存在")
            return
        
        for hook_func in self.hooks[hook_name]:
            try:
                hook_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"执行钩子 '{hook_name}' 失败: {e}")
    
    def _register_hooks(self, plugin: Plugin):
        """注册插件的所有钩子"""
        hook_methods = {
            'before_request': plugin.before_request,
            'after_request': plugin.after_request,
            'before_test': plugin.before_test,
            'after_test': plugin.after_test,
            'on_test_failure': plugin.on_test_failure,
            'on_test_success': plugin.on_test_success
        }
        
        for hook_name, method in hook_methods.items():
            if hasattr(method, '__func__'):
                self.hooks[hook_name].append(method)


# 内置插件示例

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
    
    def before_request(self, method: str, url: str, **kwargs):
        logger.info(f"[请求前] {method} {url}")
    
    def after_request(self, response, method: str, url: str, **kwargs):
        logger.info(f"[请求后] {method} {url} | 状态: {getattr(response, 'status_code', 'N/A')}")
    
    def before_test(self, test_name: str):
        logger.info(f"[测试前] {test_name}")
    
    def after_test(self, test_name: str, result):
        logger.info(f"[测试后] {test_name} | 结果: {result}")
    
    def on_test_failure(self, test_name: str, error):
        logger.error(f"[测试失败] {test_name} | 错误: {error}")
    
    def on_test_success(self, test_name: str):
        logger.info(f"[测试成功] {test_name}")


class MetricsPlugin(Plugin):
    """指标插件 - 收集性能指标"""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'request_time_total': 0,
            'test_count': 0,
            'test_passed': 0,
            'test_failed': 0
        }
    
    @property
    def name(self) -> str:
        return "metrics"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "收集性能和测试指标"
    
    @property
    def author(self) -> str:
        return "System"
    
    def before_request(self, method: str, url: str, **kwargs):
        self.metrics['request_count'] += 1
    
    def after_request(self, response, method: str, url: str, **kwargs):
        # 可以记录响应时间等指标
        pass
    
    def before_test(self, test_name: str):
        self.metrics['test_count'] += 1
    
    def on_test_success(self, test_name: str):
        self.metrics['test_passed'] += 1
    
    def on_test_failure(self, test_name: str, error):
        self.metrics['test_failed'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return self.metrics.copy()


class CachePlugin(Plugin):
    """缓存插件 - 缓存GET请求"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5分钟
    
    @property
    def name(self) -> str:
        return "cache"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "缓存GET请求"
    
    @property
    def author(self) -> str:
        return "System"
    
    def before_request(self, method: str, url: str, **kwargs):
        if method.upper() == 'GET':
            cache_key = f"{url}_{str(kwargs)}"
            if cache_key in self.cache:
                logger.debug(f"缓存命中: {url}")
                return self.cache[cache_key]
    
    def after_request(self, response, method: str, url: str, **kwargs):
        if method.upper() == 'GET' and hasattr(response, 'status_code') and response.status_code == 200:
            cache_key = f"{url}_{str(kwargs)}"
            self.cache[cache_key] = response
            logger.debug(f"已缓存: {url}")
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")


# 全局插件管理器实例
_global_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """
    获取全局插件管理器实例
    
    Returns:
        PluginManager: 插件管理器实例
    """
    global _global_plugin_manager
    if _global_plugin_manager is None:
        _global_plugin_manager = PluginManager()
        
        # 自动注册内置插件
        _global_plugin_manager.register(LoggingPlugin())
        _global_plugin_manager.register(MetricsPlugin())
        _global_plugin_manager.register(CachePlugin())
        
        # 启用所有插件
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