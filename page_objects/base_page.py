"""
页面基类

提供所有页面类的公共方法
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time
import os

logger = logging.getLogger(__name__)


class BasePage:
    """页面基类"""
    
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
    
    def open(self, url):
        """打开页面"""
        logger.info(f"打开页面: {url}")
        self.driver.get(url)
    
    def find_element(self, locator):
        """查找单个元素"""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator):
        """查找多个元素"""
        return self.wait.until(EC.presence_of_all_elements_located(locator))
    
    def click(self, locator):
        """点击元素"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logger.info(f"点击元素: {locator}")
    
    def input_text(self, locator, text):
        """输入文本"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        logger.info(f"输入文本: {text}")
    
    def get_text(self, locator):
        """获取元素文本"""
        element = self.find_element(locator)
        return element.text
    
    def is_element_visible(self, locator, timeout=None):
        """判断元素是否可见"""
        try:
            wait = WebDriverWait(self.driver, timeout or self.timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False
    
    def wait_for_element(self, locator, timeout=None):
        """等待元素出现"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))
    
    def wait_for_element_disappear(self, locator, timeout=None):
        """等待元素消失"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.invisibility_of_element_located(locator))
    
    def get_title(self):
        """获取页面标题"""
        return self.driver.title
    
    def get_url(self):
        """获取当前URL"""
        return self.driver.current_url
    
    def screenshot(self, name="screenshot"):
        """截图"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"
        os.makedirs("screenshots", exist_ok=True)
        self.driver.save_screenshot(filename)
        logger.info(f"截图保存: {filename}")
        return filename
    
    def execute_script(self, script, *args):
        """执行JavaScript"""
        return self.driver.execute_script(script, *args)
    
    def scroll_to_element(self, locator):
        """滚动到元素位置"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def hover(self, locator):
        """鼠标悬停"""
        element = self.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()
        logger.info(f"鼠标悬停: {locator}")
