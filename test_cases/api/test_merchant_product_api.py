"""
商家信息 + 商品管理 API 测试

测试覆盖：
- 商家搜索（关键字搜索 + 附近商家）
- 商品菜单查询
- 菜品管理（增删改查 + 上下架）
- 边界值测试（空菜品名、负价格）

双模式：Mock / 真实 API
"""

import allure
import pytest

from api.takeout_api import AuthApi, MerchantApi, ProductApi, get_biz_code, is_success
from common.test_helpers import get_customer_token, get_merchant1_token
from config.config import config


class TestMerchantSearch:
    """商家搜索功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        self.merchant = MerchantApi(requests=http_session)

    def test_search_by_keyword(self, mock_helper):
        """测试搜索关键词，返回至少1条结果"""
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": [{"id": 1, "name": "辣味馆", "score": 4.5}],
            },
        )
        with mock_helper.mock_request(self.merchant, "get", resp):
            result = self.merchant.search("辣")

        assert is_success(result), f"搜索失败: {result.json()}"
        data = result.json().get("data", [])
        if isinstance(data, list) and len(data) > 0:
            assert "name" in data[0]

    def test_get_nearby_merchants(self, mock_helper):
        """测试坐标附近商家列表"""
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": [{"id": 1, "name": "辣味馆", "distance": 500}],
            },
        )
        with mock_helper.mock_request(self.merchant, "get", resp):
            result = self.merchant.get_nearby(31.23, 121.47, 5000)

        assert is_success(result), f"获取附近商家失败: {result.json()}"


class TestProductMenu:
    """商品菜单查询测试"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        token = get_customer_token()
        if not token and not config.USE_MOCK:
            pytest.skip("无法获取用户 Token")
        self.product = ProductApi(token, requests=http_session)

    def test_get_merchant_menu(self, mock_helper):
        """测试获取商家1菜单，有分类有菜品"""
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": [
                    {"categoryName": "热销", "dishes": [{"id": 1, "name": "招牌菜"}]}
                ],
            },
        )
        with mock_helper.mock_request(self.product, "get", resp):
            result = self.product.get_menu(1)

        assert is_success(result), f"获取菜单失败: {result.json()}"

    def test_get_product_category(self, mock_helper):
        """测试获取商品分类"""
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": [{"id": 1, "name": "热销推荐"}]}
        )
        with mock_helper.mock_request(self.product, "get", resp):
            result = self.product.list_categories(1)

        assert is_success(result), f"获取分类失败: {result.json()}"

    @pytest.mark.parametrize(
        "merchant_id,expect_items",
        [
            (1, True),
            (2, True),
        ],
        ids=["merchant_1", "merchant_2"],
    )
    def test_list_dishes(self, mock_helper, merchant_id, expect_items):
        """测试获取菜品列表"""
        resp = mock_helper.create_mock_response(
            200,
            {
                "code": 200,
                "success": True,
                "data": [{"id": 1, "name": "招牌菜", "price": 29.9}],
            },
        )
        with mock_helper.mock_request(self.product, "get", resp):
            result = self.product.list_dishes(merchant_id)

        assert is_success(result), f"获取菜品列表失败: {result.json()}"
        data = result.json().get("data", [])
        if isinstance(data, list) and len(data) > 0 and expect_items:
            assert "price" in data[0]


class TestProductManage:
    """菜品管理测试（需要商家 Token）"""

    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        token = get_merchant1_token()
        if not token and not config.USE_MOCK:
            pytest.skip("无法获取商家 Token")
        self.product = ProductApi(token, requests=http_session)

    def test_add_dish(self, mock_helper):
        """测试商家端添加菜品"""
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"id": 100, "name": "新菜品"}}
        )
        with mock_helper.mock_request(self.product, "post", resp):
            result = self.product.add_dish(
                merchantId=1, name="新菜品", price=19.9, categoryId=1
            )

        assert is_success(result), f"添加菜品失败: {result.json()}"

    @allure.title("添加菜品失败 - {case}")
    @pytest.mark.parametrize(
        "dish_name,price,status_code,resp_data,case",
        [
            (
                "",
                19.9,
                400,
                {"code": 400, "success": False, "msg": "菜品名称不能为空"},
                "空名称",
            ),
            (
                "测试",
                -1,
                400,
                {"code": 400, "success": False, "msg": "价格不能为负"},
                "负价格",
            ),
        ],
        ids=["empty_name", "negative_price"],
    )
    def test_add_dish_invalid(
        self, mock_helper, dish_name, price, status_code, resp_data, case
    ):
        """测试添加菜品的边界值"""
        resp = mock_helper.create_mock_response(status_code, resp_data)
        with mock_helper.mock_request(self.product, "post", resp):
            result = self.product.add_dish(name=dish_name, price=price, categoryId=1)

        assert not is_success(result), f"场景'{case}'应返回失败"

    def test_update_dish(self, mock_helper):
        """测试更新菜品信息"""
        resp = mock_helper.create_mock_response(
            200,
            {"code": 200, "success": True, "data": {"id": 1, "name": "更新后的菜品"}},
        )
        with mock_helper.mock_request(self.product, "put", resp):
            result = self.product.update_dish(1, name="更新后的菜品", price=29.9)

        assert is_success(result), f"更新菜品失败: {result.json()}"

    @allure.title("菜品上下架 - {action}")
    @pytest.mark.parametrize(
        "status,action",
        [
            (0, "下架"),
            (1, "上架"),
        ],
        ids=["offline", "online"],
    )
    def test_toggle_dish_status(self, mock_helper, status, action):
        """测试菜品上下架"""
        resp = mock_helper.create_mock_response(
            200, {"code": 200, "success": True, "data": {"id": 1, "status": status}}
        )
        with mock_helper.mock_request(self.product, "put", resp):
            result = self.product.toggle_dish_status(1, status)

        assert is_success(result), f"菜品{action}失败: {result.json()}"
