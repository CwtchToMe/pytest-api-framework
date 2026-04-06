"""
Mock 工具类 - 支持通过环境变量控制 Mock 模式

使用方式：
1. Mock 模式（默认）：USE_MOCK=true 或不设置
2. 真实 API 模式：USE_MOCK=false

示例：
    from common.mock_util import MockHelper
    
    # 在测试中使用
    def test_get_user(github_client):
        helper = MockHelper()
        
        if helper.use_mock:
            # Mock 模式
            mock_response = helper.create_mock_response(200, user_data)
            with helper.mock_request(github_client, 'get', mock_response):
                user = github_client.get_user("testuser")
        else:
            # 真实 API 模式
            user = github_client.get_user("testuser")
        
        # 验证（两种模式共用）
        assert user["login"] == "testuser"
"""
from unittest.mock import Mock, patch
from typing import Any, Dict, Optional
from contextlib import contextmanager
from config.config import config


class MockHelper:
    """
    Mock 辅助类 - 简化 Mock 和真实 API 切换
    
    属性：
        use_mock: 是否使用 Mock 模式（从配置读取）
    """
    
    def __init__(self):
        self.use_mock = config.USE_MOCK
    
    def create_mock_response(self, status_code: int = 200, 
                             json_data: Optional[Dict] = None,
                             text: str = "",
                             headers: Optional[Dict] = None) -> Mock:
        """
        创建 Mock 响应对象
        
        Args:
            status_code: HTTP 状态码
            json_data: JSON 响应数据
            text: 文本响应
            headers: 响应头
            
        Returns:
            Mock: Mock 响应对象
        """
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = text
        mock_response.headers = headers or {}
        mock_response.ok = 200 <= status_code < 300
        return mock_response
    
    @contextmanager
    def mock_request(self, client: Any, method: str, mock_response: Mock):
        """
        Mock 请求上下文管理器
        
        Args:
            client: API 客户端
            method: HTTP 方法 ('get', 'post', 'put', 'delete')
            mock_response: Mock 响应对象
            
        Yields:
            None
        """
        if not self.use_mock:
            yield
            return
        
        requests_obj = getattr(client, 'requests', client)
        with patch.object(requests_obj, method, return_value=mock_response):
            yield
    
    def should_mock(self) -> bool:
        """返回是否应该使用 Mock"""
        return self.use_mock
    
    def get_mode_description(self) -> str:
        """获取当前模式描述"""
        return "Mock 模式" if self.use_mock else "真实 API 模式"


def create_mock_response(status_code: int = 200, 
                         json_data: Optional[Dict] = None) -> Mock:
    """
    快捷函数：创建 Mock 响应
    
    Args:
        status_code: HTTP 状态码
        json_data: JSON 响应数据
        
    Returns:
        Mock: Mock 响应对象
    """
    helper = MockHelper()
    return helper.create_mock_response(status_code, json_data)


def is_mock_mode() -> bool:
    """
    快捷函数：检查是否为 Mock 模式
    
    Returns:
        bool: 是否使用 Mock
    """
    return config.USE_MOCK
