"""
认证模块 API 测试用例

测试覆盖：
- 短信验证码发送（正常 + 异常）
- 用户登录（各角色 + 边界值）
- Token 刷新（有效 + 无效）

双模式设计：
- USE_MOCK=true：使用 Mock 响应（通过 mock_helper fixture）
- USE_MOCK=false：对接真实 TakeoutSystem 后端
"""

import allure
import pytest

from api.takeout_api import AuthApi, get_biz_code, is_success
from config.config import config


class TestAuthSms:
    """短信验证码发送测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.auth = AuthApi(requests=http_session)

    def test_send_sms_success(self, mock_helper):
        """测试正常手机号发送验证码

        注意：后端限制 60 秒内只能发一次验证码，可能返回 400（频率限制）。
        """
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": None}
        )
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.send_sms(config.TEST_CUSTOMER_PHONE)

        data = result.json()
        is_rate_limited = data.get("code") != 200 and "频繁" in data.get("message", "")
        assert is_success(result) or is_rate_limited, f"发送验证码失败: {data}"

    @allure.title("发送验证码失败 - {case}")
    @pytest.mark.parametrize(
        "phone,status_code,resp_data,case",
        [
            (
                "1234",
                400,
                {"code": 400, "success": False, "msg": "手机号格式错误"},
                "格式错误",
            ),
            (
                "",
                400,
                {"code": 400, "success": False, "msg": "手机号不能为空"},
                "空手机号",
            ),
            (
                "abc",
                400,
                {"code": 400, "success": False, "msg": "手机号格式错误"},
                "非数字",
            ),
        ],
        ids=["format_error", "empty", "non_numeric"],
    )
    def test_send_sms_invalid_phone(
        self, mock_helper, phone, status_code, resp_data, case
    ):
        """测试格式错误手机号发送验证码

        Args:
            phone: 手机号
            status_code: 模拟的 HTTP 状态码
            resp_data: 模拟的响应体
            case: 用例描述
        """
        resp = mock_helper.create_mock_response(status_code, resp_data)
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.send_sms(phone)

        assert not is_success(result), f"手机号'{phone}'应返回失败"


class TestAuthLogin:
    """用户登录测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.auth = AuthApi(requests=http_session)

    @allure.title("用户登录成功 - {role}")
    @pytest.mark.parametrize(
        "phone,role",
        [
            (config.TEST_CUSTOMER_PHONE, "普通用户"),
            (config.TEST_MERCHANT1_PHONE, "商家1"),
            (config.TEST_MERCHANT2_PHONE, "商家2"),
            (config.TEST_ADMIN_PHONE, "管理员"),
        ],
        ids=["customer", "merchant1", "merchant2", "admin"],
    )
    def test_login_success(self, mock_helper, phone, role):
        """测试各角色用户登录成功，返回 accessToken

        Args:
            phone: 手机号
            role: 角色描述
        """
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {
                    "accessToken": f"mock-token-{role}",
                    "refreshToken": "mock-refresh",
                },
            },
        )
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.login(phone, config.TEST_SMS_CODE)

        assert is_success(result), f"{role} 登录失败"
        data = result.json().get("data", {})
        assert "accessToken" in data, "响应中应包含 accessToken"

    @allure.title("登录失败 - {case}")
    @pytest.mark.parametrize(
        "phone,code,status_code,resp_data,case",
        [
            (
                config.TEST_CUSTOMER_PHONE,
                "000000",
                400,
                {"code": 400, "success": False, "msg": "验证码错误"},
                "错误验证码",
            ),
            (
                "",
                config.TEST_SMS_CODE,
                400,
                {"code": 400, "success": False, "msg": "手机号不能为空"},
                "空手机号",
            ),
            (
                "1380000",
                config.TEST_SMS_CODE,
                400,
                {"code": 400, "success": False, "msg": "手机号格式错误"},
                "格式错误手机号",
            ),
        ],
        ids=["wrong_code", "empty_phone", "invalid_phone"],
    )
    def test_login_failed(self, mock_helper, phone, code, status_code, resp_data, case):
        """测试各种异常登录场景"""
        resp = mock_helper.create_mock_response(status_code, resp_data)
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.login(phone, code)

        assert not is_success(result), f"场景'{case}'应返回失败"


class TestAuthTokenRefresh:
    """Token 刷新测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.auth = AuthApi(requests=http_session)

    def test_refresh_token_success(self, mock_helper):
        """测试有效 refreshToken → 返回新 accessToken"""
        refresh_token = "valid-refresh-token"

        if not mock_helper.use_mock:
            login_resp = self.auth.login(
                config.TEST_CUSTOMER_PHONE, config.TEST_SMS_CODE
            )
            if not is_success(login_resp):
                pytest.skip("登录失败，无法测试 Token 刷新")
            refresh_token = login_resp.json().get("data", {}).get("refreshToken")
            if not refresh_token:
                pytest.skip("登录响应中无 refreshToken")

        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {
                    "accessToken": "new-mock-token",
                    "refreshToken": "new-mock-refresh",
                },
            },
        )
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.refresh_token(refresh_token)

        assert is_success(result), f"Token 刷新失败: {result.json()}"

    def test_refresh_invalid_token(self, mock_helper):
        """测试无效 refreshToken → success=false"""
        resp = mock_helper.create_mock_response(
            401, {"code": 401, "success": False, "msg": "无效的 refreshToken"}
        )
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.refresh_token("invalid-token")

        assert not is_success(result), "无效 Token 时应返回失败"
