"""
YAML 工具类 - 数据加载和管理
"""

import os
from typing import Any, Dict, Optional

import yaml


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

        with open(file_path, "r", encoding="utf-8") as f:
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
        with open(file_path, "w", encoding="utf-8") as f:
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
        keys = key_path.split(".")
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return None
        return result


class DataHelper:
    """测试数据加载器 - 实现数据与方法解耦

    提供按业务模块划分的数据访问方法，自动缓存减少文件 I/O。
    数据来源：
    - api_test_data.yaml（API 层测试数据）
    - web_test_data.yaml（UI 层测试数据）
    """

    _data_cache: Dict[str, Dict[str, Any]] = {}
    _data_dir: Optional[str] = None

    @classmethod
    def get_data_dir(cls) -> str:
        """获取数据目录路径"""
        if cls._data_dir is None:
            cls._data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data"
            )
        return cls._data_dir

    @classmethod
    def load_api_data(cls) -> Dict[str, Any]:
        """
        加载 API 测试数据

        Returns:
            Dict: API 测试数据
        """
        if "api" not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), "api_test_data.yaml")
            cls._data_cache["api"] = YamlUtil.load_yaml(file_path)
        return cls._data_cache["api"]

    @classmethod
    def load_web_data(cls) -> Dict[str, Any]:
        """
        加载 Web UI 测试数据

        Returns:
            Dict: Web UI 测试数据
        """
        if "web" not in cls._data_cache:
            file_path = os.path.join(cls.get_data_dir(), "web_test_data.yaml")
            cls._data_cache["web"] = YamlUtil.load_yaml(file_path)
        return cls._data_cache["web"]

    # ============================================================
    # API 测试数据业务方法
    # ============================================================

    @classmethod
    def get_auth_data(cls) -> Dict[str, Any]:
        """获取认证模块测试数据（auth）"""
        return cls.load_api_data().get("auth", {})

    @classmethod
    def get_merchant_data(cls) -> Dict[str, Any]:
        """获取商家模块测试数据（merchant）"""
        return cls.load_api_data().get("merchant", {})

    @classmethod
    def get_product_data(cls) -> Dict[str, Any]:
        """获取商品模块测试数据（product）"""
        return cls.load_api_data().get("product", {})

    @classmethod
    def get_cart_data(cls) -> Dict[str, Any]:
        """获取购物车模块测试数据（cart）"""
        return cls.load_api_data().get("cart", {})

    @classmethod
    def get_order_data(cls) -> Dict[str, Any]:
        """获取订单模块测试数据（order）"""
        return cls.load_api_data().get("order", {})

    @classmethod
    def get_review_data(cls) -> Dict[str, Any]:
        """获取评价模块测试数据（review）"""
        return cls.load_api_data().get("review", {})

    @classmethod
    def get_boundary_data(cls) -> Dict[str, Any]:
        """获取边界值测试数据（boundary）"""
        return cls.load_api_data().get("boundary", {})

    @classmethod
    def get_security_data(cls) -> Dict[str, Any]:
        """获取安全测试数据（security）"""
        return cls.load_api_data().get("security", {})

    # ============================================================
    # Web 测试数据业务方法
    # ============================================================

    @classmethod
    def get_h5_web_data(cls) -> Dict[str, Any]:
        """获取 H5 端 UI 测试数据（h5）"""
        return cls.load_web_data().get("h5", {})

    @classmethod
    def get_merchant_web_data(cls) -> Dict[str, Any]:
        """获取商家端 UI 测试数据（merchant_web）"""
        return cls.load_web_data().get("merchant_web", {})

    @classmethod
    def get_admin_web_data(cls) -> Dict[str, Any]:
        """获取管理后台 UI 测试数据（admin_web）"""
        return cls.load_web_data().get("admin_web", {})

    @classmethod
    def clear_cache(cls):
        """清除数据缓存"""
        cls._data_cache = {}
