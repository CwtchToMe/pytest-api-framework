"""
商家端店铺管理页面 - Element Plus
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class MerchantShopManagePage(BasePage):
    """商家端店铺管理页面"""

    SHOP_NAME = (By.CSS_SELECTOR, ".shop-name, .merchant-name, .el-statistic__content")
    STATUS_SWITCH = (By.CSS_SELECTOR, ".el-switch, .status-switch")

    def open(self):
        self.driver.get(f"{config.MERCHANT_BASE_URL}/shop")
        return self

    def get_shop_name(self) -> str:
        try:
            return self.get_text(self.SHOP_NAME)
        except Exception:
            return ""

    def toggle_status(self):
        if self.is_element_visible(self.STATUS_SWITCH):
            self.click(self.STATUS_SWITCH)
