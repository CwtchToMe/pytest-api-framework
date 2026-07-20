"""
管理后台 UI 测试 - Element Plus 组件库（localhost:3003）
"""

import allure
import pytest

from config.config import config
from page_objects.admin_web.login_page import AdminLoginPage
from page_objects.admin_web.merchant_manage_page import AdminMerchantManagePage
from page_objects.admin_web.order_manage_page import AdminOrderManagePage
from page_objects.admin_web.user_manage_page import AdminUserManagePage


@pytest.mark.admin
@pytest.mark.ui
@allure.feature("管理后台")
class TestAdmin:
    """管理后台全量测试，共享一个 module-scope 浏览器"""

    @allure.story("登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("完整登录")
    def test_login_full_flow(self, desktop_driver):
        page = AdminLoginPage(desktop_driver)
        page.open()
        assert page.is_element_visible(page.PHONE_INPUT), "手机号输入框应可见"
        page.login(config.TEST_ADMIN_PHONE, config.TEST_SMS_CODE)
        assert page.is_logged_in(), "登录后应跳转到首页"

    @allure.story("商家管理")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("商家管理浏览")
    def test_merchant_full_view(self, desktop_driver):
        page = AdminMerchantManagePage(desktop_driver).open()
        assert page.is_element_visible(page.MERCHANT_TABLE, timeout=5), "商家表格应可见"
        print(f"  商家表格行数: {page.get_merchant_count()}")

    @allure.story("订单管理")
    @allure.title("订单管理页面")
    def test_order_page(self, desktop_driver):
        page = AdminOrderManagePage(desktop_driver).open()
        assert page.is_element_visible(page.ORDER_TABLE, timeout=5), "订单表格应可见"
        print(f"  订单行数: {page.get_order_count()}")

    @allure.story("用户管理")
    @allure.title("用户管理页面")
    def test_user_page(self, desktop_driver):
        page = AdminUserManagePage(desktop_driver).open()
        assert page.is_element_visible(page.USER_TABLE, timeout=5), "用户表格应可见"
        print(f"  用户行数: {page.get_user_count()}")
