"""
管理后台订单管理页面 - Element Plus
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class AdminOrderManagePage(BasePage):
    """管理后台订单管理页面"""

    ORDER_TABLE = (By.CSS_SELECTOR, ".el-table, .order-table")
    TABLE_ROWS = (By.CSS_SELECTOR, ".el-table__row")

    def open(self):
        self.driver.get(f"{config.ADMIN_BASE_URL}/orders")
        return self

    def get_order_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.TABLE_ROWS))
        except Exception:
            return 0
