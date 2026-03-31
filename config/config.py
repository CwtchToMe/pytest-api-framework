"""
项目配置管理模块 - 支持多环境配置和 .env 文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
import re
from common.secure_config import get_secure_config, SecureConfig


# 加载 .env 文件
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class Config:
    """基础配置类 - 可被子类继承"""
    
    # 安全配置管理器
    _secure_config: Optional[SecureConfig] = None
    
    @classmethod
    def get_secure_config(cls) -> SecureConfig:
        """获取安全配置实例"""
        if cls._secure_config is None:
            encryption_key = os.getenv('ENCRYPTION_KEY')
            cls._secure_config = get_secure_config(encryption_key)
        return cls._secure_config
    
    @classmethod
    def get_sensitive_value(cls, value: str, encrypted: bool = False) -> str:
        """
        获取敏感配置值（自动处理加密/解密）
        
        Args:
            value: 配置值
            encrypted: 值是否已加密
            
        Returns:
            str: 解密后的值
        """
        if not value:
            return ""
        
        secure_config = cls.get_secure_config()
        
        if encrypted:
            try:
                return secure_config.decrypt_value(value)
            except:
                # 如果解密失败，返回原值
                return value
        else:
            return value
    
    @classmethod
    def encrypt_sensitive_value(cls, value: str) -> str:
        """
        加密敏感配置值
        
        Args:
            value: 要加密的值
            
        Returns:
            str: 加密后的值
        """
        if not value:
            return ""
        
        secure_config = cls.get_secure_config()
        return secure_config.encrypt_value(value)
    
    # ========== 环境选择 ==========
    ENVIRONMENT = os.getenv("ENV", "test")
    
    # ========== API 配置 ==========
    # GitHub API 配置（主要测试目标）
    GITHUB_API_URL = os.getenv(
        "GITHUB_API_URL",
        "https://api.github.com"
    )
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # 从环境变量获取
    
    # GitHub API 频率限制配置
    GITHUB_RATE_LIMIT = int(os.getenv("GITHUB_RATE_LIMIT", "5000"))  # 每小时 5000 次
    GITHUB_RATE_LIMIT_WINDOW = int(os.getenv("GITHUB_RATE_LIMIT_WINDOW", "3600"))  # 1 小时
    
    # 通用 API 配置
    API_BASE_URL = GITHUB_API_URL  # 默认使用 GitHub API
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    API_VERIFY_SSL = os.getenv("API_VERIFY_SSL", "true").lower() == "true"
    
    # 企业级特性配置
    ENABLE_CIRCUIT_BREAKER = os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
    ENABLE_RATE_LIMITER = os.getenv("ENABLE_RATE_LIMITER", "true").lower() == "true"
    ENABLE_PLUGINS = os.getenv("ENABLE_PLUGINS", "true").lower() == "true"
    
    # ========== UI 配置 ==========
    UI_BASE_URL = os.getenv(
        "UI_BASE_URL",
        "https://petstore.octoperf.com"
    )
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1920"))
    WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "1080"))
    WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "10"))
    
    # ========== 日志配置 ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_FILE = os.getenv("LOG_FILE", "test.log")
    
    # 创建日志目录
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # ========== 报告配置 ==========
    REPORT_DIR = os.getenv("REPORT_DIR", "reports")
    ALLURE_DIR = os.getenv("ALLURE_DIR", "reports/allure_results")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    SCREENSHOT_ON_FAILURE = os.getenv(
        "SCREENSHOT_ON_FAILURE",
        "true"
    ).lower() == "true"
    
    # 创建必要的目录
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(ALLURE_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    # ========== 测试数据 ==========
    # GitHub 测试数据
    TEST_GITHUB_USER = os.getenv("TEST_GITHUB_USER", "octocat")  # GitHub 官方测试账号
    TEST_GITHUB_REPO = os.getenv("TEST_GITHUB_REPO", "Hello-World")  # GitHub 官方测试仓库
    
    # 测试用户数据（用于创建 Issue 等操作）
    TEST_USER_DATA = {
        "username": "testuser_001",
        "firstName": "Test",
        "lastName": "User",
        "email": "testuser@example.com",
        "password": "test123"
    }
    
    @classmethod
    def validate(cls) -> None:
        """
        验证配置的有效性
        
        Raises:
            ConfigValidationError: 如果配置无效
        """
        errors = []
        
        # 验证 API_BASE_URL
        if not cls._is_valid_url(cls.API_BASE_URL):
            errors.append(f"API_BASE_URL 格式无效: {cls.API_BASE_URL}")
        
        # 验证 API_TIMEOUT
        if cls.API_TIMEOUT <= 0:
            errors.append(f"API_TIMEOUT 必须大于 0: {cls.API_TIMEOUT}")
        if cls.API_TIMEOUT > 300:
            errors.append(f"API_TIMEOUT 过大: {cls.API_TIMEOUT}")
        
        # 验证 UI_BASE_URL
        if not cls._is_valid_url(cls.UI_BASE_URL):
            errors.append(f"UI_BASE_URL 格式无效: {cls.UI_BASE_URL}")
        
        # 验证 BROWSER
        valid_browsers = ["chrome", "firefox", "edge", "safari"]
        if cls.BROWSER not in valid_browsers:
            errors.append(f"BROWSER 必须是 {valid_browsers} 之一: {cls.BROWSER}")
        
        # 验证 WINDOW_WIDTH 和 WINDOW_HEIGHT
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
            errors.append(f"LOG_LEVEL 必须是 {valid_log_levels} 之一: {cls.LOG_LEVEL}")
        
        # 验证 ENVIRONMENT
        valid_environments = ["dev", "test", "staging", "prod"]
        if cls.ENVIRONMENT not in valid_environments:
            errors.append(f"ENVIRONMENT 必须是 {valid_environments} 之一: {cls.ENVIRONMENT}")
        
        if errors:
            raise ConfigValidationError("\n".join(errors))
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        验证 URL 格式
        
        Args:
            url: URL 字符串
            
        Returns:
            bool: 是否有效
        """
        url_pattern = re.compile(
            r'^(https?:\/\/)?'  # http:// or https://
            r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'  # domain
            r'(:\d+)?'  # optional port
            r'(\/.*)?$',  # optional path
            re.IGNORECASE
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
        print("当前配置:")
        print(f"  环境: {cls.ENVIRONMENT}")
        print(f"  API URL: {cls.API_BASE_URL}")
        print(f"  UI URL: {cls.UI_BASE_URL}")
        print(f"  浏览器: {cls.BROWSER}")
        print(f"  日志级别: {cls.LOG_LEVEL}")
        print(f"  API 超时: {cls.API_TIMEOUT}s")
        print("=" * 70)


class DevConfig(Config):
    """开发环境配置"""
    ENVIRONMENT = "dev"
    LOG_LEVEL = "DEBUG"
    HEADLESS = False
    API_TIMEOUT = 60


class TestConfig(Config):
    """测试环境配置"""
    ENVIRONMENT = "test"
    LOG_LEVEL = "DEBUG"
    HEADLESS = True


class StagingConfig(Config):
    """预发布环境配置"""
    ENVIRONMENT = "staging"
    LOG_LEVEL = "INFO"
    HEADLESS = True


class ProdConfig(Config):
    """生产环境配置"""
    ENVIRONMENT = "prod"
    LOG_LEVEL = "WARNING"
    HEADLESS = True
    API_VERIFY_SSL = True


def get_config(env: str = None) -> Config:
    """
    获取配置对象
    
    Args:
        env: 环境名称 (dev/test/staging/prod)，如果为 None 则从 .env 文件读取
        
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
    try:
        config_instance.validate()
    except ConfigValidationError as e:
        print(f"配置验证失败: {e}")
        raise
    
    return config_instance


# 默认配置实例
config = get_config()

