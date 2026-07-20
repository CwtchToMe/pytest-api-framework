"""
H5 端商家详情页 - 通过点击商家卡片进入
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class H5MerchantDetailPage(BasePage):
    """H5 用户端商家详情页"""

    MERCHANT_NAME = (By.CSS_SELECTOR, ".merchant-name")
    DISH_CARDS = (By.CSS_SELECTOR, ".dish-card")
    DISH_NAMES = (By.CSS_SELECTOR, ".dish-name")
    ADD_BTN = (By.CSS_SELECTOR, "button.add-btn")
    STEP_PLUS = (By.CSS_SELECTOR, "button.step-btn.plus")
    CART_BAR = (By.CSS_SELECTOR, ".cart-bar")
    CART_BADGE = (By.CSS_SELECTOR, ".van-badge")
    CHECKOUT_BTN = (By.CSS_SELECTOR, "button.checkout-btn")
    FAVORITE_BTN = (By.CSS_SELECTOR, ".fav-btn, .like-btn, .collect-btn")
    CAT_NAMES = (By.CSS_SELECTOR, ".cat-name, .category-tab")

    def open(self, merchant_id=0):
        """导航到商家详情页（用 merchant_id=0 时从首页点击进入，否则直接 URL 导航）"""
        if merchant_id == 0:
            # 从首页点击商家卡片进入 — 原生 click，模拟真实用户
            from page_objects.h5.home_page import H5HomePage

            home = H5HomePage(self.driver)
            home.open()
            cards = self.driver.find_elements(*home.MERCHANT_CARDS)
            if cards:
                cards[0].location_once_scrolled_into_view
                cards[0].click()
                self.wait_for_url_contains("/merchant")
        else:
            self.driver.get(f"{config.H5_BASE_URL}/merchant/{merchant_id}")
        return self

    def get_merchant_name(self) -> str:
        try:
            return self.wait_for_text(self.MERCHANT_NAME, timeout=8)
        except Exception:
            return ""

    def get_dish_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.DISH_CARDS))
        except Exception:
            return 0

    def get_dish_names(self) -> list:
        try:
            return [
                n.text for n in self.driver.find_elements(*self.DISH_NAMES) if n.text
            ]
        except Exception:
            return []

    def add_first_dish(self):
        """
        加购第一个菜品。
        先尝试原生 click（滚动后点击模拟真实用户）；
        若被 Vant 底栏遮挡导致 ElementClickInterceptedException，降级为 JS 点击。
        """
        try:
            btn = self.find_element(self.ADD_BTN)
            btn.location_once_scrolled_into_view
            btn.click()
        except Exception:
            try:
                btn = self.find_element(self.STEP_PLUS)
                btn.location_once_scrolled_into_view
                btn.click()
            except Exception:
                # Vant 底栏遮挡时 JS 点击兜底
                btn = self.find_element(self.ADD_BTN)
                self.driver.execute_script("arguments[0].click();", btn)

    def add_dish_by_index(self, index: int = 1):
        try:
            btns = self.find_elements(self.ADD_BTN)
            if index < len(btns):
                btns[index].location_once_scrolled_into_view
                btns[index].click()
            else:
                plus_btns = self.find_elements(self.STEP_PLUS)
                if index < len(plus_btns):
                    plus_btns[index].location_once_scrolled_into_view
                    plus_btns[index].click()
                else:
                    raise Exception(f"找不到第{index+1}个加购按钮")
        except Exception:
            raise

    def get_cart_quantity(self) -> int:
        """等待购物车角标出现且为数字后返回"""
        from selenium.webdriver.support.ui import WebDriverWait as Wait

        try:
            text = Wait(self.driver, 8).until(
                lambda d: d.find_element(*self.CART_BADGE).text.strip()
            )
            return int(text) if text.isdigit() else 0
        except Exception:
            return 0

    def go_to_checkout(self):
        self.click(self.CHECKOUT_BTN)

    def click_favorite(self) -> bool:
        try:
            self.click(self.FAVORITE_BTN)
            return True
        except Exception:
            return False

    def get_category_tabs(self) -> list:
        try:
            return self.driver.find_elements(*self.CAT_NAMES)
        except Exception:
            return []

    def click_category_tab(self, index: int = 0):
        tabs = self.get_category_tabs()
        if index < len(tabs):
            tabs[index].location_once_scrolled_into_view
            tabs[index].click()
