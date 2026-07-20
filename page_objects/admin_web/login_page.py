"""
管理后台登录页面 - Element Plus
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class AdminLoginPage(BasePage):
    """管理后台登录页面"""

    PHONE_INPUT = (By.CSS_SELECTOR, "input[placeholder*='手机']")
    SEND_CODE_BTN = (By.CSS_SELECTOR, "button.el-button:not(.el-button--primary)")
    CODE_INPUT = (By.CSS_SELECTOR, "input[placeholder*='验证码']")
    SUBMIT_BTN = (By.CSS_SELECTOR, ".el-button--primary")

    def open(self):
        self.driver.get(f"{config.ADMIN_BASE_URL}/login")
        return self

    def login(self, phone: str, code: str):
        self.input_text(self.PHONE_INPUT, phone)
        self.click(self.SEND_CODE_BTN)
        self.input_text(self.CODE_INPUT, code)
        self.click(self.SUBMIT_BTN)
        self.wait_for_url_not_contains("/login")

    def is_logged_in(self) -> bool:
        return "/login" not in self.driver.current_url
