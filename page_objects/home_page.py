"""
GitHub 首页
"""
from selenium.webdriver.common.by import By
from page_objects.base_page import BasePage
import logging

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """GitHub 首页"""
    
    # 页面URL
    HOME_URL = "https://github.com"
    
    # 定位器
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    NAV_HOME = (By.LINK_TEXT, "Home")
    NAV_PULLS = (By.LINK_TEXT, "Pull requests")
    NAV_ISSUES = (By.LINK_TEXT, "Issues")
    NAV_MARKETPLACE = (By.LINK_TEXT, "Marketplace")
    NAV_EXPLORE = (By.LINK_TEXT, "Explore")
    USER_AVATAR = (By.CSS_SELECTOR, "summary.Header-link img.avatar")
    USER_MENU = (By.CSS_SELECTOR, "details-menu")
    SIGN_OUT_BUTTON = (By.LINK_TEXT, "Sign out")
    REPO_LIST = (By.CSS_SELECTOR, "li.repo-list-item")
    NOTIFICATION_INDICATOR = (By.CSS_SELECTOR, "span.mail-status")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open_home_page(self):
        """打开首页"""
        self.open(self.HOME_URL)
        return self
    
    def search(self, keyword):
        """搜索"""
        logger.info(f"搜索: {keyword}")
        self.input_text(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
    
    def is_user_logged_in(self):
        """判断用户是否已登录"""
        return self.is_element_visible(self.USER_AVATAR, timeout=5)
    
    def get_user_avatar_src(self):
        """获取用户头像URL"""
        if self.is_user_logged_in():
            avatar = self.find_element(self.USER_AVATAR)
            return avatar.get_attribute("src")
        return None
    
    def click_user_avatar(self):
        """点击用户头像"""
        self.click(self.USER_AVATAR)
    
    def sign_out(self):
        """退出登录"""
        self.click_user_avatar()
        self.wait_for_element(self.USER_MENU)
        self.click(self.SIGN_OUT_BUTTON)
        logger.info("退出登录")
    
    def navigate_to_pulls(self):
        """导航到 Pull requests"""
        self.click(self.NAV_PULLS)
    
    def navigate_to_issues(self):
        """导航到 Issues"""
        self.click(self.NAV_ISSUES)
    
    def navigate_to_marketplace(self):
        """导航到 Marketplace"""
        self.click(self.NAV_MARKETPLACE)
    
    def navigate_to_explore(self):
        """导航到 Explore"""
        self.click(self.NAV_EXPLORE)
    
    def is_home_page_displayed(self):
        """判断是否在首页"""
        return self.is_element_visible(self.SEARCH_INPUT)
    
    def get_repo_count(self):
        """获取仓库列表数量"""
        repos = self.find_elements(self.REPO_LIST)
        return len(repos)
    
    def has_notifications(self):
        """是否有通知"""
        return self.is_element_visible(self.NOTIFICATION_INDICATOR, timeout=3)
    
    def get_page_title(self):
        """获取页面标题"""
        return self.get_title()
