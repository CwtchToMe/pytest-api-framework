"""
项目配置管理模块 - 支持多环境配置和 .env 文件

目标系统：TakeoutSystem 外卖点餐系统

设计要点：
1. 环境变量优先，.env 文件兜底，代码默认值最低优先级
2. 多环境继承体系：Config(基类) → DevConfig / TestConfig / StagingConfig / ProdConfig
3. 启动时自动验证配置有效性（URL 格式、超时范围、浏览器类型等）
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env 文件（优先从项目根目录）
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class ConfigValidationError(Exception):
    """配置验证错误"""

    pass


class Config:
    """基础配置类 - 可被子类继承覆盖"""

    # ========== 环境选择 ==========
    ENVIRONMENT = os.getenv("ENV", "test")

    # ========== 后端 API 配置 ==========
    TAKEOUT_API_URL = os.getenv("TAKEOUT_API_URL", "http://localhost:8080")
    API_BASE_URL = TAKEOUT_API_URL  # HTTP 请求基类使用的根地址
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    API_VERIFY_SSL = os.getenv("API_VERIFY_SSL", "true").lower() == "true"

    # ========== 功能开关 ==========
    ENABLE_PLUGINS = os.getenv("ENABLE_PLUGINS", "true").lower() == "true"
    USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

    # ========== 前端 UI 地址（Selenium 测试使用） ==========
    H5_BASE_URL = os.getenv("H5_BASE_URL", "http://localhost:3001")
    MERCHANT_BASE_URL = os.getenv("MERCHANT_BASE_URL", "http://localhost:3002")
    ADMIN_BASE_URL = os.getenv("ADMIN_BASE_URL", "http://localhost:3003")
    UI_BASE_URL = os.getenv("UI_BASE_URL", "http://localhost:3001")

    # ========== 浏览器配置（Selenium） ==========
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1920"))
    WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "1080"))
    WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "10"))

    # ========== 日志配置 ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_FILE = os.getenv("LOG_FILE", "test.log")

    # ========== 报告与截图配置 ==========
    REPORT_DIR = os.getenv("REPORT_DIR", "reports")
    ALLURE_DIR = os.getenv("ALLURE_DIR", "reports/allure_results")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"

    # ========== 测试账号配置 ==========
    TEST_SMS_CODE = os.getenv("TEST_SMS_CODE", "123456")
    TEST_CUSTOMER_PHONE = os.getenv("TEST_CUSTOMER_PHONE", "13800000003")
    TEST_MERCHANT1_PHONE = os.getenv("TEST_MERCHANT1_PHONE", "13800000002")
    TEST_MERCHANT2_PHONE = os.getenv("TEST_MERCHANT2_PHONE", "13800000004")
    TEST_ADMIN_PHONE = os.getenv("TEST_ADMIN_PHONE", "13800000001")

    # 创建必要的目录
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(ALLURE_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    @classmethod
    def validate(cls) -> None:
        """
        验证配置的有效性

        Raises:
            ConfigValidationError: 如果配置无效
        """
        errors = []

        # 验证 API_BASE_URL 格式
        if not cls._is_valid_url(cls.API_BASE_URL):
            errors.append(f"API_BASE_URL 格式无效: {cls.API_BASE_URL}")

        # 验证 API_TIMEOUT
        if cls.API_TIMEOUT <= 0:
            errors.append(f"API_TIMEOUT 必须大于 0，当前值: {cls.API_TIMEOUT}")
        if cls.API_TIMEOUT > 300:
            errors.append(f"API_TIMEOUT 过大: {cls.API_TIMEOUT}（最大 300）")

        # 验证前端 URL
        if not cls._is_valid_url(cls.H5_BASE_URL):
            errors.append(f"H5_BASE_URL 格式无效: {cls.H5_BASE_URL}")
        if not cls._is_valid_url(cls.MERCHANT_BASE_URL):
            errors.append(f"MERCHANT_BASE_URL 格式无效: {cls.MERCHANT_BASE_URL}")
        if not cls._is_valid_url(cls.ADMIN_BASE_URL):
            errors.append(f"ADMIN_BASE_URL 格式无效: {cls.ADMIN_BASE_URL}")

        # 验证 BROWSER
        valid_browsers = ["chrome", "firefox", "edge", "safari"]
        if cls.BROWSER not in valid_browsers:
            errors.append(
                f"BROWSER 必须是 {valid_browsers} 之一，当前值: {cls.BROWSER}"
            )

        # 验证窗口尺寸
        if cls.WINDOW_WIDTH <= 0 or cls.WINDOW_WIDTH > 7680:
            errors.append(f"WINDOW_WIDTH 超出有效范围: {cls.WINDOW_WIDTH}")
        if cls.WINDOW_HEIGHT <= 0 or cls.WINDOW_HEIGHT > 4320:
            errors.append(f"WINDOW_HEIGHT 超出有效范围: {cls.WINDOW_HEIGHT}")

        # 验证 WAIT_TIMEOUT
        if cls.WAIT_TIMEOUT <= 0 or cls.WAIT_TIMEOUT > 60:
            errors.append(f"WAIT_TIMEOUT 超出有效范围: {cls.WAIT_TIMEOUT}")

        # 验证 LOG_LEVEL
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(
                f"LOG_LEVEL 必须是 {valid_log_levels} 之一，当前值: {cls.LOG_LEVEL}"
            )

        # 验证 ENVIRONMENT
        valid_environments = ["dev", "test", "staging", "prod"]
        if cls.ENVIRONMENT not in valid_environments:
            errors.append(
                f"ENVIRONMENT 必须是 {valid_environments} 之一，当前值: {cls.ENVIRONMENT}"
            )

        if errors:
            raise ConfigValidationError("\n".join(errors))

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        验证 URL 格式

        接受三种主机格式：
        - localhost
        - IPv4 地址（如 192.168.1.100）
        - 域名（如 api.example.com）

        Args:
            url: URL 字符串

        Returns:
            bool: 是否有效
        """
        url_pattern = re.compile(
            r"^https?://(localhost|(\d{1,3}\.){3}\d{1,3}|([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})(:\d+)?(/.*)?$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(url))

    @classmethod
    def get_log_file_path(cls):
        """获取完整的日志文件路径"""
        return os.path.join(cls.LOG_DIR, cls.LOG_FILE)

    @classmethod
    def print_config(cls):
        """打印当前配置（用于调试）"""
        print("=" * 70)
        print(f"当前配置（环境: {cls.ENVIRONMENT}）:")
        print(f"  TakeoutSystem API: {cls.TAKEOUT_API_URL}")
        print(f"  H5 前端: {cls.H5_BASE_URL}")
        print(f"  商家端: {cls.MERCHANT_BASE_URL}")
        print(f"  管理后台: {cls.ADMIN_BASE_URL}")
        print(f"  浏览器: {cls.BROWSER} | 无头: {cls.HEADLESS}")
        print(f"  日志级别: {cls.LOG_LEVEL} | API 超时: {cls.API_TIMEOUT}s")
        print(f"  Mock 模式: {cls.USE_MOCK}")
        print("=" * 70)


class DevConfig(Config):
    """开发环境配置 - 本地调试"""

    ENVIRONMENT = "dev"
    LOG_LEVEL = "DEBUG"
    HEADLESS = False
    API_TIMEOUT = 60  # 放宽超时，方便断点调试


class TestConfig(Config):
    """测试环境配置 - CI/CD 自动化测试"""

    ENVIRONMENT = "test"
    LOG_LEVEL = "DEBUG"
    HEADLESS = True


class StagingConfig(Config):
    """预发布环境配置"""

    ENVIRONMENT = "staging"
    LOG_LEVEL = "INFO"
    HEADLESS = True


class ProdConfig(Config):
    """生产环境配置 - 只读冒烟测试"""

    ENVIRONMENT = "prod"
    LOG_LEVEL = "WARNING"
    HEADLESS = True
    API_VERIFY_SSL = True


def get_config(env: str = None) -> Config:
    """
    获取配置对象

    Args:
        env: 环境名称 (dev/test/staging/prod)，如果为 None 则从环境变量读取

    Returns:
        Config: 配置对象
    """
    env = env or Config.ENVIRONMENT

    config_map = {
        "dev": DevConfig,
        "test": TestConfig,
        "staging": StagingConfig,
        "prod": ProdConfig,
    }

    config_class = config_map.get(env, TestConfig)
    config_instance = config_class()

    # 验证配置
    config_instance.validate()

    return config_instance


# 默认配置实例（模块级单例）
config = get_config()
