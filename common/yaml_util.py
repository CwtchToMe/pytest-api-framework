"""
YAML 工具类 - 数据加载和管理
"""
import yaml
import os
from typing import Any, Dict, Optional


class YamlUtil:
    """YAML 文件处理工具类"""
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        加载 YAML 文件
        
        Args:
            file_path: YAML 文件路径
            
        Returns:
            Dict: 解析后的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML 文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data if data else {}
    
    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: str):
        """
        保存数据到 YAML 文件
        
        Args:
            data: 数据字典
            file_path: 保存路径
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    @staticmethod
    def get_value(data: Dict[str, Any], key_path: str) -> Optional[Any]:
        """
        获取嵌套的值
        
        Args:
            data: 数据字典
            key_path: 键路径，如 "database.host"
            
        Returns:
            值，如果不存在返回 None
        """
        keys = key_path.split('.')
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return None
        return result


class DataHelper:
    """测试数据加载器 - 实现数据与方法解耦"""
    
    _data_cache: Dict[str, Dict[str, Any]] = {}
    _data_dir: Optional[str] = None
    
    @classmethod
    def get_data_dir(cls) -> str:
        """获取数据目录路径"""
        if cls._data_dir is None:
            cls._data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data'
            )
        return cls._data_dir
    
    @classmethod
    def load_api_data(cls) -> Dict[str, Any]:
        """
        加载 API 测试数据
        
        Returns:
            Dict: API 测试数据
        """
        if 'api' not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), 'api_test_data.yaml')
            cls._data_cache['api'] = YamlUtil.load_yaml(file_path)
        return cls._data_cache['api']
    
    @classmethod
    def load_web_data(cls) -> Dict[str, Any]:
        """
        加载 Web UI 测试数据
        
        Returns:
            Dict: Web UI 测试数据
        """
        if 'web' not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), 'web_test_data.yaml')
            cls._data_cache['web'] = YamlUtil.load_yaml(file_path)
        return cls._data_cache['web']
    
    @classmethod
    def load_framework_data(cls) -> Dict[str, Any]:
        """
        加载框架配置测试数据
        
        Returns:
            Dict: 框架测试数据
        """
        if 'framework' not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), 'framework_test_data.yaml')
            cls._data_cache['framework'] = YamlUtil.load_yaml(file_path)
        return cls._data_cache['framework']
    
    @classmethod
    def load_boundary_data(cls) -> Dict[str, Any]:
        """
        加载边界值测试数据
        
        Returns:
            Dict: 边界值测试数据
        """
        if 'boundary' not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), 'boundary_test_data.yaml')
            cls._data_cache['boundary'] = YamlUtil.load_yaml(file_path)
        return cls._data_cache['boundary']
    
    @classmethod
    def load_invalid_data(cls) -> Dict[str, Any]:
        """
        加载异常测试数据
        
        Returns:
            Dict: 异常测试数据
        """
        if 'invalid' not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), 'invalid_test_data.yaml')
            cls._data_cache['invalid'] = YamlUtil.load_yaml(file_path)
        return cls._data_cache['invalid']
    
    @classmethod
    def get_api_users(cls) -> Dict[str, Any]:
        """获取 API 用户测试数据"""
        data = cls.load_api_data()
        return data.get('users', {})
    
    @classmethod
    def get_api_repositories(cls) -> Dict[str, Any]:
        """获取 API 仓库测试数据"""
        data = cls.load_api_data()
        return data.get('repositories', {})
    
    @classmethod
    def get_api_issues(cls) -> Dict[str, Any]:
        """获取 API Issue 测试数据"""
        data = cls.load_api_data()
        return data.get('issues', {})
    
    @classmethod
    def get_api_search(cls) -> Dict[str, Any]:
        """获取 API 搜索测试数据"""
        data = cls.load_api_data()
        return data.get('search', {})
    
    @classmethod
    def get_web_login_data(cls) -> Dict[str, Any]:
        """获取 Web 登录测试数据"""
        data = cls.load_web_data()
        return data.get('login', {})
    
    @classmethod
    def get_web_home_data(cls) -> Dict[str, Any]:
        """获取 Web 首页测试数据"""
        data = cls.load_web_data()
        return data.get('home', {})
    
    @classmethod
    def get_web_elements(cls, page_name: str) -> Dict[str, Any]:
        """
        获取 Web 页面元素定位
        
        Args:
            page_name: 页面名称 (login_page, home_page 等)
            
        Returns:
            Dict: 元素定位配置
        """
        data = cls.load_web_data()
        return data.get(page_name, {}).get('elements', {})
    
    @classmethod
    def get_circuit_breaker_data(cls) -> Dict[str, Any]:
        """获取熔断器测试数据"""
        data = cls.load_framework_data()
        return data.get('circuit_breaker', {})
    
    @classmethod
    def get_rate_limiter_data(cls) -> Dict[str, Any]:
        """获取限流器测试数据"""
        data = cls.load_framework_data()
        return data.get('rate_limiter', {})
    
    @classmethod
    def get_security_data(cls) -> Dict[str, Any]:
        """获取安全模块测试数据"""
        data = cls.load_framework_data()
        return data.get('security', {})
    
    @classmethod
    def clear_cache(cls):
        """清除数据缓存"""
        cls._data_cache = {}
