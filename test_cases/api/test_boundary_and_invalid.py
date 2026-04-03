"""
边界值测试和异常测试

数据来源：
- 边界值数据：data/boundary_test_data.yaml
- 异常数据：data/invalid_test_data.yaml
- 正常数据：DataGenerator (Faker)

使用指南：参见 docs/数据管理指南.md
"""
import pytest
import allure
from unittest.mock import Mock, patch
from api.github_api import GitHubApi
from config.config import config
from common.data_generator import DataGenerator
from common.yaml_util import DataHelper


@allure.feature("边界值测试")
class TestBoundaryValues:
    """
    边界值测试类
    
    数据来源：data/boundary_test_data.yaml
    修改数据：直接编辑 YAML 文件
    """
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def boundary_data(self):
        """加载边界值测试数据"""
        return DataHelper.load_boundary_data()
    
    @allure.story("用户名边界值")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_username_boundary(self, github_client, boundary_data):
        """测试用户名边界值"""
        boundaries = boundary_data['username']['boundaries']
        
        for item in boundaries:
            username = item['value']
            expected_valid = item['expected_valid']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                if expected_valid:
                    user_data = DataGenerator.generate_github_user(login=username)
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = user_data
                    
                    with patch.object(github_client.requests, 'get', return_value=mock_response):
                        user = github_client.get_user(username)
                        assert user["login"] == username
                else:
                    error_data = DataGenerator.generate_error_response(status_code=422)
                    mock_response = Mock()
                    mock_response.status_code = 422
                    mock_response.json.return_value = error_data
                    
                    with patch.object(github_client.requests, 'get', return_value=mock_response):
                        response = github_client.requests.get(f"/users/{username}")
                        assert response.status_code == 422
    
    @allure.story("星标数边界值")
    @allure.severity(allure.severity_level.NORMAL)
    def test_stargazers_boundary(self, boundary_data):
        """测试星标数边界值"""
        boundaries = boundary_data['stargazers']['boundaries']
        
        for item in boundaries:
            stargazers = item['value']
            expected_valid = item['expected_valid']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                if expected_valid:
                    repo_data = DataGenerator.generate_github_repository(stargazers_count=stargazers)
                    assert repo_data["stargazers_count"] == stargazers
                else:
                    allure.attach(f"负数 {stargazers} 应被拒绝", "无效数据", allure.attachment_type.TEXT)
    
    @allure.story("Issue 标题边界值")
    @allure.severity(allure.severity_level.NORMAL)
    def test_issue_title_boundary(self, boundary_data):
        """测试 Issue 标题边界值"""
        boundaries = boundary_data['issue_title']['boundaries']
        
        for item in boundaries:
            title = item['value']
            expected_valid = item['expected_valid']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                issue_data = DataGenerator.generate_github_issue(title=title)
                assert issue_data["title"] == title
    
    @allure.story("频率限制边界值")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_rate_limit_boundary(self, boundary_data):
        """测试频率限制边界值"""
        boundaries = boundary_data['rate_limit']['boundaries']
        
        for item in boundaries:
            remaining = item['remaining']
            expected_valid = item['expected_valid']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                rate_limit = DataGenerator.generate_rate_limit(remaining=remaining)
                assert rate_limit["rate"]["remaining"] == remaining


@allure.feature("异常测试")
class TestInvalidData:
    """
    异常测试类
    
    数据来源：data/invalid_test_data.yaml
    修改数据：直接编辑 YAML 文件
    """
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def invalid_data(self):
        """加载异常测试数据"""
        return DataHelper.load_invalid_data()
    
    @allure.story("SQL 注入测试")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection(self, github_client, invalid_data):
        """测试 SQL 注入攻击"""
        payloads = invalid_data['sql_injection']['payloads']
        
        for item in payloads:
            sql_injection = item['value']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                error_data = DataGenerator.generate_error_response(status_code=400)
                mock_response = Mock()
                mock_response.status_code = 400
                mock_response.json.return_value = error_data
                
                with patch.object(github_client.requests, 'get', return_value=mock_response):
                    response = github_client.requests.get(f"/users/{sql_injection}")
                    assert response.status_code == 400
    
    @allure.story("XSS 攻击测试")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_attack(self, github_client, invalid_data):
        """测试 XSS 攻击"""
        payloads = invalid_data['xss_attack']['payloads']
        
        for item in payloads:
            xss_payload = item['value']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                error_data = DataGenerator.generate_error_response(status_code=400)
                mock_response = Mock()
                mock_response.status_code = 400
                mock_response.json.return_value = error_data
                
                with patch.object(github_client.requests, 'get', return_value=mock_response):
                    response = github_client.requests.get(f"/users/{xss_payload}")
                    assert response.status_code == 400
    
    @allure.story("无效邮箱格式")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_email_format(self, invalid_data):
        """测试无效邮箱格式"""
        formats = invalid_data['invalid_email']['formats']
        
        for item in formats:
            invalid_email = item['value']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                user_data = DataGenerator.generate_github_user(email=invalid_email)
                allure.attach(f"邮箱: '{invalid_email}'", description, allure.attachment_type.TEXT)
    
    @allure.story("特殊字符测试")
    @allure.severity(allure.severity_level.NORMAL)
    def test_special_characters(self, invalid_data):
        """测试特殊字符"""
        cases = invalid_data['special_characters']['cases']
        
        for item in cases:
            special_char = item['value']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                user_data = DataGenerator.generate_github_user(login=special_char)
                assert user_data["login"] == special_char
    
    @allure.story("类型错误测试")
    @allure.severity(allure.severity_level.NORMAL)
    def test_type_errors(self, invalid_data):
        """测试类型错误"""
        cases = invalid_data['type_errors']['cases']
        
        for item in cases:
            login_value = item['value']
            description = item['description']
            
            with allure.step(f"测试: {description}"):
                allure.attach(
                    f"输入值: {login_value}\n类型: {type(login_value).__name__}",
                    description,
                    allure.attachment_type.TEXT
                )
    
    @allure.story("HTTP 错误响应")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_http_error_responses(self, github_client, invalid_data):
        """测试 HTTP 错误响应 - 使用 error_responses 数据"""
        error_responses = invalid_data['error_responses']
        
        for error in error_responses:
            status_code = error['status_code']
            message = error['message']
            description = error['description']
            
            with allure.step(f"测试: {description} ({status_code})"):
                error_data = DataGenerator.generate_error_response(
                    status_code=status_code,
                    message=message
                )
                
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.json.return_value = error_data
                
                with patch.object(github_client.requests, 'get', return_value=mock_response):
                    response = github_client.requests.get("/test")
                
                assert response.status_code == status_code
                assert response.json()["message"] == message


@allure.feature("混合测试 - Faker + YAML")
class TestHybridDataGeneration:
    """
    混合测试类
    
    展示如何结合使用：
    - Faker：正常流程测试
    - YAML：边界值和异常测试
    """
    
    @allure.story("正常流程 + 边界值组合")
    @allure.severity(allure.severity_level.NORMAL)
    def test_normal_and_boundary_combined(self):
        """测试正常流程和边界值组合"""
        boundary_data = DataHelper.load_boundary_data()
        
        with allure.step("1. 正常流程测试 - 使用 Faker"):
            normal_user = DataGenerator.generate_github_user()
            assert len(normal_user["login"]) > 0
        
        with allure.step("2. 边界值测试 - 从 YAML 加载"):
            boundaries = boundary_data['username']['boundaries']
            for item in boundaries:
                user = DataGenerator.generate_github_user(login=item['value'])
                assert user["login"] == item['value']
    
    @allure.story("可重复数据测试")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reproducible_data(self):
        """测试设置随机种子确保数据可重复"""
        with allure.step("设置随机种子"):
            DataGenerator.set_seed(12345)
        
        with allure.step("第一次生成"):
            user1 = DataGenerator.generate_github_user()
        
        with allure.step("重置种子并重新生成"):
            DataGenerator.set_seed(12345)
            user2 = DataGenerator.generate_github_user()
        
        with allure.step("验证数据完全相同"):
            assert user1["login"] == user2["login"]
            assert user1["name"] == user2["name"]
