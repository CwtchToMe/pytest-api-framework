"""
H5 端登录页面 - Vant 组件库
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class H5LoginPage(BasePage):
    """H5 用户端登录页面"""

    PHONE_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入手机号']")
    SEND_CODE_BTN = (By.CSS_SELECTOR, "button.sms-btn")
    CODE_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入验证码']")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button.login-btn")
    ERROR_MSG = (By.CSS_SELECTOR, ".van-toast__text, .van-field__error-message")
    BRAND_NAME = (By.CSS_SELECTOR, ".brand-name")

    def open(self):
        self.driver.get(f"{config.H5_BASE_URL}/login")
        return self

    def login(self, phone: str, code: str):
        self.input_text(self.PHONE_INPUT, phone)
        self.click(self.SEND_CODE_BTN)
        self.input_text(self.CODE_INPUT, code)
        self.click(self.SUBMIT_BTN)
        self.wait_for_url_not_contains("/login")

    def is_logged_in(self) -> bool:
        return "/login" not in self.driver.current_url

    def is_login_page(self) -> bool:
        return self.is_element_visible(self.PHONE_INPUT)
