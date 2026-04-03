"""
插件管理器 - 管理所有插件的生命周期

特性：
1. 区分核心插件和普通插件
2. 核心插件强制加载，不可禁用
3. 普通插件可自由启用/禁用
4. 统一的钩子执行机制
"""
import logging
from typing import Dict, List, Callable, Any, Optional

from .base import Plugin, PluginInfo, PluginType, PluginState


logger = logging.getLogger(__name__)


class PluginManager:
    """
    插件管理器 - 管理所有插件的生命周期
    """
    
    def __init__(self):
        """初始化插件管理器"""
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[Callable]] = {
            'before_request': [],
            'after_request': [],
            'on_request_error': [],
            'before_test': [],
            'after_test': [],
            'on_test_failure': [],
            'on_test_success': []
        }
        logger.info("插件管理器初始化成功")
    
    def register(self, plugin: Plugin, force: bool = False):
        """
        注册插件
        
        Args:
            plugin: 插件实例
            force: 是否强制注册（覆盖已存在的插件）
        """
        if plugin.name in self.plugins and not force:
            logger.warning(f"插件 '{plugin.name}' 已存在，跳过注册")
            return
        
        self.plugins[plugin.name] = plugin
        self.plugin_info[plugin.name] = PluginInfo(
            name=plugin.name,
            version=plugin.version,
            description=plugin.description,
            author=plugin.author,
            plugin_type=plugin.plugin_type
        )
        
        try:
            plugin.on_load()
            self._register_hooks(plugin)
            logger.info(f"插件 '{plugin.name}' 注册成功 (类型: {plugin.plugin_type.value})")
        except Exception as e:
            logger.error(f"插件 '{plugin.name}' 加载失败: {e}")
            self.plugin_info[plugin.name].state = PluginState.ERROR
            raise
    
    def unregister(self, name: str) -> bool:
        """
        注销插件
        
        Args:
            name: 插件名称
            
        Returns:
            bool: 是否成功注销
        """
        if name not in self.plugins:
            logger.warning(f"插件 '{name}' 不存在")
            return False
        
        plugin = self.plugins[name]
        
        if plugin.plugin_type == PluginType.CORE:
            logger.warning(f"核心插件 '{name}' 不允许注销")
            return False
        
        try:
            plugin.on_unload()
        except Exception as e:
            logger.error(f"插件 '{name}' 卸载失败: {e}")
        
        del self.plugins[name]
        del self.plugin_info[name]
        
        for hook_list in self.hooks.values():
            hook_list[:] = [h for h in hook_list if h.__self__ is not plugin]
        
        logger.info(f"插件 '{name}' 已注销")
        return True
    
    def enable(self, name: str) -> bool:
        """
        启用插件
        
        Args:
            name: 插件名称
            
        Returns:
            bool: 是否成功启用
        """
        if name not in self.plugins:
            raise ValueError(f"插件 '{name}' 不存在")
        
        plugin = self.plugins[name]
        plugin.on_enable()
        self.plugin_info[name].state = PluginState.ENABLED
        logger.info(f"插件 '{name}' 已启用")
        return True
    
    def disable(self, name: str) -> bool:
        """
        禁用插件
        
        Args:
            name: 插件名称
            
        Returns:
            bool: 是否成功禁用
        """
        if name not in self.plugins:
            raise ValueError(f"插件 '{name}' 不存在")
        
        plugin = self.plugins[name]
        
        if plugin.plugin_type == PluginType.CORE:
            logger.warning(f"核心插件 '{name}' 不允许禁用")
            return False
        
        plugin.on_disable()
        self.plugin_info[name].state = PluginState.DISABLED
        logger.info(f"插件 '{name}' 已禁用")
        return True
    
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
    
    def get_core_plugins(self) -> List[PluginInfo]:
        """
        获取核心插件列表
        
        Returns:
            list: 核心插件信息列表
        """
        return [info for info in self.plugin_info.values() if info.is_core]
    
    def get_normal_plugins(self) -> List[PluginInfo]:
        """
        获取普通插件列表
        
        Returns:
            list: 普通插件信息列表
        """
        return [info for info in self.plugin_info.values() if not info.is_core]
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        执行钩子，收集所有返回值
        
        Args:
            hook_name: 钩子名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            List[Any]: 所有钩子的返回值列表
        """
        if hook_name not in self.hooks:
            logger.warning(f"钩子 '{hook_name}' 不存在")
            return []
        
        results = []
        for hook_func in self.hooks[hook_name]:
            try:
                result = hook_func(*args, **kwargs)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.error(f"执行钩子 '{hook_name}' 失败: {e}")
        
        return results
    
    def _register_hooks(self, plugin: Plugin):
        """注册插件的所有钩子"""
        hook_methods = {
            'before_request': plugin.before_request,
            'after_request': plugin.after_request,
            'on_request_error': plugin.on_request_error,
            'before_test': plugin.before_test,
            'after_test': plugin.after_test,
            'on_test_failure': plugin.on_test_failure,
            'on_test_success': plugin.on_test_success
        }
        
        for hook_name, method in hook_methods.items():
            self.hooks[hook_name].append(method)
