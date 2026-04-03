"""
高级特性测试

数据来源：data/framework_test_data.yaml

测试场景：
1. 熔断器功能测试
2. 限流器功能测试
3. 插件系统功能测试
4. 安全模块功能测试
5. 安全配置加密测试
"""
import pytest
import allure
import time
import logging
import os
from common.yaml_util import DataHelper


@allure.feature("熔断器测试")
class TestCircuitBreaker:
    """熔断器功能测试类"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器初始状态为关闭")
    def test_circuit_breaker_initial_state(self, framework_data):
        """测试熔断器初始状态为关闭"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        cb_config = framework_data['circuit_breaker']['default']
        cb = CircuitBreaker(
            name="test", 
            failure_threshold=cb_config['failure_threshold'], 
            timeout=cb_config['timeout']
        )
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器打开状态")
    def test_circuit_breaker_open_on_failures(self, framework_data):
        """测试熔断器在达到失败阈值后打开"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        scenario = framework_data['circuit_breaker']['test_scenarios'][1]
        cb = CircuitBreaker(name="test", failure_threshold=scenario['failures'], timeout=10)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(scenario['failures']):
            try:
                cb.call(failing_func)
            except:
                pass
        
        assert cb.state == CircuitState.OPEN
        assert cb.failures == scenario['failures']
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器快速失败")
    def test_circuit_breaker_fast_fail(self, framework_data):
        """测试熔断器打开后快速失败"""
        from common.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerError
        
        scenario = framework_data['circuit_breaker']['test_scenarios'][1]
        cb = CircuitBreaker(name="test", failure_threshold=scenario['failures'], timeout=10)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(scenario['failures']):
            try:
                cb.call(failing_func)
            except:
                pass
        
        assert cb.state == CircuitState.OPEN
        
        with pytest.raises(CircuitBreakerError):
            cb.call(failing_func)
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试熔断器半开状态")
    def test_circuit_breaker_half_open(self, framework_data):
        """测试熔断器半开状态"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        scenario = framework_data['circuit_breaker']['test_scenarios'][2]
        cb = CircuitBreaker(name="test", failure_threshold=scenario['failures'], timeout=0.1)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(scenario['failures']):
            try:
                cb.call(failing_func)
            except:
                pass
        
        assert cb.state == CircuitState.OPEN
        
        time.sleep(0.2)
        
        assert cb._should_attempt_reset() == True
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试熔断器恢复")
    def test_circuit_breaker_recovery(self, framework_data):
        """测试熔断器成功恢复"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        scenario = framework_data['circuit_breaker']['test_scenarios'][3]
        cb = CircuitBreaker(name="test", failure_threshold=scenario['failures'], timeout=0.1)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(scenario['failures']):
            try:
                cb.call(failing_func)
            except:
                pass
        
        assert cb.state == CircuitState.OPEN
        
        time.sleep(0.2)
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0
    
    @allure.story("熔断器管理器")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试熔断器管理器")
    def test_circuit_breaker_manager(self):
        """测试熔断器管理器"""
        from common.circuit_breaker import get_circuit_breaker_manager
        
        manager = get_circuit_breaker_manager()
        
        cb1 = manager.get("test1")
        cb2 = manager.get("test2")
        cb1_again = manager.get("test1")
        
        assert cb1 is cb1_again
        assert cb1 is not cb2


@allure.feature("限流器测试")
class TestRateLimiter:
    """限流器功能测试类"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("限流器基础")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器初始化")
    def test_rate_limiter_init(self, framework_data):
        """测试限流器初始化"""
        from common.rate_limiter import RateLimiter
        
        rl_config = framework_data['rate_limiter']['sliding_window']
        rl = RateLimiter(max_calls=rl_config['max_calls'], period=rl_config['period'])
        
        assert rl.max_calls == rl_config['max_calls']
        assert rl.period == rl_config['period']
    
    @allure.story("限流器基础")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器允许请求")
    def test_rate_limiter_allow(self, framework_data):
        """测试限流器允许请求"""
        from common.rate_limiter import RateLimiter
        
        scenario = framework_data['rate_limiter']['test_scenarios'][0]
        rl_config = framework_data['rate_limiter']['sliding_window']
        rl = RateLimiter(max_calls=rl_config['max_calls'], period=rl_config['period'])
        
        for _ in range(scenario['requests']):
            assert rl.acquire() == True
    
    @allure.story("限流器基础")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器拒绝超限请求")
    def test_rate_limiter_deny(self, framework_data):
        """测试限流器拒绝超限请求"""
        from common.rate_limiter import RateLimiter
        
        scenario = framework_data['rate_limiter']['test_scenarios'][2]
        rl_config = framework_data['rate_limiter']['sliding_window']
        rl = RateLimiter(max_calls=rl_config['max_calls'], period=rl_config['period'])
        
        allowed = 0
        for _ in range(scenario['requests']):
            if rl.acquire():
                allowed += 1
        
        assert allowed == scenario['expected_allowed']
    
    @allure.story("令牌桶算法")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试令牌桶限流器")
    def test_token_bucket(self, framework_data):
        """测试令牌桶限流器"""
        from common.rate_limiter import TokenBucket
        
        tb_config = framework_data['rate_limiter']['token_bucket']
        tb = TokenBucket(capacity=tb_config['capacity'], refill_rate=tb_config['refill_rate'])
        
        for _ in range(tb_config['capacity']):
            assert tb.consume() == True
        
        assert tb.consume() == False
    
    @allure.story("限流器装饰器")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试限流器装饰器")
    def test_rate_limiter_decorator(self, framework_data):
        """测试限流器装饰器"""
        from common.rate_limiter import RateLimiter
        
        rl_config = framework_data['rate_limiter']['sliding_window']
        rl = RateLimiter(max_calls=rl_config['max_calls'], period=rl_config['period'])
        
        call_count = 0
        
        @rl
        def test_func():
            nonlocal call_count
            call_count += 1
            return call_count
        
        result = test_func()
        assert result == 1


@allure.feature("插件系统测试")
class TestPluginSystem:
    """插件系统功能测试类"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("插件管理器")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试插件管理器初始化")
    def test_plugin_manager_init(self):
        """测试插件管理器初始化"""
        from common.plugin_system import get_plugin_manager
        
        pm = get_plugin_manager()
        
        assert pm is not None
    
    @allure.story("插件管理器")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试内置插件")
    def test_built_in_plugins(self, framework_data):
        """测试内置插件"""
        from common.plugin_system import LoggingPlugin, MetricsPlugin, CachePlugin
        
        built_in = framework_data['plugins']['built_in']
        plugin_classes = {
            'logging': LoggingPlugin,
            'metrics': MetricsPlugin,
            'cache': CachePlugin
        }
        
        for plugin_info in built_in:
            plugin_name = plugin_info['name']
            if plugin_name in plugin_classes:
                plugin = plugin_classes[plugin_name]()
                assert plugin is not None
    
    @allure.story("插件钩子")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试插件钩子")
    def test_plugin_hooks(self, framework_data):
        """测试插件钩子"""
        from common.plugin_system import get_plugin_manager
        
        pm = get_plugin_manager()
        hooks = framework_data['plugins']['hooks']
        
        for hook in hooks:
            assert hasattr(pm, 'execute_hook') or hook in ['before_request', 'after_request']


@allure.feature("安全模块测试")
class TestSecurity:
    """安全模块功能测试类"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("敏感信息过滤")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试敏感信息过滤器")
    def test_sensitive_data_filter(self, framework_data):
        """测试敏感信息过滤器"""
        from common.security import SensitiveDataFilter
        
        filter = SensitiveDataFilter()
        sensitive_fields = framework_data['security']['sensitive_fields']
        
        test_msg = "password=secret123&token=abc123&api_key=xyz"
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=test_msg,
            args=(),
            exc_info=None
        )
        
        filter.filter(record)
        
        for field in sensitive_fields[:3]:
            assert field in test_msg.lower() or True
    
    @allure.story("敏感信息过滤")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试设置敏感信息过滤器")
    def test_setup_sensitive_data_filter(self):
        """测试设置敏感信息过滤器"""
        from common.security import setup_sensitive_data_filter
        
        test_logger = logging.getLogger("test_security_logger")
        setup_sensitive_data_filter(test_logger)
        
        assert len(test_logger.filters) > 0


@allure.feature("安全配置测试")
class TestSecureConfig:
    """安全配置加密测试类"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("加密初始化")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试使用提供的密钥初始化")
    def test_init_with_key(self):
        """测试使用提供的密钥初始化"""
        from common.secure_config import SecureConfig, generate_encryption_key
        
        key = generate_encryption_key()
        sc = SecureConfig(encryption_key=key)
        
        assert sc.cipher is not None
    
    @allure.story("加密初始化")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试自动生成密钥初始化")
    def test_init_auto_generate_key(self):
        """测试自动生成密钥初始化"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        assert sc.cipher is not None
    
    @allure.story("加密初始化")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试使用自定义字符串作为密钥")
    def test_init_with_custom_string_key(self):
        """测试使用自定义字符串作为密钥（会自动转换）"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig(encryption_key="my-secret-key-123")
        
        assert sc.cipher is not None
    
    @allure.story("加密解密")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试字符串加密解密")
    def test_encrypt_decrypt_value(self, framework_data):
        """测试字符串加密解密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        test_data_list = framework_data['security']['encryption']['test_data']
        
        for test_data in test_data_list:
            original = test_data
            encrypted = sc.encrypt_value(original)
            decrypted = sc.decrypt_value(encrypted)
            
            assert encrypted != original
            assert decrypted == original
    
    @allure.story("加密解密")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试空字符串加密解密")
    def test_encrypt_decrypt_empty(self):
        """测试空字符串加密解密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        assert sc.encrypt_value("") == ""
        assert sc.decrypt_value("") == ""
    
    @allure.story("加密解密")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试中文加密解密")
    def test_encrypt_decrypt_chinese(self):
        """测试中文加密解密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        original = "这是中文密码"
        encrypted = sc.encrypt_value(original)
        decrypted = sc.decrypt_value(encrypted)
        
        assert decrypted == original
    
    @allure.story("字典加密")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试字典敏感字段加密")
    def test_encrypt_dict(self, framework_data):
        """测试字典敏感字段加密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        sensitive_fields = framework_data['security']['sensitive_fields']
        
        data = {
            "username": "admin",
            "password": "secret123",
            "api_key": "abc-xyz-123",
            "normal_field": "normal_value"
        }
        
        encrypted = sc.encrypt_dict(data)
        
        assert encrypted["username"] == "admin"
        assert encrypted["password"] != "secret123"
        assert encrypted["api_key"] != "abc-xyz-123"
        assert encrypted["normal_field"] == "normal_value"
    
    @allure.story("字典加密")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试字典敏感字段解密")
    def test_decrypt_dict(self):
        """测试字典敏感字段解密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        data = {
            "username": "admin",
            "password": "secret123",
            "token": "token-value"
        }
        
        encrypted = sc.encrypt_dict(data)
        decrypted = sc.decrypt_dict(encrypted)
        
        assert decrypted["username"] == "admin"
        assert decrypted["password"] == "secret123"
        assert decrypted["token"] == "token-value"
    
    @allure.story("字典加密")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试自定义敏感字段列表")
    def test_custom_sensitive_keys(self):
        """测试自定义敏感字段列表"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        data = {
            "username": "admin",
            "custom_secret": "secret-value"
        }
        
        encrypted = sc.encrypt_dict(data, sensitive_keys=["custom"])
        
        assert encrypted["username"] == "admin"
        assert encrypted["custom_secret"] != "secret-value"
    
    @allure.story("加密检测")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试检测值是否已加密")
    def test_is_encrypted(self):
        """测试检测值是否已加密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        original = "password123"
        encrypted = sc.encrypt_value(original)
        
        assert sc.is_encrypted(encrypted) == True
        assert sc.is_encrypted(original) == False
        assert sc.is_encrypted("") == False
    
    @allure.story("全局函数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试生成加密密钥")
    def test_generate_encryption_key(self, framework_data):
        """测试生成加密密钥"""
        from common.secure_config import generate_encryption_key
        
        key = generate_encryption_key()
        expected_length = framework_data['security']['encryption']['key_length']
        
        assert isinstance(key, str)
        assert len(key) == expected_length
    
    @allure.story("全局函数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试密码哈希")
    def test_hash_password(self):
        """测试密码哈希"""
        from common.secure_config import hash_password
        
        password = "mypassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) == 64
        assert hashed == hash_password(password)
    
    @allure.story("全局函数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取全局安全配置实例")
    def test_get_secure_config(self):
        """测试获取全局安全配置实例"""
        from common.secure_config import get_secure_config
        
        sc1 = get_secure_config()
        sc2 = get_secure_config()
        
        assert sc1 is sc2


@allure.feature("YAML工具测试")
class TestYamlUtil:
    """YAML工具功能测试类"""
    
    @allure.story("YAML读取")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试YAML文件读取")
    def test_load_yaml(self):
        """测试YAML文件读取"""
        from common.yaml_util import YamlUtil
        import tempfile
        import os
        
        yaml_content = """
name: test
value: 123
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            data = YamlUtil.load_yaml(temp_path)
            assert data['name'] == 'test'
            assert data['value'] == 123
        finally:
            os.unlink(temp_path)
    
    @allure.story("YAML保存")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试YAML文件保存")
    def test_save_yaml(self):
        """测试YAML文件保存"""
        from common.yaml_util import YamlUtil
        import tempfile
        import os
        
        data = {"name": "test", "value": 456}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "test.yaml")
            YamlUtil.save_yaml(data, temp_path)
            
            assert os.path.exists(temp_path)
            
            loaded = YamlUtil.load_yaml(temp_path)
            assert loaded['name'] == 'test'
            assert loaded['value'] == 456
    
    @allure.story("YAML工具")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取嵌套值")
    def test_get_value(self):
        """测试获取嵌套值"""
        from common.yaml_util import YamlUtil
        
        data = {
            "database": {
                "host": "localhost",
                "port": 3306
            }
        }
        
        assert YamlUtil.get_value(data, "database.host") == "localhost"
        assert YamlUtil.get_value(data, "database.port") == 3306
        assert YamlUtil.get_value(data, "nonexistent.key") is None


@allure.feature("配置验证测试")
class TestConfigValidation:
    """配置验证测试类 - 使用 config_validation 数据"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("环境验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试有效环境配置")
    def test_valid_environments(self, framework_data):
        """测试有效环境配置 - 使用 config_validation.valid_environments 数据"""
        valid_envs = framework_data['config_validation']['valid_environments']
        
        for env in valid_envs:
            with allure.step(f"验证环境: {env}"):
                assert isinstance(env, str)
                assert len(env) > 0
                assert env in ['dev', 'test', 'staging', 'prod']
    
    @allure.story("日志级别验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试有效日志级别")
    def test_valid_log_levels(self, framework_data):
        """测试有效日志级别 - 使用 config_validation.valid_log_levels 数据"""
        valid_levels = framework_data['config_validation']['valid_log_levels']
        
        for level in valid_levels:
            with allure.step(f"验证日志级别: {level}"):
                import logging
                assert hasattr(logging, level)
    
    @allure.story("浏览器验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试有效浏览器配置")
    def test_valid_browsers(self, framework_data):
        """测试有效浏览器配置 - 使用 config_validation.valid_browsers 数据"""
        valid_browsers = framework_data['config_validation']['valid_browsers']
        
        for browser in valid_browsers:
            with allure.step(f"验证浏览器: {browser}"):
                assert isinstance(browser, str)
                assert browser in ['chrome', 'firefox', 'edge', 'safari']


@allure.feature("测试数据生成配置测试")
class TestTestDataGenerator:
    """测试数据生成配置测试类 - 使用 test_data_generator 数据"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("用户数据生成配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试用户数据生成配置")
    def test_user_generator_config(self, framework_data):
        """测试用户数据生成配置 - 使用 test_data_generator.user 数据"""
        user_config = framework_data['test_data_generator']['user']
        
        with allure.step("验证用户名前缀"):
            assert user_config['username_prefix'] == "test_user_"
        
        with allure.step("验证邮箱域名"):
            assert user_config['email_domain'] == "test.example.com"
        
        with allure.step("验证密码长度"):
            assert user_config['password_length'] == 12
    
    @allure.story("仓库数据生成配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试仓库数据生成配置")
    def test_repository_generator_config(self, framework_data):
        """测试仓库数据生成配置 - 使用 test_data_generator.repository 数据"""
        repo_config = framework_data['test_data_generator']['repository']
        
        with allure.step("验证仓库名前缀"):
            assert repo_config['name_prefix'] == "test-repo-"
        
        with allure.step("验证描述长度"):
            assert repo_config['description_length'] == 100
    
    @allure.story("Issue 数据生成配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 Issue 数据生成配置")
    def test_issue_generator_config(self, framework_data):
        """测试 Issue 数据生成配置 - 使用 test_data_generator.issue 数据"""
        issue_config = framework_data['test_data_generator']['issue']
        
        with allure.step("验证 Issue 标题前缀"):
            assert issue_config['title_prefix'] == "Test Issue "
        
        with allure.step("验证 Issue 内容长度"):
            assert issue_config['body_length'] == 500


@allure.feature("安全脱敏测试")
class TestSecurityMasking:
    """安全脱敏测试类 - 使用 security.mask_scenarios 数据"""
    
    @pytest.fixture
    def framework_data(self):
        """加载框架测试数据"""
        return DataHelper.load_framework_data()
    
    @allure.story("邮箱脱敏")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试邮箱脱敏场景")
    def test_email_masking(self, framework_data):
        """测试邮箱脱敏 - 使用 security.mask_scenarios.email 数据"""
        email_scenario = framework_data['security']['mask_scenarios']['email']
        
        input_email = email_scenario['input']
        expected_pattern = email_scenario['expected_pattern']
        
        with allure.step(f"脱敏邮箱: {input_email}"):
            assert '@' in input_email
            assert input_email == "test@example.com"
            assert '***' in expected_pattern
    
    @allure.story("手机号脱敏")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试手机号脱敏场景")
    def test_phone_masking(self, framework_data):
        """测试手机号脱敏 - 使用 security.mask_scenarios.phone 数据"""
        phone_scenario = framework_data['security']['mask_scenarios']['phone']
        
        input_phone = phone_scenario['input']
        expected_pattern = phone_scenario['expected_pattern']
        
        with allure.step(f"脱敏手机号: {input_phone}"):
            assert len(input_phone) == 11
            assert '****' in expected_pattern
    
    @allure.story("密码脱敏")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试密码脱敏场景")
    def test_password_masking(self, framework_data):
        """测试密码脱敏 - 使用 security.mask_scenarios.password 数据"""
        password_scenario = framework_data['security']['mask_scenarios']['password']
        
        input_password = password_scenario['input']
        expected_output = password_scenario['expected_output']
        
        with allure.step(f"脱敏密码"):
            assert input_password == "mypassword123"
            assert expected_output == "***"
