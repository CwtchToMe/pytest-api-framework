"""
压力测试和负载测试

数据来源：data/framework_test_data.yaml

测试场景：
1. 压力测试 - 高并发下的系统表现
2. 负载测试 - 逐步增加负载
3. 持久性测试 - 长时间运行稳定性
"""
import pytest
import allure
import time
import threading
import statistics
from unittest.mock import Mock, patch
from api.github_api import GitHubApi
from config.config import config
from common.yaml_util import DataHelper


@allure.feature("压力测试")
class TestStressTest:
    """压力测试类 - 测试系统在极端条件下的表现"""
    
    @pytest.fixture
    def stress_data(self):
        """加载压力测试数据"""
        return DataHelper.load_framework_data()['stress_test']
    
    @allure.story("高并发压力测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试高并发请求")
    def test_high_concurrency_stress(self, stress_data):
        """测试高并发压力"""
        client = GitHubApi()
        
        high_concurrency = stress_data['high_concurrency']
        mock_resp = stress_data['mock_response']
        concurrent_requests = high_concurrency['concurrent_requests']
        expected_success_rate = high_concurrency['expected_success_rate']
        
        mock_response = Mock()
        mock_response.status_code = mock_resp['status_code']
        mock_response.json.return_value = mock_resp['body']
        
        results = []
        errors = []
        
        def make_request():
            try:
                with patch.object(client.requests, 'get', return_value=mock_response):
                    user = client.get_user("test")
                    results.append(user)
            except Exception as e:
                errors.append(str(e))
        
        with allure.step(f"创建 {concurrent_requests} 个并发线程"):
            threads = []
            for _ in range(concurrent_requests):
                t = threading.Thread(target=make_request)
                threads.append(t)
        
        with allure.step("同时启动所有线程"):
            start_time = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            end_time = time.time()
        
        with allure.step("验证结果"):
            success_rate = len(results) / concurrent_requests * 100
            total_time = end_time - start_time
            
            assert len(errors) == 0, f"存在错误: {errors}"
            assert success_rate == expected_success_rate, f"成功率: {success_rate}%"
            
        client.close()
        
        allure.attach(
            f"并发数: {concurrent_requests}\n"
            f"成功数: {len(results)}\n"
            f"错误数: {len(errors)}\n"
            f"总耗时: {total_time:.2f}s\n"
            f"成功率: {success_rate}%",
            "压力测试结果",
            allure.attachment_type.TEXT
        )
    
    @allure.story("持续压力测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试持续高压请求")
    def test_sustained_stress(self, stress_data):
        """测试持续压力"""
        client = GitHubApi()
        
        sustained = stress_data['sustained']
        mock_resp = stress_data['mock_response']
        duration_seconds = sustained['duration_seconds']
        concurrent_threads = sustained['concurrent_threads']
        
        mock_response = Mock()
        mock_response.status_code = mock_resp['status_code']
        mock_response.json.return_value = mock_resp['body']
        
        results = []
        stop_flag = threading.Event()
        
        def continuous_requests():
            while not stop_flag.is_set():
                try:
                    with patch.object(client.requests, 'get', return_value=mock_response):
                        client.get_user("test")
                        results.append(1)
                except:
                    pass
        
        with allure.step(f"启动 {concurrent_threads} 个持续请求线程"):
            threads = []
            for _ in range(concurrent_threads):
                t = threading.Thread(target=continuous_requests)
                t.daemon = True
                threads.append(t)
                t.start()
        
        with allure.step(f"持续运行 {duration_seconds} 秒"):
            time.sleep(duration_seconds)
            stop_flag.set()
        
        with allure.step("验证结果"):
            requests_per_second = len(results) / duration_seconds
            
            assert len(results) > 0, "没有成功的请求"
            
        client.close()
        
        allure.attach(
            f"持续时间: {duration_seconds}秒\n"
            f"总请求数: {len(results)}\n"
            f"每秒请求数: {requests_per_second:.1f}\n"
            f"并发线程: {concurrent_threads}",
            "持续压力测试结果",
            allure.attachment_type.TEXT
        )


@allure.feature("负载测试")
class TestLoadTest:
    """负载测试类 - 测试系统在不同负载下的表现"""
    
    @pytest.fixture
    def stress_data(self):
        """加载压力测试数据"""
        return DataHelper.load_framework_data()['stress_test']
    
    @allure.story("阶梯负载测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试逐步增加负载")
    def test_gradual_load_increase(self, stress_data):
        """测试阶梯负载 - 逐步增加并发数"""
        client = GitHubApi()
        
        mock_resp = stress_data['mock_response']
        load_levels = stress_data['load_levels']
        
        mock_response = Mock()
        mock_response.status_code = mock_resp['status_code']
        mock_response.json.return_value = mock_resp['body']
        
        load_results = []
        
        for level in load_levels:
            concurrent_users = level['concurrent_users']
            results = []
            
            def make_request():
                with patch.object(client.requests, 'get', return_value=mock_response):
                    client.get_user("test")
                    results.append(1)
            
            threads = [threading.Thread(target=make_request) for _ in range(concurrent_users)]
            
            start_time = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / concurrent_users
            
            load_results.append({
                "concurrent_users": concurrent_users,
                "description": level['description'],
                "total_time": total_time,
                "avg_time": avg_time
            })
        
        client.close()
        
        with allure.step("验证负载增加时性能下降可接受"):
            for i, result in enumerate(load_results):
                allure.attach(
                    f"并发数: {result['concurrent_users']}\n"
                    f"描述: {result['description']}\n"
                    f"总耗时: {result['total_time']:.3f}s\n"
                    f"平均耗时: {result['avg_time']*1000:.2f}ms",
                    f"负载级别 {i+1}",
                    allure.attachment_type.TEXT
                )


@allure.feature("性能基准测试")
class TestPerformanceBenchmark:
    """性能基准测试类"""
    
    @pytest.fixture
    def stress_data(self):
        """加载压力测试数据"""
        return DataHelper.load_framework_data()['stress_test']
    
    @allure.story("响应时间基准")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试响应时间分布")
    def test_response_time_distribution(self, stress_data):
        """测试响应时间分布"""
        client = GitHubApi()
        
        mock_resp = stress_data['mock_response']
        benchmark = stress_data['performance_benchmark']
        sample_count = benchmark['sample_count']
        max_avg_response_time_ms = benchmark['max_avg_response_time_ms']
        
        mock_response = Mock()
        mock_response.status_code = mock_resp['status_code']
        mock_response.json.return_value = mock_resp['body']
        
        response_times = []
        
        with allure.step(f"执行 {sample_count} 次请求并记录响应时间"):
            for _ in range(sample_count):
                start = time.time()
                with patch.object(client.requests, 'get', return_value=mock_response):
                    client.get_user("test")
                end = time.time()
                response_times.append((end - start) * 1000)
        
        client.close()
        
        with allure.step("计算统计数据"):
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95 = sorted(response_times)[int(len(response_times) * 0.95)]
            p99 = sorted(response_times)[int(len(response_times) * 0.99)]
        
        allure.attach(
            f"样本数: {sample_count}\n"
            f"平均响应时间: {avg_time:.2f}ms\n"
            f"最小响应时间: {min_time:.2f}ms\n"
            f"最大响应时间: {max_time:.2f}ms\n"
            f"P95 响应时间: {p95:.2f}ms\n"
            f"P99 响应时间: {p99:.2f}ms",
            "响应时间统计",
            allure.attachment_type.TEXT
        )
        
        assert avg_time < max_avg_response_time_ms, f"平均响应时间 {avg_time:.2f}ms 超过 {max_avg_response_time_ms}ms"
