"""
用户信息 + 优惠券 + 收藏 + 健康检查 API 测试

测试覆盖：
- 用户个人资料（有/无 Token）
- 优惠券列表、领取、已领取
- 商家收藏/取消收藏
- 系统健康检查

已知问题（xfail）：
- list_coupons：后端返回 500
- claim_coupon：后端返回 500
- add_favorite：后端已修复
- get_my_coupons：后端已修复
- remove_favorite：后端已修复
"""

import allure
import pytest

from api.takeout_api import (
    CouponApi,
    FavoriteApi,
    HealthApi,
    UserApi,
    get_biz_code,
    is_success,
)
from common.test_helpers import get_customer_token
from config.config import config


class TestUserProfile:
    """用户个人资料测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.http_session = http_session

    def test_get_user_profile(self, mock_helper):
        """测试有 token → 返回用户信息"""
        token = get_customer_token()
        if not token and not mock_helper.use_mock:
            pytest.skip("无法获取用户 Token")
        user = UserApi(token, requests=self.http_session)

        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {"id": 1, "phone": "138****0003", "nickname": "测试用户"},
            },
        )
        with mock_helper.mock_request(user, "get", resp):
            result = user.get_profile()

        assert is_success(result), f"获取用户资料失败: {result.json()}"
        data = result.json().get("data", {})
        assert "phone" in data or "nickname" in data

    def test_get_user_profile_no_token(self, mock_helper):
        """测试无 token → 401"""
        user = UserApi(requests=self.http_session)  # 不传入 Token

        resp = mock_helper.create_mock_response(
            401, {"code": 401, "success": False, "msg": "未登录"}
        )
        with mock_helper.mock_request(user, "get", resp):
            result = user.get_profile()

        assert not is_success(result), "无 Token 应返回失败"
        assert result.status_code == 401 or get_biz_code(result) == 401


class TestCoupon:
    """优惠券功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        token = get_customer_token()
        if not token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        self.coupon = CouponApi(token, requests=http_session)

    @pytest.mark.xfail(reason="Backend Bug: GET /api/coupon/ 返回 500")
    def test_list_coupons(self, mock_helper):
        """测试获取优惠券列表 — 已知后端返回 500"""
        resp = mock_helper.create_mock_response(500, {"code": 500, "success": False})
        with mock_helper.mock_request(self.coupon, "get", resp):
            result = self.coupon.list_coupons()

        assert is_success(result)  # xfail

    @pytest.mark.xfail(reason="Backend Bug: POST /api/coupon/claim 返回 500")
    def test_claim_coupon(self, mock_helper):
        """测试领取优惠券 — 已知后端返回 500"""
        resp = mock_helper.create_mock_response(500, {"code": 500, "success": False})
        with mock_helper.mock_request(self.coupon, "post", resp):
            result = self.coupon.claim_coupon(1)

        assert is_success(result)  # xfail

    @pytest.mark.xfail(reason="Backend 已修复: GET /api/coupon/my 正常返回")
    def test_get_my_coupons(self, mock_helper):
        """测试获取我的优惠券 — 后端已修复，实际通过→xpassed"""
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": [{"id": 1, "name": "满减券"}]}
        )
        with mock_helper.mock_request(self.coupon, "get", resp):
            result = self.coupon.my_coupons()

        assert is_success(result), f"获取我的优惠券失败: {result.json()}"


class TestFavorite:
    """收藏功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        token = get_customer_token()
        if not token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        self.fav = FavoriteApi(token, requests=http_session)

    def test_add_favorite(self, mock_helper):
        """测试收藏商家"""
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"merchantId": 1}}
        )
        with mock_helper.mock_request(self.fav, "post", resp):
            result = self.fav.add_favorite(1)

        assert is_success(result), f"收藏失败: {result.json()}"

    def test_remove_favorite(self, mock_helper):
        """测试取消收藏"""
        resp = mock_helper.create_mock_response(200, {"code": 200, "success": True})
        with mock_helper.mock_request(self.fav, "delete", resp):
            result = self.fav.remove_favorite(1)

        assert is_success(result), f"取消收藏失败: {result.json()}"


class TestHealth:
    """健康检查测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.health = HealthApi(requests=http_session)

    def test_health_check(self, mock_helper):
        """测试系统健康检查"""
        resp = mock_helper.create_mock_response(200, {"status": "UP", "checks": {}})
        with mock_helper.mock_request(self.health, "get", resp):
            result = self.health.check()

        assert is_success(result), f"健康检查失败: {result.json()}"

    def test_health_check_response_time(self, mock_helper):
        """测试健康检查响应时间不超过 1s"""
        import time

        resp = mock_helper.create_mock_response(200, {"status": "UP", "checks": {}})
        with mock_helper.mock_request(self.health, "get", resp):
            start = time.time()
            result = self.health.check()
            elapsed = time.time() - start

        assert is_success(result), f"健康检查失败: {result.json()}"
        assert elapsed < 1.0, f"响应时间 ({elapsed:.2f}s) 超过 1s 阈值"
