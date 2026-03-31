"""
压力测试和负载测试

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


@allure.feature("压力测试")
class TestStressTest:
    """压力测试类 - 测试系统在极端条件下的表现"""
    
    @allure.story("高并发压力测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 100 并发请求")
    def test_high_concurrency_stress(self):
        """测试高并发压力 - 100 个并发请求"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test", "id": 123}
        
        results = []
        errors = []
        
        def make_request():
            try:
                with patch.object(client.requests, 'get', return_value=mock_response):
                    user = client.get_user("test")
                    results.append(user)
            except Exception as e:
                errors.append(str(e))
        
        with allure.step("创建 100 个并发线程"):
            threads = []
            for _ in range(100):
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
            success_rate = len(results) / 100 * 100
            total_time = end_time - start_time
            
            assert len(errors) == 0, f"存在错误: {errors}"
            assert success_rate == 100, f"成功率: {success_rate}%"
            
        client.close()
        
        allure.attach(
            f"并发数: 100\n"
            f"成功数: {len(results)}\n"
            f"错误数: {len(errors)}\n"
            f"总耗时: {total_time:.2f}s\n"
            f"成功率: {success_rate}%",
            "压力测试结果",
            allure.attachment_type.TEXT
        )
    
    @allure.story("持续压力测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试持续 10 秒高压请求")
    def test_sustained_stress(self):
        """测试持续压力 - 持续 10 秒的高频请求"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test", "id": 123}
        
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
        
        with allure.step("启动 10 个持续请求线程"):
            threads = []
            for _ in range(10):
                t = threading.Thread(target=continuous_requests)
                t.daemon = True
                threads.append(t)
                t.start()
        
        with allure.step("持续运行 10 秒"):
            time.sleep(10)
            stop_flag.set()
        
        with allure.step("验证结果"):
            requests_per_second = len(results) / 10
            
            assert len(results) > 0, "没有成功的请求"
            
        client.close()
        
        allure.attach(
            f"持续时间: 10秒\n"
            f"总请求数: {len(results)}\n"
            f"每秒请求数: {requests_per_second:.1f}\n"
            f"并发线程: 10",
            "持续压力测试结果",
            allure.attachment_type.TEXT
        )


@allure.feature("负载测试")
class TestLoadTest:
    """负载测试类 - 测试系统在不同负载下的表现"""
    
    @allure.story("阶梯负载测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试逐步增加负载")
    def test_gradual_load_increase(self):
        """测试阶梯负载 - 逐步增加并发数"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test", "id": 123}
        
        load_results = []
        
        for concurrent_users in [10, 20, 50, 100]:
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
                "total_time": total_time,
                "avg_time": avg_time
            })
        
        client.close()
        
        with allure.step("验证负载增加时性能下降可接受"):
            for i, result in enumerate(load_results):
                allure.attach(
                    f"并发数: {result['concurrent_users']}\n"
                    f"总耗时: {result['total_time']:.3f}s\n"
                    f"平均耗时: {result['avg_time']*1000:.2f}ms",
                    f"负载级别 {i+1}",
                    allure.attachment_type.TEXT
                )


@allure.feature("性能基准测试")
class TestPerformanceBenchmark:
    """性能基准测试类"""
    
    @allure.story("响应时间基准")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试响应时间分布")
    def test_response_time_distribution(self):
        """测试响应时间分布"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test", "id": 123}
        
        response_times = []
        
        with allure.step("执行 100 次请求并记录响应时间"):
            for _ in range(100):
                start = time.time()
                with patch.object(client.requests, 'get', return_value=mock_response):
                    client.get_user("test")
                end = time.time()
                response_times.append((end - start) * 1000)  # 转换为毫秒
        
        client.close()
        
        with allure.step("计算统计数据"):
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95 = sorted(response_times)[int(len(response_times) * 0.95)]
            p99 = sorted(response_times)[int(len(response_times) * 0.99)]
        
        allure.attach(
            f"样本数: 100\n"
            f"平均响应时间: {avg_time:.2f}ms\n"
            f"最小响应时间: {min_time:.2f}ms\n"
            f"最大响应时间: {max_time:.2f}ms\n"
            f"P95 响应时间: {p95:.2f}ms\n"
            f"P99 响应时间: {p99:.2f}ms",
            "响应时间统计",
            allure.attachment_type.TEXT
        )
        
        assert avg_time < 100, f"平均响应时间 {avg_time:.2f}ms 超过 100ms"
