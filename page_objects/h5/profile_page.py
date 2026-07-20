"""
H5 端"我的"页面 - 通过点击底部 Tab 进入
"""

from selenium.webdriver.common.by import By

from page_objects.base_page import BasePage


class H5ProfilePage(BasePage):
    """H5 我的页面"""

    # 底部导航 Tab（Vant 4，按索引：0首页 1搜索 2订单 3我的）
    TABBAR_ITEMS = (By.CSS_SELECTOR, ".van-tabbar-item")

    # 我的页面内容
    FAVORITE_ENTRY = (By.CSS_SELECTOR, ".favorite-entry, a[href*='favorite']")
    COUPON_ENTRY = (By.CSS_SELECTOR, ".coupon-entry, a[href*='coupon']")
    FAVORITE_ITEMS = (By.CSS_SELECTOR, ".favorite-item, .merchant-card")
    COUPON_ITEMS = (By.CSS_SELECTOR, ".coupon-item, .van-coupon-card")
    LOGOUT_BTN = (By.CSS_SELECTOR, "button.logout-btn")
    CONFIRM_LOGOUT = (
        By.XPATH,
        "//button[contains(text(),'确认') or contains(text(),'确定')]",
    )

    def open(self):
        """先回到首页，再点击底部「我的」Tab（第4个）进入"""
        from page_objects.h5.home_page import H5HomePage

        H5HomePage(self.driver).open()
        tabs = self.driver.find_elements(*self.TABBAR_ITEMS)
        if len(tabs) > 3:
            tabs[3].click()
        self.wait_for_url_contains("/profile")
        return self

    def open_favorites(self):
        if self.is_element_visible(self.FAVORITE_ENTRY):
            self.click(self.FAVORITE_ENTRY)
            self.wait_for_url_contains("favorite", timeout=3)

    def open_coupons(self):
        if self.is_element_visible(self.COUPON_ENTRY):
            self.click(self.COUPON_ENTRY)
            self.wait_for_url_contains("coupon", timeout=3)

    def get_favorite_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.FAVORITE_ITEMS))
        except Exception:
            return 0

    def get_coupon_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.COUPON_ITEMS))
        except Exception:
            return 0

    def logout(self) -> bool:
        """点击退出登录按钮 → 确认退出（原生 click 模拟真实用户）"""
        try:
            btn = self.find_element(self.LOGOUT_BTN)
            btn.location_once_scrolled_into_view
            btn.click()
            # 等待确认弹窗出现
            if self.is_element_visible(self.CONFIRM_LOGOUT, timeout=3):
                confirm = self.find_element(self.CONFIRM_LOGOUT)
                confirm.click()
        except Exception as e:
            print(f"  退出失败: {e}")
            return False
        # 等待跳转到登录页
        try:
            self.wait_for_url_contains("/login", timeout=5)
            return True
        except Exception:
            return False
