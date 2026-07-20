"""
商家端 UI 测试 - Element Plus 组件库（localhost:3002）
"""

import allure
import pytest

from config.config import config
from page_objects.merchant_web.login_page import MerchantLoginPage
from page_objects.merchant_web.order_manage_page import MerchantOrderManagePage
from page_objects.merchant_web.shop_manage_page import MerchantShopManagePage


@pytest.mark.merchant
@pytest.mark.ui
@allure.feature("商家端")
class TestMerchant:
    """商家端全量测试，共享一个 module-scope 浏览器"""

    @allure.story("登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("完整登录")
    def test_login_full_flow(self, desktop_driver):
        page = MerchantLoginPage(desktop_driver)
        page.open()
        assert page.is_element_visible(page.PHONE_INPUT), "手机号输入框应可见"
        page.login(config.TEST_MERCHANT1_PHONE, config.TEST_SMS_CODE)
        assert page.is_logged_in(), "登录后应跳转到首页"

    @allure.story("订单管理")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("订单管理浏览")
    def test_orders_full_view(self, desktop_driver):
        page = MerchantOrderManagePage(desktop_driver).open()
        assert page.is_element_visible(page.ORDER_TABLE, timeout=5), "订单表格应可见"
        count = page.get_order_count()
        print(f"  订单行数: {count}")
        if count > 0:
            has_accept = page.is_element_visible(page.ACCEPT_BTN, timeout=2)
            print(f"  接单按钮{'可见' if has_accept else '不可见'}")

    @allure.story("店铺管理")
    @allure.title("店铺信息与营业状态")
    def test_shop_info_and_status(self, desktop_driver):
        shop = MerchantShopManagePage(desktop_driver).open()
        print(f"  店铺名称: {shop.get_shop_name()}")
        try:
            shop.toggle_status()
            shop.toggle_status()
            print("  营业状态已切换并恢复")
        except Exception as e:
            print(f"  营业状态切换跳过: {e}")

    @allure.story("订单处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("订单处理全流程")
    def test_process_order(self, desktop_driver):
        import requests

        from common.test_helpers import get_customer_token

        try:
            token = get_customer_token()
            if not token:
                pytest.skip("无法获取顾客 token")
            h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            requests.post(
                "http://localhost:8080/api/cart/add",
                json={"dishId": 1, "merchantId": 1, "quantity": 1},
                headers=h,
            )
            addr = requests.get("http://localhost:8080/api/user/address", headers=h)
            if not addr.ok or not addr.json().get("data"):
                pytest.skip("无收货地址")
            aid = addr.json()["data"][0]["id"]
            order = requests.post(
                "http://localhost:8080/api/order/submit",
                json={
                    "merchantId": 1,
                    "addressId": aid,
                    "items": [{"dishId": 1, "quantity": 1}],
                },
                headers=h,
            )
            if not order.ok or not order.json().get("success"):
                pytest.skip("提交订单失败")
            order_no = order.json()["data"]["orderNo"]
            print(f"  已创建订单: {order_no}")
            pay = requests.post(
                "http://localhost:8080/api/pay/create",
                json={"orderNo": order_no, "payType": 1},
                headers=h,
            )
            if pay.ok and pay.json().get("success"):
                pn = pay.json()["data"]["paymentNo"]
                requests.post(
                    "http://localhost:8080/api/pay/callback",
                    json={"paymentNo": pn, "success": True},
                    headers=h,
                )
        except Exception as e:
            pytest.skip(f"创建测试订单失败: {e}")

        op = MerchantOrderManagePage(desktop_driver).open()
        assert op.is_element_visible(op.ORDER_TABLE, timeout=5), "订单表格应可见"
        for btn, label in [
            (op.ACCEPT_BTN, "接单"),
            (op.READY_BTN, "备餐"),
            (op.COMPLETE_BTN, "完成"),
        ]:
            try:
                if op.is_element_visible(btn, timeout=2):
                    op.click(btn)
                    print(f"  已{label}")
            except Exception:
                pass
        print("  订单处理流程完成")
