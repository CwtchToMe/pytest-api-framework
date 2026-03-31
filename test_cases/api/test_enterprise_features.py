"""
安全模块单元测试

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


@allure.feature("熔断器测试")
class TestCircuitBreaker:
    """熔断器功能测试类"""
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器初始状态为关闭")
    def test_circuit_breaker_initial_state(self):
        """测试熔断器初始状态为关闭"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        cb = CircuitBreaker(name="test", failure_threshold=3, timeout=10)
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器打开状态")
    def test_circuit_breaker_open_on_failures(self):
        """测试熔断器在达到失败阈值后打开"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        cb = CircuitBreaker(name="test", failure_threshold=3, timeout=10)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(3):
            try:
                cb.call(failing_func)
            except:
                pass
        
        assert cb.state == CircuitState.OPEN
        assert cb.failures == 3
    
    @allure.story("熔断器状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器快速失败")
    def test_circuit_breaker_fast_fail(self):
        """测试熔断器打开后快速失败"""
        from common.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerError
        
        cb = CircuitBreaker(name="test", failure_threshold=2, timeout=10)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(2):
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
    def test_circuit_breaker_half_open(self):
        """测试熔断器半开状态"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        cb = CircuitBreaker(name="test", failure_threshold=2, timeout=0.1)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(2):
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
    def test_circuit_breaker_recovery(self):
        """测试熔断器成功恢复"""
        from common.circuit_breaker import CircuitBreaker, CircuitState
        
        cb = CircuitBreaker(name="test", failure_threshold=2, timeout=0.1)
        
        def failing_func():
            raise Exception("Test error")
        
        for _ in range(2):
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
    
    @allure.story("限流器基础")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器初始化")
    def test_rate_limiter_init(self):
        """测试限流器初始化"""
        from common.rate_limiter import RateLimiter
        
        rl = RateLimiter(max_calls=10, period=60)
        
        assert rl.max_calls == 10
        assert rl.period == 60
    
    @allure.story("限流器基础")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器允许请求")
    def test_rate_limiter_allow(self):
        """测试限流器允许请求"""
        from common.rate_limiter import RateLimiter
        
        rl = RateLimiter(max_calls=5, period=60)
        
        for _ in range(5):
            assert rl.acquire() == True
    
    @allure.story("限流器基础")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器拒绝超限请求")
    def test_rate_limiter_deny(self):
        """测试限流器拒绝超限请求"""
        from common.rate_limiter import RateLimiter
        
        rl = RateLimiter(max_calls=3, period=60)
        
        assert rl.acquire() == True
        assert rl.acquire() == True
        assert rl.acquire() == True
        assert rl.acquire() == False
    
    @allure.story("令牌桶算法")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试令牌桶限流器")
    def test_token_bucket(self):
        """测试令牌桶限流器"""
        from common.rate_limiter import TokenBucket
        
        tb = TokenBucket(capacity=5, refill_rate=1)
        
        for _ in range(5):
            assert tb.consume() == True
        
        assert tb.consume() == False
    
    @allure.story("限流器装饰器")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试限流器装饰器")
    def test_rate_limiter_decorator(self):
        """测试限流器装饰器"""
        from common.rate_limiter import RateLimiter
        
        rl = RateLimiter(max_calls=3, period=60)
        
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
    @allure.title("测试日志插件")
    def test_logging_plugin(self):
        """测试日志插件"""
        from common.plugin_system import LoggingPlugin
        
        plugin = LoggingPlugin()
        
        assert plugin is not None


@allure.feature("安全模块测试")
class TestSecurity:
    """安全模块功能测试类"""
    
    @allure.story("敏感信息过滤")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试敏感信息过滤器")
    def test_sensitive_data_filter(self):
        """测试敏感信息过滤器"""
        from common.security import SensitiveDataFilter
        
        filter = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="password=secret123&token=abc123",
            args=(),
            exc_info=None
        )
        
        filter.filter(record)
        
        assert "secret123" not in record.msg
        assert "abc123" not in record.msg
    
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
    def test_encrypt_decrypt_value(self):
        """测试字符串加密解密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
        original = "my-secret-password"
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
    def test_encrypt_dict(self):
        """测试字典敏感字段加密"""
        from common.secure_config import SecureConfig
        
        sc = SecureConfig()
        
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
    def test_generate_encryption_key(self):
        """测试生成加密密钥"""
        from common.secure_config import generate_encryption_key
        
        key = generate_encryption_key()
        
        assert isinstance(key, str)
        assert len(key) == 44  # Fernet key is 44 chars
    
    @allure.story("全局函数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试密码哈希")
    def test_hash_password(self):
        """测试密码哈希"""
        from common.secure_config import hash_password
        
        password = "mypassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) == 64  # SHA256 produces 64 hex chars
        assert hashed == hash_password(password)  # Same input = same hash
    
    @allure.story("全局函数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取全局安全配置实例")
    def test_get_secure_config(self):
        """测试获取全局安全配置实例"""
        from common.secure_config import get_secure_config, _global_secure_config
        
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
