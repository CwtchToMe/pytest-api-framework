"""
跨用例共用 Helper - 登录获取 Token 等公共逻辑

功能：
1. 统一登录流程（支持 Mock 模式和真实 API 模式）
2. 获取测试用户 Token
3. 多角色 Token 管理
"""

import logging
from typing import Dict, Optional

from api.takeout_api import AuthApi, is_success
from config.config import config

logger = logging.getLogger(__name__)


def login_and_get_token(phone: str, code: str = None) -> Optional[str]:
    """
    登录并获取 accessToken

    Mock 模式：直接返回模拟 token，不发起真实请求。
    真实模式：使用给定手机号和验证码登录，返回 accessToken。

    Args:
        phone: 手机号
        code: 验证码（默认使用 TEST_SMS_CODE）

    Returns:
        Optional[str]: accessToken，登录失败返回 None
    """
    from common.mock_util import is_mock_mode

    if is_mock_mode():
        return f"mock-token-{phone}"

    code = code or config.TEST_SMS_CODE
    auth_api = AuthApi()

    # 直接登录（验证码已预置在 Redis，无需先调 send_sms）
    login_resp = auth_api.login(phone, code)
    if not is_success(login_resp):
        logger.warning(f"登录失败: {phone} | {login_resp.json()}")
        return None

    try:
        data = login_resp.json().get("data", {})
        token = data.get("accessToken")
        if token:
            logger.info(f"用户登录成功: {phone}")
            return token
        else:
            logger.warning(f"登录响应中未包含 accessToken: {phone}")
            return None
    except Exception as e:
        logger.error(f"解析登录响应失败: {e}")
        return None


def get_customer_token() -> Optional[str]:
    """获取普通用户（13800000003）的 accessToken"""
    return login_and_get_token(config.TEST_CUSTOMER_PHONE)


def get_merchant1_token() -> Optional[str]:
    """获取商家1（13800000002，辣味馆）的 accessToken"""
    return login_and_get_token(config.TEST_MERCHANT1_PHONE)


def get_merchant2_token() -> Optional[str]:
    """获取商家2（13800000004，快乐汉堡）的 accessToken"""
    return login_and_get_token(config.TEST_MERCHANT2_PHONE)


def get_admin_token() -> Optional[str]:
    """获取管理员（13800000001）的 accessToken"""
    return login_and_get_token(config.TEST_ADMIN_PHONE)


class TokenManager:
    """
    Token 管理器 - 缓存各角色 Token，避免重复登录

    用法：
        manager = TokenManager()
        customer_token = manager.get_token("customer")
        merchant_token = manager.get_token("merchant1")
    """

    def __init__(self):
        self._token_cache: Dict[str, str] = {}

    def get_token(self, role: str) -> Optional[str]:
        """
        获取指定角色的 Token（带缓存）

        Args:
            role: 角色名（customer / merchant1 / merchant2 / admin）

        Returns:
            Optional[str]: accessToken
        """
        if role in self._token_cache:
            return self._token_cache[role]

        token = None
        if role == "customer":
            token = get_customer_token()
        elif role == "merchant1":
            token = get_merchant1_token()
        elif role == "merchant2":
            token = get_merchant2_token()
        elif role == "admin":
            token = get_admin_token()

        if token:
            self._token_cache[role] = token
        return token

    def clear_cache(self):
        """清除 Token 缓存"""
        self._token_cache.clear()
        logger.info("Token 缓存已清除")
