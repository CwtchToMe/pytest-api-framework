"""
Pytest 全局配置文件 - 定义全局 fixtures 和钩子

分层设计：
- 本文件（根级）：全局级 fixture（日志、会话管理等）
- test_cases/conftest.py：测试级通用 fixture
- test_cases/api/conftest.py：API 测试专用 fixture
- test_cases/web/conftest.py：Web UI 测试专用 fixture

插件系统集成：
- 核心插件（熔断器、限流器）：强制加载，不可禁用
- 普通插件（日志、指标、缓存）：可选加载，可通过 --disable-plugins 禁用
"""
import pytest
import allure
import logging
from config.config import config
from common.yaml_util import YamlUtil
from common.security import setup_sensitive_data_filter
from common.plugin_system import get_plugin_manager


def setup_logging():
    """设置日志系统（带轮转）"""
    import os
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)
    
    from logging.handlers import RotatingFileHandler
    log_file_path = config.get_log_file_path()
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(config.LOG_LEVEL)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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


@pytest.fixture(scope="session", autouse=True)
def session_start_end():
    """测试会话开始和结束的生命周期管理"""
    logger.info("=" * 70)
    logger.info(f"测试会话开始 | 环境: {config.ENVIRONMENT}")
    logger.info(f"API URL: {config.API_BASE_URL}")
    logger.info(f"UI URL: {config.UI_BASE_URL}")
    
    core_plugins = plugin_manager.get_core_plugins()
    normal_plugins = plugin_manager.get_normal_plugins()
    
    logger.info(f"核心插件（强制）: {[p.name for p in core_plugins]}")
    logger.info(f"普通插件（可选）: {[p.name for p in normal_plugins]}")
    logger.info("=" * 70)
    
    yield
    
    metrics_plugin = plugin_manager.get_plugin('metrics')
    if metrics_plugin:
        logger.info("\n" + "=" * 70)
        logger.info("测试统计摘要:")
        logger.info(metrics_plugin.get_summary())
        logger.info("=" * 70)
    
    circuit_breaker_plugin = plugin_manager.get_plugin('circuit_breaker')
    if circuit_breaker_plugin:
        logger.info(f"熔断器状态: {circuit_breaker_plugin.get_state().value}")
        logger.info(f"熔断器失败次数: {circuit_breaker_plugin.get_failures()}")
    
    rate_limiter_plugin = plugin_manager.get_plugin('rate_limiter')
    if rate_limiter_plugin:
        stats = rate_limiter_plugin.get_stats()
        logger.info(f"限流器统计: {stats['current_calls']}/{stats['max_calls']} (周期: {stats['period']}s)")
    
    logger.info("=" * 70)
    logger.info("测试会话结束")
    logger.info("=" * 70)


@pytest.fixture(scope="function", autouse=True)
def test_start_end(request):
    """测试开始和结束的生命周期管理 - 集成插件钩子"""
    test_name = request.node.name
    
    plugin_manager.execute_hook('before_test', test_name)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"[开始] {test_name}")
    logger.info(f"{'='*60}")
    
    yield
    
    logger.info(f"[完成] {test_name}\n")


@pytest.fixture
def test_data():
    """加载测试数据"""
    import os
    data_path = os.path.join(os.path.dirname(__file__), "data/user_login.yaml")
    return YamlUtil().load_yaml(data_path) if os.path.exists(data_path) else {}


def pytest_configure(config):
    """Pytest 配置函数"""
    logger.info("Pytest 配置初始化完成")
    
    core_plugins = plugin_manager.get_core_plugins()
    normal_plugins = plugin_manager.get_normal_plugins()
    
    logger.info(f"插件系统已启用")
    logger.info(f"  - 核心插件: {[p.name for p in core_plugins]} (不可禁用)")
    logger.info(f"  - 普通插件: {[p.name for p in normal_plugins]} (可通过 --disable-plugins 禁用)")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集测试结果并记录 - 集成插件钩子"""
    outcome = yield
    rep = outcome.get_result()
    
    if call.when == "call":
        test_name = item.name
        
        if rep.failed:
            logger.error(f"❌ 测试失败: {test_name}")
            plugin_manager.execute_hook('on_test_failure', test_name, str(rep.longrepr))
        elif rep.passed:
            logger.info(f"✅ 测试通过: {test_name}")
            plugin_manager.execute_hook('on_test_success', test_name)
        
        plugin_manager.execute_hook('after_test', test_name, rep.outcome)
        
        if hasattr(item, "rep_call"):
            item.rep_call = rep


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
    
    parser.addoption(
        "--disable-plugins",
        action="store_true",
        default=False,
        help="禁用普通插件（核心插件不可禁用）"
    )


def pytest_collection_modifyitems(config, items):
    """测试收集后处理"""
    if config.getoption("--disable-plugins"):
        normal_plugins = plugin_manager.get_normal_plugins()
        for plugin_info in normal_plugins:
            plugin_manager.disable(plugin_info.name)
        logger.info(f"普通插件已禁用: {[p.name for p in normal_plugins]}")
        logger.info("核心插件保持启用（不可禁用）")
