"""WebDriver Fixture — scope=module，整个文件共享一个浏览器"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.config import config


def _build_chrome(width: int, height: int, mobile: bool = False):
    opts = Options()
    if config.HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={width},{height}")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    if mobile:
        opts.add_experimental_option(
            "mobileEmulation",
            {"deviceMetrics": {"width": width, "height": height, "pixelRatio": 3.0}},
        )
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(0)
    return d


@pytest.fixture(scope="module")
def mobile_driver():
    """H5 手机浏览器（390×844，移动模拟），文件内所有测试共享"""
    d = _build_chrome(390, 844, mobile=True)
    yield d
    d.quit()


@pytest.fixture(scope="module")
def desktop_driver():
    """桌面浏览器（1280×800），商家端/管理后台共享"""
    d = _build_chrome(1280, 800)
    yield d
    d.quit()
