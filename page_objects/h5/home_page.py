"""
H5 端首页 - Vant 组件库
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class H5HomePage(BasePage):
    """H5 用户端首页"""

    SEARCH_BAR = (By.CSS_SELECTOR, ".search-bar")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder*='搜索'], .search-input input")
    MERCHANT_CARDS = (By.CSS_SELECTOR, ".merchant-card")
    CATEGORY_ITEMS = (By.CSS_SELECTOR, ".category-item")
    HOME_HEADER = (By.CSS_SELECTOR, ".home-header")

    def open(self):
        self.driver.get(config.H5_BASE_URL)
        return self

    def get_merchant_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.MERCHANT_CARDS))
        except Exception:
            return 0

    def get_category_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.CATEGORY_ITEMS))
        except Exception:
            return 0

    def click_merchant_by_index(self, index=0):
        """
        点击第 N 个商家卡片（真实用户点击）。

        用 find_elements 获取所有商家卡片列表，按索引取第 index 个，
        滚动到可视区域后用 Selenium 原生 click。
        """
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        # 等待至少一个商家卡片出现
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.MERCHANT_CARDS)
        )
        # 用 find_elements 取所有卡片，按索引获取
        cards = self.driver.find_elements(*self.MERCHANT_CARDS)
        if index >= len(cards):
            raise IndexError(f"索引 {index} 超出商家卡片总数 {len(cards)}")
        card = cards[index]
        # 先滚动到可视区域，避免被遮挡
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", card
        )
        # Selenium 原生点击
        card.click()
        return self

    def click_search_bar(self):
        """点击搜索栏"""
        self.click(self.SEARCH_BAR)

    def search_for(self, keyword: str):
        """点击搜索栏并输入关键字"""
        self.click_search_bar()
        inp = self.find_element(self.SEARCH_INPUT)
        inp.clear()
        inp.send_keys(keyword)
        return self
