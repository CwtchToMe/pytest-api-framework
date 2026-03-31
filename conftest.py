"""
Pytest 全局配置文件 - 定义全局 fixtures 和钩子

分层设计：
- 本文件（根级）：全局级 fixture（日志、会话管理等）
- test_cases/conftest.py：测试级通用 fixture
- test_cases/api/conftest.py：API 测试专用 fixture
- test_cases/web/conftest.py：Web UI 测试专用 fixture
"""
import pytest
import allure
import logging
from config.config import config
from common.yaml_util import YamlUtil
from common.security import setup_sensitive_data_filter


# ============= 日志配置（全局级） =============
def setup_logging():
    """设置日志系统（带轮转）"""
    # 创建日志目录
    import os
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)
    
    # 文件处理器（带轮转）
    from logging.handlers import RotatingFileHandler
    log_file_path = config.get_log_file_path()
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(config.LOG_LEVEL)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 清除已有的处理器，避免重复
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 添加新处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 设置敏感信息过滤器
    setup_sensitive_data_filter(logger)
    
    return logging.getLogger(__name__)


logger = setup_logging()


# ============= 全局 Fixtures =============

@pytest.fixture(scope="session", autouse=True)
def session_start_end():
    """测试会话开始和结束的生命周期管理"""
    logger.info("=" * 70)
    logger.info(f"测试会话开始 | 环境: {config.ENVIRONMENT}")
    logger.info(f"API URL: {config.API_BASE_URL}")
    logger.info(f"UI URL: {config.UI_BASE_URL}")
    logger.info("=" * 70)
    
    yield
    
    logger.info("=" * 70)
    logger.info("测试会话结束")
    logger.info("=" * 70)


@pytest.fixture(scope="function", autouse=True)
def test_start_end(request):
    """测试开始和结束的生命周期管理"""
    logger.info(f"\n{'='*60}")
    logger.info(f"[开始] {request.node.name}")
    logger.info(f"{'='*60}")
    
    yield
    
    logger.info(f"[完成] {request.node.name}\n")


@pytest.fixture
def test_data():
    """加载测试数据"""
    import os
    data_path = os.path.join(os.path.dirname(__file__), "data/user_login.yaml")
    return YamlUtil().load_yaml(data_path) if os.path.exists(data_path) else {}


# ============= Pytest 钩子 =============

def pytest_configure(config):
    """Pytest 配置函数"""
    logger.info("Pytest 配置初始化完成")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果并记录"""
    outcome = yield
    rep = outcome.get_result()
    
    # 只处理测试执行阶段
    if call.when == "call":
        if rep.failed:
            logger.error(f"❌ 测试失败: {item.name}")
            # 添加到 Allure 报告
            if hasattr(item, "rep_call"):
                item.rep_call = rep
        elif rep.passed:
            logger.info(f"✅ 测试通过: {item.name}")


def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="以无头模式运行浏览器 UI 测试"
    )
    
    parser.addoption(
        "--env",
        action="store",
        default="test",
        choices=["dev", "test", "staging", "prod"],
        help="指定运行环境 (dev/test/staging/prod)"
    )
    
    parser.addoption(
        "--screenshot-on-failure",
        action="store_true",
        default=config.SCREENSHOT_ON_FAILURE,
        help="失败时自动截图"
    )

