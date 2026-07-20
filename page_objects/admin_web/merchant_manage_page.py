"""
管理后台商家管理页面 - Element Plus
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class AdminMerchantManagePage(BasePage):
    """管理后台商家管理页面"""

    MERCHANT_TABLE = (By.CSS_SELECTOR, ".el-table, .merchant-table")
    TABLE_ROWS = (By.CSS_SELECTOR, ".el-table__row")

    def open(self):
        self.driver.get(f"{config.ADMIN_BASE_URL}/merchants")
        return self

    def get_merchant_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.TABLE_ROWS))
        except Exception:
            return 0
