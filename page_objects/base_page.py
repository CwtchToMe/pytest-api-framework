"""
页面基类

提供所有页面类的公共方法，所有等待均使用显式等待，不依赖 time.sleep。
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class BasePage:
    """页面基类"""

    # 默认超时时间（子类可覆盖）
    WAIT_TIMEOUT = 10
    SHORT_TIMEOUT = 3

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or self.WAIT_TIMEOUT
        self.wait = WebDriverWait(driver, self.timeout)

    def open(self, url):
        """打开页面"""
        logger.info(f"打开页面: {url}")
        self.driver.get(url)

    def find_element(self, locator, timeout=None):
        """查找单个元素，等待元素出现在 DOM 中"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator, timeout=None):
        """查找多个元素，等待至少一个出现"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        """点击元素，等待元素可点击"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logger.info(f"点击元素: {locator}")

    def input_text(self, locator, text):
        """输入文本，等待元素可见可交互"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.clear()
        element.send_keys(text)
        logger.info(f"输入文本: {text}")

    def get_text(self, locator, timeout=None):
        """获取元素文本，等待元素可见"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        el = wait.until(EC.visibility_of_element_located(locator))
        return el.text

    def wait_for_text(self, locator, timeout=None):
        """等待元素的文本非空后返回"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        el = wait.until(lambda d: d.find_element(*locator).text.strip() != "")
        return el.text

    def is_element_visible(self, locator, timeout=None):
        """判断元素是否可见（不抛异常）"""
        try:
            wait = WebDriverWait(self.driver, timeout or self.SHORT_TIMEOUT)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def wait_for_element(self, locator, timeout=None):
        """等待元素可见"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def wait_for_element_disappear(self, locator, timeout=None):
        """等待元素消失"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_url_contains(self, path: str, timeout=None):
        """等待 URL 包含指定路径"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(lambda d: path in d.current_url)

    def wait_for_url_not_contains(self, path: str, timeout=None):
        """等待 URL 不再包含指定路径（如登录后跳转）"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(lambda d: path not in d.current_url)
        logger.info(f"URL 已离开 '{path}'，当前 URL: {self.driver.current_url}")

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    def back(self):
        """浏览器后退"""
        self.driver.back()
