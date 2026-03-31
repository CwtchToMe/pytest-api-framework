"""
GitHub 登录页面
"""
from selenium.webdriver.common.by import By
from page_objects.base_page import BasePage
import logging

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """GitHub 登录页面"""
    
    # 页面URL
    LOGIN_URL = "https://github.com/login"
    
    # 定位器
    USERNAME_INPUT = (By.ID, "login_field")
    PASSWORD_INPUT = (By.ID, "password")
    SIGN_IN_BUTTON = (By.NAME, "commit")
    ERROR_MESSAGE = (By.CLASS_NAME, "flash-error")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot password?")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open_login_page(self):
        """打开登录页面"""
        self.open(self.LOGIN_URL)
        return self
    
    def login(self, username, password):
        """登录操作"""
        logger.info(f"登录用户: {username}")
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click(self.SIGN_IN_BUTTON)
    
    def get_error_message(self):
        """获取错误信息"""
        if self.is_element_visible(self.ERROR_MESSAGE, timeout=5):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def is_login_page_displayed(self):
        """判断是否在登录页面"""
        return self.is_element_visible(self.USERNAME_INPUT) and \
               self.is_element_visible(self.PASSWORD_INPUT)
    
    def click_forgot_password(self):
        """点击忘记密码"""
        self.click(self.FORGOT_PASSWORD_LINK)
    
    def is_username_field_displayed(self):
        """判断用户名输入框是否显示"""
        return self.is_element_visible(self.USERNAME_INPUT)
    
    def is_password_field_displayed(self):
        """判断密码输入框是否显示"""
        return self.is_element_visible(self.PASSWORD_INPUT)
    
    def is_sign_in_button_displayed(self):
        """判断登录按钮是否显示"""
        return self.is_element_visible(self.SIGN_IN_BUTTON)
