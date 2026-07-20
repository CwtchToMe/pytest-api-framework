"""
H5 端购物车页面 - Vant 组件库
"""

from selenium.webdriver.common.by import By

from page_objects.base_page import BasePage


class H5CartPage(BasePage):
    """H5 购物车侧边栏"""

    CART_PANEL = (By.CSS_SELECTOR, ".cart-panel, .van-action-sheet, .cart-popup")
    CART_ITEMS = (By.CSS_SELECTOR, ".cart-item, .van-checkbox, .cart-dish-item")
    ITEM_QUANTITY = (
        By.CSS_SELECTOR,
        ".cart-item .step-count, .van-stepper__input, .num-text",
    )
    CLEAR_BTN = (
        By.XPATH,
        "//*[contains(@class,'clear-btn')] | //button[contains(text(),'清空')]",
    )
    CONFIRM_CLEAR = (
        By.XPATH,
        "//*[contains(@class,'van-dialog__confirm') or contains(@class,'confirm-btn')] | //button[contains(text(),'确认') or contains(text(),'确定')]",
    )
    CHECKOUT_BTN = (By.CSS_SELECTOR, ".checkout-btn, .submit-btn, .go-pay-btn")

    def get_item_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.CART_ITEMS))
        except Exception:
            return 0

    def clear_cart(self):
        try:
            if self.is_element_visible(self.CLEAR_BTN):
                self.click(self.CLEAR_BTN)
            if self.is_element_visible(self.CONFIRM_CLEAR):
                self.click(self.CONFIRM_CLEAR)
        except Exception:
            pass
