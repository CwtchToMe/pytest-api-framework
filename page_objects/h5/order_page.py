"""
H5 端订单列表页面 - 点击底部 Tab 进入
"""

from selenium.webdriver.common.by import By

from page_objects.base_page import BasePage


class H5OrderPage(BasePage):
    """H5 订单列表页面"""

    TABBAR_ITEMS = (By.CSS_SELECTOR, ".van-tabbar-item")
    ORDER_CARDS = (By.CSS_SELECTOR, ".order-card, .van-card, .order-item-wrapper")
    TAB_ALL = (By.XPATH, "//div[contains(text(),'全部')]/..")
    TAB_PENDING = (By.XPATH, "//div[contains(text(),'待付款')]/..")

    def open(self):
        """先回到首页，再点击底部「订单」Tab（第3个）进入"""
        from page_objects.h5.home_page import H5HomePage

        H5HomePage(self.driver).open()
        tabs = self.driver.find_elements(*self.TABBAR_ITEMS)
        if len(tabs) > 2:
            tabs[2].click()
        self.wait_for_url_contains("/orders")
        return self

    def get_order_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.ORDER_CARDS))
        except Exception:
            return 0

    def switch_tab(self, tab_name: str):
        locator = {"全部": self.TAB_ALL, "待付款": self.TAB_PENDING}.get(tab_name)
        if locator and self.is_element_visible(locator, timeout=2):
            self.click(locator)
