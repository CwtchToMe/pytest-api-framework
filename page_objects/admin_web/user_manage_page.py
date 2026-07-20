"""
管理后台用户管理页面 - Element Plus
"""

from selenium.webdriver.common.by import By

from config.config import config
from page_objects.base_page import BasePage


class AdminUserManagePage(BasePage):
    """管理后台用户管理页面"""

    USER_TABLE = (By.CSS_SELECTOR, ".el-table, .user-table")
    TABLE_ROWS = (By.CSS_SELECTOR, ".el-table__row")

    def open(self):
        self.driver.get(f"{config.ADMIN_BASE_URL}/users")
        return self

    def get_user_count(self) -> int:
        try:
            return len(self.driver.find_elements(*self.TABLE_ROWS))
        except Exception:
            return 0
