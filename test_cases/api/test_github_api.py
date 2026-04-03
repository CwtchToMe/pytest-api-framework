"""
GitHub API 测试用例

数据来源：
- 正常数据：data/api_test_data.yaml (通过 DataHelper 加载)
- 随机数据：DataGenerator (Faker)
- 边界值：data/boundary_test_data.yaml
- 异常数据：data/invalid_test_data.yaml

使用指南：参见 docs/数据管理指南.md
"""
import pytest
import allure
from unittest.mock import Mock, patch
from api.github_api import GitHubApi
from config.config import config
from common.data_generator import DataGenerator
from common.yaml_util import DataHelper


@allure.feature("用户相关功能测试")
class TestUserFeatures:
    """用户相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("获取用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取指定用户信息")
    def test_get_user_info(self, github_client, api_data):
        """测试获取指定用户信息"""
        users = api_data['users']['valid']
        test_user = users[0]
        
        user_data = DataGenerator.generate_github_user(
            login=test_user['username'],
            user_id=test_user.get('expected_id')
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = user_data
        
        with allure.step("Mock GitHub API 响应"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                user = github_client.get_user(test_user['username'])
        
        with allure.step("验证用户基本信息"):
            assert user["login"] == test_user['username']
            assert "id" in user
            assert user["type"] == test_user.get('expected_type', 'User')
    
    @allure.story("获取当前认证用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取当前认证用户信息")
    def test_get_authenticated_user(self, github_client, api_data):
        """测试获取当前认证用户信息"""
        auth_user = api_data['authenticated_user']['valid']
        
        user_data = DataGenerator.generate_github_user()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = user_data
        
        with allure.step("Mock GitHub API 响应"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                user = github_client.get_my_user()
        
        with allure.step("验证认证用户信息"):
            for field in auth_user['expected_fields']:
                assert field in user
    
    @allure.story("获取用户仓库列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取用户公开仓库列表")
    def test_get_user_repositories(self, github_client, api_data):
        """测试获取用户公开仓库列表"""
        repos_data = DataGenerator.generate_github_repositories(2, owner=config.TEST_GITHUB_USER)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = repos_data
        
        with allure.step("Mock 获取用户仓库列表"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                repos = github_client.get_user_repos(config.TEST_GITHUB_USER, per_page=10)
        
        with allure.step("验证仓库列表"):
            assert isinstance(repos, list)
            assert len(repos) == 2
            
        with allure.step("验证第一个仓库信息"):
            first_repo = repos[0]
            assert "name" in first_repo
            assert first_repo["private"] == False
            assert "stargazers_count" in first_repo
    
    @allure.story("获取当前用户仓库列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取当前认证用户的仓库列表")
    def test_get_my_repositories(self, github_client):
        """测试获取当前认证用户的仓库列表"""
        public_repo = DataGenerator.generate_github_repository(private=False)
        private_repo = DataGenerator.generate_github_repository(private=True)
        repos_data = [public_repo, private_repo]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = repos_data
        
        with allure.step("Mock 获取当前用户仓库列表"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                repos = github_client.get_my_repos(visibility="all", per_page=10)
        
        with allure.step("验证仓库列表包含私有仓库"):
            assert isinstance(repos, list)
            assert len(repos) == 2
            
            private_repos = [r for r in repos if r["private"]]
            public_repos = [r for r in repos if not r["private"]]
            
            assert len(private_repos) == 1
            assert len(public_repos) == 1


@allure.feature("仓库相关功能测试")
class TestRepositoryFeatures:
    """仓库相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("获取仓库详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取指定仓库详情")
    def test_get_repository_detail(self, github_client, api_data):
        """测试获取指定仓库详情"""
        repos = api_data['repositories']['valid']
        test_repo = repos[0]
        
        repo_data = DataGenerator.generate_github_repository(
            owner=test_repo['owner'],
            repo_name=test_repo['repo'],
            private=test_repo.get('expected_private', False)
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = repo_data
        
        with allure.step(f"Mock 获取仓库详情: {test_repo['owner']}/{test_repo['repo']}"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                repo = github_client.get_repo(test_repo['owner'], test_repo['repo'])
        
        with allure.step("验证仓库基本信息"):
            assert "name" in repo
            assert "private" in repo
            assert repo["owner"]["login"] == test_repo['owner']
        
        with allure.step("验证仓库统计信息"):
            assert repo["stargazers_count"] >= 0
            assert repo["forks_count"] >= 0
            assert repo["open_issues_count"] >= 0
    
    @allure.story("获取不存在的仓库")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取不存在的仓库")
    def test_get_nonexistent_repository(self, github_client, api_data):
        """测试获取不存在的仓库"""
        invalid_repos = api_data['repositories']['invalid']
        test_repo = invalid_repos[0]
        
        error_data = DataGenerator.generate_error_response(
            status_code=test_repo['expected_status']
        )
        
        mock_response = Mock()
        mock_response.status_code = test_repo['expected_status']
        mock_response.json.return_value = error_data
        
        with allure.step("Mock 获取不存在的仓库"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                response = github_client.requests.get(
                    f"/repos/{test_repo['owner']}/{test_repo['repo']}"
                )
        
        with allure.step("验证返回 404"):
            assert response.status_code == test_repo['expected_status']


@allure.feature("搜索相关功能测试")
class TestSearchFeatures:
    """搜索相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("搜索仓库")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试搜索仓库功能")
    def test_search_repositories(self, github_client, api_data):
        """测试搜索仓库功能"""
        search_data = api_data['search']['repositories']['valid'][0]
        
        search_result = DataGenerator.generate_search_result(
            query=search_data['query'],
            total_count=search_data['expected_min_count']
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = search_result
        
        with allure.step("Mock 搜索仓库"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                result = github_client.search_repositories(
                    search_data['query'], 
                    sort=search_data['sort'], 
                    per_page=2
                )
        
        with allure.step("验证搜索结果"):
            assert "total_count" in result
            assert result["total_count"] >= search_data['expected_min_count']
            assert "items" in result
    
    @allure.story("搜索仓库 - 空结果")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试搜索仓库返回空结果")
    def test_search_repositories_empty_result(self, github_client, api_data):
        """测试搜索仓库返回空结果"""
        search_data = api_data['search']['repositories']['empty'][0]
        
        search_result = DataGenerator.generate_search_result(
            query=search_data['query'],
            total_count=search_data['expected_count']
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = search_result
        
        with allure.step("Mock 搜索不存在的仓库"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                result = github_client.search_repositories(search_data['query'], per_page=10)
        
        with allure.step("验证返回空结果"):
            assert result["total_count"] == 0


@allure.feature("Issue 相关功能测试")
class TestIssueFeatures:
    """Issue 相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("获取 Issue 列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取仓库 Issue 列表")
    def test_get_repository_issues(self, github_client):
        """测试获取仓库 Issue 列表"""
        issues_data = DataGenerator.generate_github_issues(2, owner=config.TEST_GITHUB_USER)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = issues_data
        
        with allure.step(f"Mock 获取仓库 Issue 列表"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                issues = github_client.get_issues(
                    config.TEST_GITHUB_USER,
                    "Hello-World",
                    state="open",
                    per_page=10
                )
        
        with allure.step("验证 Issue 列表"):
            assert isinstance(issues, list)
            assert len(issues) == 2
        
        with allure.step("验证第一个 Issue"):
            first_issue = issues[0]
            assert "number" in first_issue
            assert "state" in first_issue
            assert "labels" in first_issue
    
    @allure.story("创建 Issue")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试创建新 Issue")
    def test_create_issue(self, github_client, api_data):
        """测试创建新 Issue"""
        issue_data_from_yaml = api_data['issues']['create']['valid'][0]
        
        issue_data = DataGenerator.generate_github_issue(
            owner=config.TEST_GITHUB_USER,
            repo="Hello-World",
            title=issue_data_from_yaml['title'],
            body=issue_data_from_yaml.get('body'),
            labels=issue_data_from_yaml.get('labels')
        )
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = issue_data
        
        with allure.step("Mock 创建 Issue"):
            with patch.object(github_client.requests, 'post', return_value=mock_response):
                issue = github_client.create_issue(
                    config.TEST_GITHUB_USER,
                    "Hello-World",
                    title=issue_data_from_yaml['title'],
                    body=issue_data_from_yaml.get('body', '')
                )
        
        with allure.step("验证创建的 Issue"):
            assert "number" in issue
            assert "title" in issue
            assert issue["state"] == "open"
    
    @allure.story("获取 Issue 列表 - 按状态筛选")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取关闭状态的 Issue 列表")
    def test_get_closed_issues(self, github_client):
        """测试获取关闭状态的 Issue 列表"""
        issues_data = DataGenerator.generate_github_issues(1, owner=config.TEST_GITHUB_USER, state="closed")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = issues_data
        
        with allure.step("Mock 获取关闭状态的 Issue"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                issues = github_client.get_issues(
                    config.TEST_GITHUB_USER,
                    "Hello-World",
                    state="closed",
                    per_page=10
                )
        
        with allure.step("验证所有 Issue 都是关闭状态"):
            assert all(issue["state"] == "closed" for issue in issues)
    
    @allure.story("获取 Issue 列表 - 状态筛选数据驱动")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试按不同状态筛选 Issue")
    def test_filter_issues_by_state(self, github_client, api_data):
        """测试按不同状态筛选 Issue - 使用 issues.filter.states 数据"""
        filter_states = api_data['issues']['filter']['states']
        
        for state in filter_states:
            with allure.step(f"筛选状态: {state}"):
                issues_data = DataGenerator.generate_github_issues(2, owner=config.TEST_GITHUB_USER, state=state)
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = issues_data
                
                with patch.object(github_client.requests, 'get', return_value=mock_response):
                    issues = github_client.get_issues(
                        config.TEST_GITHUB_USER,
                        "Hello-World",
                        state=state,
                        per_page=10
                    )
                
                if state != "all":
                    assert all(issue["state"] == state for issue in issues)


@allure.feature("无效用户测试")
class TestInvalidUsers:
    """无效用户测试类 - 使用 users.invalid 数据"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("获取无效用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取不存在的用户")
    def test_get_invalid_users(self, github_client, api_data):
        """测试获取无效用户 - 使用 users.invalid 数据"""
        invalid_users = api_data['users']['invalid']
        
        for user_data in invalid_users:
            username = user_data['username']
            expected_status = user_data['expected_status']
            
            with allure.step(f"测试无效用户: '{username}'"):
                error_data = DataGenerator.generate_error_response(status_code=expected_status)
                
                mock_response = Mock()
                mock_response.status_code = expected_status
                mock_response.json.return_value = error_data
                
                with patch.object(github_client.requests, 'get', return_value=mock_response):
                    response = github_client.requests.get(f"/users/{username}")
                
                assert response.status_code == expected_status


@allure.feature("错误响应测试")
class TestErrorResponses:
    """错误响应测试类 - 使用 errors 数据"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("HTTP 错误响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试各种 HTTP 错误响应")
    def test_error_responses(self, github_client, api_data):
        """测试各种 HTTP 错误响应 - 使用 errors 数据"""
        errors = api_data['errors']
        
        for error_name, error_info in errors.items():
            status_code = error_info['status']
            message = error_info['message']
            
            with allure.step(f"测试错误: {error_name} ({status_code})"):
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


@allure.feature("API 频率限制测试")
class TestRateLimit:
    """API 频率限制测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("获取频率限制")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取 API 频率限制状态")
    def test_get_rate_limit_status(self, github_client, api_data):
        """测试获取 API 频率限制状态"""
        rate_limit_config = api_data['rate_limit']
        
        rate_limit_data = DataGenerator.generate_rate_limit(
            remaining=rate_limit_config['core']['min_remaining']
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = rate_limit_data
        
        with allure.step("Mock 获取频率限制状态"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                rate_limit = github_client.get_rate_limit()
        
        with allure.step("验证频率限制信息"):
            assert "resources" in rate_limit
            assert "core" in rate_limit["resources"]
            assert "search" in rate_limit["resources"]
            
        with allure.step("验证核心 API 限制"):
            core = rate_limit["resources"]["core"]
            assert core["limit"] == rate_limit_config['core']['limit']


@allure.feature("高级特性测试")
class TestEnterpriseFeatures:
    """高级特性测试类 - 测试插件系统"""
    
    @allure.story("熔断器插件")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器核心插件是否启用")
    def test_circuit_breaker_enabled(self):
        """测试熔断器核心插件是否启用"""
        from common.plugin_system import get_plugin_manager, PluginType
        
        with allure.step("获取插件管理器"):
            plugin_manager = get_plugin_manager()
        
        with allure.step("验证熔断器插件存在"):
            cb_plugin = plugin_manager.get_plugin('circuit_breaker')
            assert cb_plugin is not None
        
        with allure.step("验证熔断器是核心插件"):
            cb_info = plugin_manager.plugin_info['circuit_breaker']
            assert cb_info.plugin_type == PluginType.CORE
            assert cb_info.is_core == True
            assert cb_info.can_disable == False
    
    @allure.story("限流器插件")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器核心插件是否启用")
    def test_rate_limiter_enabled(self):
        """测试限流器核心插件是否启用"""
        from common.plugin_system import get_plugin_manager, PluginType
        
        with allure.step("获取插件管理器"):
            plugin_manager = get_plugin_manager()
        
        with allure.step("验证限流器插件存在"):
            rl_plugin = plugin_manager.get_plugin('rate_limiter')
            assert rl_plugin is not None
        
        with allure.step("验证限流器是核心插件"):
            rl_info = plugin_manager.plugin_info['rate_limiter']
            assert rl_info.plugin_type == PluginType.CORE
            assert rl_info.is_core == True
            assert rl_info.can_disable == False
    
    @allure.story("插件系统功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试插件系统是否启用")
    def test_plugins_enabled(self):
        """测试插件系统是否启用"""
        from common.plugin_system import get_plugin_manager
        
        with allure.step("获取插件管理器"):
            plugin_manager = get_plugin_manager()
        
        with allure.step("验证插件系统状态"):
            assert plugin_manager is not None
            assert len(plugin_manager.plugins) > 0
        
        with allure.step("验证核心插件数量"):
            core_plugins = plugin_manager.get_core_plugins()
            assert len(core_plugins) >= 2  # 熔断器 + 限流器
        
        with allure.step("验证普通插件数量"):
            normal_plugins = plugin_manager.get_normal_plugins()
            assert len(normal_plugins) >= 3  # 日志 + 指标 + 缓存


@allure.feature("性能测试")
class TestPerformance:
    """性能测试类"""
    
    @pytest.fixture
    def api_data(self):
        """加载 API 测试数据"""
        return DataHelper.load_api_data()
    
    @allure.story("响应时间测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 API 响应时间")
    def test_api_response_time(self, api_data):
        """测试 API 响应时间"""
        import time
        
        perf_config = api_data['performance']['response_time']
        client = GitHubApi()
        
        user_data = DataGenerator.generate_github_user(login=config.TEST_GITHUB_USER)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = user_data
        
        with allure.step("Mock API 请求并测量时间"):
            start_time = time.time()
            
            with patch.object(client.requests, 'get', return_value=mock_response):
                for i in range(perf_config['iterations']):
                    client.get_user(config.TEST_GITHUB_USER)
            
            end_time = time.time()
            total_time = end_time - start_time
        
        with allure.step("验证响应时间"):
            avg_time = total_time / perf_config['iterations']
            assert avg_time < perf_config['max_avg_time']
        
        client.close()
    
    @allure.story("并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试并发请求处理")
    def test_concurrent_requests(self, api_data):
        """测试并发请求处理"""
        import concurrent.futures
        
        perf_config = api_data['performance']['concurrent']
        client = GitHubApi()
        
        user_data = DataGenerator.generate_github_user(login=config.TEST_GITHUB_USER)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = user_data
        
        results = []
        
        def make_request():
            return client.get_user(config.TEST_GITHUB_USER)
        
        with allure.step("并发发送请求"):
            with patch.object(client.requests, 'get', return_value=mock_response):
                with concurrent.futures.ThreadPoolExecutor(max_workers=perf_config['threads']) as executor:
                    futures = [executor.submit(make_request) for _ in range(perf_config['iterations'])]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        with allure.step("验证所有请求都成功"):
            assert len(results) == perf_config['iterations']
        
        client.close()
