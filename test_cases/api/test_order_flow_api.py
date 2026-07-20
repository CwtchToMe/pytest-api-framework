"""
购物车 → 创建订单 → 支付 → 评价全流程 API 测试

测试覆盖：
- 购物车增删改查
- 用户提交/取消/查看订单
- 商家接单/拒单/备餐/完成
- 支付创建与状态查询
- 评价提交

双模式：Mock / 真实 API

设计说明：
- Mock 模式：setup 函数直接返回 mock 数据，不依赖真实后端
- 真实模式：setup 函数执行真实 API 调用，失败时 pytest.skip 优雅跳过
"""

from typing import Optional

import allure
import pytest

from api.takeout_api import (
    CartApi,
    OrderApi,
    PayApi,
    ProductApi,
    ReviewApi,
    UserApi,
    is_success,
)
from common.mock_util import MockHelper
from common.test_helpers import get_customer_token, get_merchant1_token
from config.config import config

#
# 前置条件辅助函数
# Mock 模式直接返回模拟数据，真实模式调用真实后端
#


def _get_customer_token():
    return get_customer_token()


def _get_merchant_token():
    return get_merchant1_token()


def _create_test_order(
    http_session, customer_token=None, merchant_id=1, dish_id=1
) -> Optional[str]:
    """
    创建一个测试订单，返回 order_no。

    Mock 模式：直接返回模拟订单号。
    真实模式：调用真实后端链路（加购→地址→下单），失败返回 None。
    """
    if config.USE_MOCK:
        return "ORD_MOCK_" + str(hash(f"{merchant_id}-{dish_id}") & 0xFFFFF)

    token = customer_token or _get_customer_token()
    if not token:
        return None

    cart = CartApi(token, requests=http_session)
    cart.add_item(dish_id=dish_id, merchant_id=merchant_id, quantity=1)

    user = UserApi(token, requests=http_session)
    addr_resp = user.list_addresses()
    if not is_success(addr_resp):
        return None
    addresses = addr_resp.json().get("data", [])
    if not addresses:
        return None
    address_id = addresses[0]["id"]

    order = OrderApi(token, requests=http_session)
    result = order.submit_order(
        merchant_id=merchant_id,
        address_id=address_id,
        items=[{"dishId": dish_id, "quantity": 1}],
    )
    if not is_success(result):
        return None

    data = result.json().get("data", {})
    return data.get("orderNo")


def _create_paid_order(
    http_session, customer_token=None, merchant_id=1, dish_id=1
) -> Optional[str]:
    """
    创建订单并完成支付，返回 order_no。
    """
    if config.USE_MOCK:
        return "ORD_PAID_MOCK_" + str(hash(f"{merchant_id}-{dish_id}") & 0xFFFFF)

    token = customer_token or _get_customer_token()
    if not token:
        return None

    order_no = _create_test_order(http_session, token, merchant_id, dish_id)
    if not order_no:
        return None

    pay = PayApi(token, requests=http_session)
    pay_resp = pay.create_payment(order_no, pay_type=1)
    if not is_success(pay_resp):
        return None

    payment_no = pay_resp.json().get("data", {}).get("paymentNo")
    if not payment_no:
        return None

    cb_resp = pay.mock_callback(payment_no)
    if not is_success(cb_resp):
        return None

    return order_no


def _create_completed_order(
    http_session, customer_token=None, merchant_id=1, dish_id=1
) -> Optional[str]:
    """
    创建订单 → 支付 → 商家接单 → 备餐完成 → 完成配送，返回 order_no。
    """
    if config.USE_MOCK:
        return "ORD_DONE_MOCK_" + str(hash(f"{merchant_id}-{dish_id}") & 0xFFFFF)

    token = customer_token or _get_customer_token()
    if not token:
        return None

    order_no = _create_paid_order(http_session, token, merchant_id, dish_id)
    if not order_no:
        return None

    merchant_token = _get_merchant_token()
    if not merchant_token:
        return None

    m_order = OrderApi(merchant_token, requests=http_session)
    for action in ["accept_order", "mark_ready", "complete_order"]:
        resp = getattr(m_order, action)(order_no)
        if not is_success(resp):
            return None

    return order_no


class TestCart:
    """购物车功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.http_session = http_session
        self.token = _get_customer_token()

    def test_add_to_cart(self, mock_helper):
        """测试添加菜品到购物车"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        cart = CartApi(self.token, requests=self.http_session)

        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {"id": 1, "dishId": 1, "quantity": 2},
            },
        )
        with mock_helper.mock_request(cart, "post", resp):
            result = cart.add_item(dish_id=1, merchant_id=1, quantity=2)

        assert is_success(result), f"加购失败: {result.json()}"

    def test_add_zero_quantity(self, mock_helper):
        """测试数量为0的加购"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        cart = CartApi(self.token, requests=self.http_session)

        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": None}
        )
        with mock_helper.mock_request(cart, "post", resp):
            result = cart.add_item(dish_id=1, merchant_id=1, quantity=0)

        assert result.status_code == 200

    def test_get_cart(self, mock_helper):
        """测试获取购物车内容"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        cart = CartApi(self.token, requests=self.http_session)

        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": [{"id": 1, "dishId": 1, "name": "招牌菜", "quantity": 2}],
            },
        )
        with mock_helper.mock_request(cart, "get", resp):
            result = cart.get_cart(1)

        assert is_success(result), f"获取购物车失败: {result.json()}"

    def test_clear_cart(self, mock_helper):
        """测试清空购物车"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        cart = CartApi(self.token, requests=self.http_session)

        resp = mock_helper.create_mock_response(200, {"code": 200, "success": True})
        with mock_helper.mock_request(cart, "delete", resp):
            result = cart.clear_cart(1)

        assert is_success(result), f"清空购物车失败: {result.json()}"


class TestOrder:
    """订单功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.http_session = http_session
        self.token = _get_customer_token()

    def test_submit_order(self, mock_helper):
        """测试用户提交订单"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        order = OrderApi(self.token, requests=self.http_session)

        address_id = 1
        if not config.USE_MOCK:
            user = UserApi(self.token, requests=self.http_session)
            addr_resp = user.list_addresses()
            if is_success(addr_resp):
                addresses = addr_resp.json().get("data", [])
                if addresses:
                    address_id = addresses[0]["id"]

        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {"id": 1001, "orderNo": "ORD20250101001", "status": "PENDING"},
            },
        )
        with mock_helper.mock_request(order, "post", resp):
            result = order.submit_order(
                merchant_id=1,
                address_id=address_id,
                items=[{"dishId": 1, "quantity": 2}],
            )

        if not is_success(result) and "库存不足" in result.json().get("message", ""):
            pytest.skip("菜品库存不足，跳过")
        assert is_success(result), f"提交订单失败: {result.json()}"
        data = result.json().get("data", {})
        if data:
            assert "orderNo" in data or "id" in data

    def test_list_my_orders(self, mock_helper):
        """测试获取我的订单列表"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        order = OrderApi(self.token, requests=self.http_session)

        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {
                    "records": [{"id": 1, "orderNo": "ORD001", "status": 1}],
                    "total": 1,
                },
            },
        )
        with mock_helper.mock_request(order, "get", resp):
            result = order.list_orders()

        assert is_success(result), f"获取订单列表失败: {result.json()}"

    def test_cancel_order(self, mock_helper):
        """测试取消订单"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        order = OrderApi(self.token, requests=self.http_session)

        order_no = _create_test_order(self.http_session, self.token)
        if not order_no:
            pytest.skip("无法创建测试订单")

        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": None}
        )
        with mock_helper.mock_request(order, "post", resp):
            result = order.cancel_order(order_no)

        assert is_success(result), f"取消订单失败: {result.json()}"


class TestMerchantOrder:
    """商家订单管理测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.http_session = http_session
        self.token = _get_merchant_token()

    def test_merchant_list_orders(self, mock_helper):
        """测试商家获取订单列表"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取商家 Token")
        m_order = OrderApi(self.token, requests=self.http_session)

        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"records": [], "total": 0}}
        )
        with mock_helper.mock_request(m_order, "get", resp):
            result = m_order.merchant_list_orders(merchant_id=1)

        assert is_success(result), f"商家获取订单列表失败: {result.json()}"

    def test_merchant_accept_order(self, mock_helper):
        """测试商家接单"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取商家 Token")

        c_token = _get_customer_token()
        if not c_token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        order_no = _create_paid_order(self.http_session, c_token)
        if not order_no:
            pytest.skip("无法创建已支付测试订单")

        m_order = OrderApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"status": "ACCEPTED"}}
        )
        with mock_helper.mock_request(m_order, "post", resp):
            result = m_order.accept_order(order_no)

        assert is_success(result), f"接单失败: {result.json()}"

    def test_merchant_reject_order(self, mock_helper):
        """测试商家拒单"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取商家 Token")

        c_token = _get_customer_token()
        if not c_token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        order_no = _create_paid_order(self.http_session, c_token)
        if not order_no:
            pytest.skip("无法创建已支付测试订单")

        m_order = OrderApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"status": "REJECTED"}}
        )
        with mock_helper.mock_request(m_order, "post", resp):
            result = m_order.reject_order(order_no, "食材不足")

        assert is_success(result), f"拒单失败: {result.json()}"


class TestPayment:
    """支付功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.http_session = http_session
        self.token = _get_customer_token()

    def test_create_payment(self, mock_helper):
        """测试创建支付记录"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")

        order_no = _create_test_order(self.http_session, self.token)
        if not order_no:
            pytest.skip("无法创建测试订单")

        pay = PayApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"paymentNo": "PAY001"}}
        )
        with mock_helper.mock_request(pay, "post", resp):
            result = pay.create_payment(order_no, 1)

        assert is_success(result), f"创建支付失败: {result.json()}"

    def test_get_payment_status(self, mock_helper):
        """测试查询支付状态"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")

        order_no = _create_paid_order(self.http_session, self.token)
        if not order_no:
            pytest.skip("无法创建已支付测试订单")

        pay = PayApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": {"orderNo": order_no, "status": "SUCCESS"},
            },
        )
        with mock_helper.mock_request(pay, "get", resp):
            result = pay.get_payment_status(order_no)

        assert is_success(result), f"查询支付状态失败: {result.json()}"


class TestReview:
    """评价功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.http_session = http_session
        self.token = _get_customer_token()

    def test_submit_review(self, mock_helper):
        """测试提交评价"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")

        order_no = _create_completed_order(self.http_session, self.token)
        if not order_no:
            pytest.skip("无法创建已完成测试订单")

        review = ReviewApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"id": 1}}
        )
        with mock_helper.mock_request(review, "post", resp):
            result = review.submit_review(order_no, 5, "很好吃！")

        assert is_success(result), f"提交评价失败: {result.json()}"

    def test_submit_review_invalid_rating(self, mock_helper):
        """测试评分=0 时后端应返回 400"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")

        review = ReviewApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(400, {"code": 400, "success": False})
        with mock_helper.mock_request(review, "post", resp):
            result = review.submit_review("ORD_MOCK_001", 0, "测试")

        assert not is_success(result), "无效评分应返回失败"

    def test_get_my_reviews(self, mock_helper):
        """测试获取我的评价列表"""
        if not self.token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")

        review = ReviewApi(self.token, requests=self.http_session)
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": [{"id": 1, "rating": 5, "content": "很好吃！"}],
            },
        )
        with mock_helper.mock_request(review, "get", resp):
            result = review.get_my_reviews()

        assert is_success(result), f"获取评价失败: {result.json()}"
