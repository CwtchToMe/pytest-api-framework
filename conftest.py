"""
Pytest 全局配置文件 - 定义全局 fixtures 和钩子

分层设计：
- 本文件（根级）：全局级 fixture（日志、会话管理等）
- test_cases/web/conftest.py：Web UI 测试专用 fixture（WebDriver）

插件系统：
- 日志插件（LoggingPlugin）：记录请求和测试日志
- Allure 附件插件（AllurePlugin）：自动附加 HTTP 请求/响应到 Allure 报告
- 可通过 --disable-plugins 禁用普通插件
"""

import logging

import allure
import pytest

from common.mock_util import MockHelper, is_mock_mode
from common.plugins import get_plugin_manager
from common.security import setup_sensitive_data_filter
from common.yaml_util import YamlUtil
from config.config import config


def setup_logging():
    """设置日志系统（带轮转）"""
    import os

    os.makedirs(config.LOG_DIR, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    from logging.handlers import RotatingFileHandler

    log_file_path = config.get_log_file_path()
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(config.LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    setup_sensitive_data_filter(logger)

    return logging.getLogger(__name__)


logger = setup_logging()

plugin_manager = get_plugin_manager()


# ============================================================
# CLI 参数注册
# ============================================================


def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--mock",
        action="store_true",
        default=None,
        help="启用 Mock 模式（覆盖环境变量 USE_MOCK）",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=None,
        help="以无头模式运行浏览器 UI 测试",
    )
    parser.addoption(
        "--env",
        action="store",
        default=None,
        choices=["dev", "test", "staging", "prod"],
        help="指定运行环境 (dev/test/staging/prod)",
    )
    parser.addoption(
        "--screenshot-on-failure",
        action="store_true",
        default=None,
        help="失败时自动截图",
    )
    parser.addoption(
        "--disable-plugins", action="store_true", default=False, help="禁用插件"
    )


# ============================================================
# 测试收集后处理
# ============================================================


def pytest_collection_modifyitems(config, items):
    """测试收集后处理"""
    # 处理 --disable-plugins
    if config.getoption("--disable-plugins"):
        for plugin_info in plugin_manager.get_all_plugins():
            plugin_manager.disable(plugin_info.name)
        logger.info(f"插件已禁用: {[p.name for p in plugin_manager.get_all_plugins()]}")

    # 处理 --mock 参数
    mock_option = config.getoption("--mock")
    if mock_option is not None:
        from config.config import Config

        Config.USE_MOCK = mock_option
        Config.USE_REAL_API = not mock_option
        logger.info(
            f"命令行参数 --mock={mock_option} 已覆盖配置，当前模式: {'Mock' if mock_option else '真实 API'}"
        )

    # 处理 --headless 参数
    headless_option = config.getoption("--headless")
    if headless_option is not None:
        from config.config import Config

        Config.HEADLESS = headless_option
        logger.info(f"命令行参数 --headless={headless_option} 已覆盖配置")

    # 处理 --env 参数
    env_option = config.getoption("--env")
    if env_option is not None:
        from config.config import Config

        Config.ENVIRONMENT = env_option
        logger.info(f"命令行参数 --env={env_option} 已设置")


# ============================================================
# 生命周期 Fixture
# ============================================================


@pytest.fixture(scope="session", autouse=True)
def session_start_end():
    """测试会话开始和结束的生命周期管理"""
    logger.info("=" * 70)
    logger.info(f"测试会话开始 | 环境: {config.ENVIRONMENT}")
    logger.info(f"API URL: {config.API_BASE_URL}")
    logger.info(f"H5 URL: {config.H5_BASE_URL}")

    registered_plugins = plugin_manager.get_all_plugins()
    logger.info(f"已注册插件: {[p.name for p in registered_plugins]}")
    logger.info(f"Mock 模式: {config.USE_MOCK}")
    logger.info(f"浏览器无头模式: {config.HEADLESS}")
    logger.info("=" * 70)

    # 真实模式：检查后端是否可用
    if not config.USE_MOCK:
        try:
            import requests

            resp = requests.get(f"{config.API_BASE_URL}/api/health", timeout=5)
            if resp.status_code == 200:
                logger.info(f"✅ 后端服务可用: {config.API_BASE_URL}")
            else:
                logger.warning(f"⚠️ 后端返回异常: {resp.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ 后端不可用: {e}（真实模式测试可能失败）")

    yield

    logger.info("=" * 70)
    logger.info("测试会话结束")
    logger.info("=" * 70)


@pytest.fixture(scope="function", autouse=True)
def test_start_end(request):
    """测试开始和结束的生命周期管理 - 集成插件钩子"""
    test_name = request.node.name

    plugin_manager.execute_hook("before_test", test_name)

    logger.info(f"\n{'='*60}")
    logger.info(f"[开始] {test_name}")
    logger.info(f"{'='*60}")

    yield

    logger.info(f"[完成] {test_name}\n")


# ============================================================
# 测试结果报告钩子
# ============================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果并记录 - 集成插件钩子"""
    outcome = yield
    rep = outcome.get_result()

    if call.when == "call":
        test_name = item.name

        if rep.failed:
            logger.error(f"❌ 测试失败: {test_name}")
            plugin_manager.execute_hook("on_test_failure", test_name, str(rep.longrepr))
        elif rep.passed:
            logger.info(f"✅ 测试通过: {test_name}")
            plugin_manager.execute_hook("on_test_success", test_name)

        plugin_manager.execute_hook("after_test", test_name, rep.outcome)

        if hasattr(item, "rep_call"):
            item.rep_call = rep


# ============================================================
# Session 级别的共享 Fixture
# ============================================================


@pytest.fixture(scope="session")
def http_session():
    """
    Session 级别的 HTTP 客户端，维护连接池。
    所有 API 对象共享此 session，减少重复创建开销。
    """
    from common.base_requests import BaseRequests

    session = BaseRequests()
    yield session
    session.close()


# ============================================================
# 公共 Fixture
# ============================================================


@pytest.fixture
def mock_helper():
    """Mock 辅助工具 fixture

    测试需要使用 Mock 时，显式调用此 fixture：

        def test_something(mock_helper):
            if mock_helper.use_mock:
                resp = mock_helper.create_mock_response(...)
                with mock_helper.mock_request(api_obj, "post", resp):
                    result = api_obj.some_method()
    """
    return MockHelper()


@pytest.fixture
def test_data():
    """加载 API 测试数据"""
    from common.yaml_util import DataHelper

    return DataHelper.load_api_data()


@pytest.fixture
def web_data():
    """加载 Web 测试数据"""
    from common.yaml_util import DataHelper

    return DataHelper.load_web_data()


def pytest_configure(config):
    """Pytest 配置函数"""
    logger.info("Pytest 配置初始化完成")

    registered_plugins = plugin_manager.get_all_plugins()
    logger.info("插件系统已启用")
    logger.info(f"  - 已注册插件: {[p.name for p in registered_plugins]}")
