"""
H5 端结算/下单页面 - Vant 组件库
"""

from selenium.webdriver.common.by import By

from page_objects.base_page import BasePage


class H5CheckoutPage(BasePage):
    """H5 结算/下单页面"""

    ADDRESS_SECTION = (By.CSS_SELECTOR, ".address-section, .order-address")
    REMARK_INPUT = (
        By.CSS_SELECTOR,
        "textarea[placeholder*='备注'], .remark-input textarea",
    )
    SUBMIT_BTN = (
        By.XPATH,
        "//*[contains(@class,'submit-order-btn') or contains(@class,'confirm-btn')] | //button[contains(text(),'提交')]",
    )
    SUCCESS_PANEL = (By.CSS_SELECTOR, ".order-success, .pay-success, .success-panel")

    def input_remark(self, remark: str):
        if self.is_element_visible(self.REMARK_INPUT, timeout=2):
            self.input_text(self.REMARK_INPUT, remark)

    def submit_order(self):
        self.click(self.SUBMIT_BTN)
        self.wait_for_url_contains("/order", timeout=5)
