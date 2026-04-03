"""
插件系统 - 基类和类型定义

"硬逻辑 + 软钩子" 组合模式：
- 核心插件：强制加载，不可禁用
- 普通插件：可选加载，可禁用
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any


logger = logging.getLogger(__name__)


class PluginState(Enum):
    """插件状态"""
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class PluginType(Enum):
    """插件类型"""
    CORE = "core"        # 核心插件：不可禁用
    NORMAL = "normal"    # 普通插件：可禁用


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    state: PluginState = PluginState.LOADED
    
    @property
    def is_core(self) -> bool:
        """是否为核心插件"""
        return self.plugin_type == PluginType.CORE
    
    @property
    def can_disable(self) -> bool:
        """是否可以禁用"""
        return self.plugin_type == PluginType.NORMAL


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
    
    @property
    def plugin_type(self) -> PluginType:
        """插件类型，默认为普通插件"""
        return PluginType.NORMAL
    
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
    
    def before_request(self, method: str, url: str, **kwargs) -> Optional[Any]:
        """
        请求前钩子
        
        Returns:
            Optional[Any]: 如果返回非 None，则直接返回该结果，跳过实际请求
        """
        pass
    
    def after_request(self, response, method: str, url: str, **kwargs):
        """请求后钩子"""
        pass
    
    def on_request_error(self, error: Exception, method: str, url: str, **kwargs):
        """请求错误钩子"""
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


class CorePlugin(Plugin):
    """
    核心插件基类 - 核心功能插件必须继承此类
    
    核心插件特点：
    1. 强制加载，不可禁用
    2. 优先级高于普通插件
    3. 在请求链中处于关键位置
    """
    
    @property
    def plugin_type(self) -> PluginType:
        """核心插件类型"""
        return PluginType.CORE
    
    def on_disable(self):
        """核心插件不允许禁用"""
        logger.warning(f"核心插件 '{self.name}' 不允许禁用")
