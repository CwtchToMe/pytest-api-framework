"""
商家端订单管理页面 - Element Plus
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class MerchantOrderManagePage(BasePage):
    """商家端订单管理页面"""

    ORDER_TABLE = (By.CSS_SELECTOR, ".el-table, .order-table")
    ORDER_ROWS = (By.CSS_SELECTOR, ".el-table__row")
    ACCEPT_BTN = (By.XPATH, "//button[contains(text(),'接单')]")
    REJECT_BTN = (By.XPATH, "//button[contains(text(),'拒单')]")
    READY_BTN = (By.XPATH, "//button[contains(text(),'备餐完成')]")
    COMPLETE_BTN = (By.XPATH, "//button[contains(text(),'完成')]")

    def open(self):
        self.driver.get(f"{config.MERCHANT_BASE_URL}/orders")
        return self

    def get_order_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.ORDER_ROWS))
        except Exception:
            return 0

    def accept_first_order(self):
        self.click(self.ACCEPT_BTN)

    def mark_first_order_ready(self):
        self.click(self.READY_BTN)

    def complete_first_order(self):
        self.click(self.COMPLETE_BTN)
