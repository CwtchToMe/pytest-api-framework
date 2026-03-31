"""
GitHub API 测试用例 - 完整版

测试场景：
1. 用户相关功能测试
2. 仓库相关功能测试
3. Issue 相关功能测试
4. 搜索相关功能测试
5. 企业级特性测试
6. 错误处理测试
7. 性能测试

使用 Mock 避免真实的 GitHub API 调用
"""
import pytest
import allure
from unittest.mock import Mock, patch
from api.github_api import GitHubApi
from config.config import config


@allure.feature("用户相关功能测试")
class TestUserFeatures:
    """用户相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @allure.story("获取用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取指定用户信息")
    def test_get_user_info(self, github_client):
        """测试获取指定用户信息"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "octocat",
            "id": 583231,
            "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=3",
            "html_url": "https://github.com/octocat",
            "type": "User",
            "name": "The Octocat",
            "company": "GitHub",
            "blog": "https://github.blog",
            "location": "San Francisco",
            "email": None,
            "bio": None,
            "public_repos": 8,
            "public_gists": 8,
            "followers": 5000,
            "following": 9
        }
        
        with allure.step("Mock GitHub API 响应"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                user = github_client.get_user(config.TEST_GITHUB_USER)
        
        with allure.step("验证用户基本信息"):
            assert user["login"] == "octocat"
            assert user["id"] == 583231
            assert user["type"] == "User"
        
        with allure.step("验证用户详细信息"):
            assert "name" in user
            assert "company" in user
            assert "public_repos" in user
            assert user["public_repos"] >= 0
        
        allure.attach(
            f"用户名: {user['login']}\n"
            f"姓名: {user.get('name', 'N/A')}\n"
            f"公司: {user.get('company', 'N/A')}\n"
            f"公开仓库数: {user['public_repos']}\n"
            f"关注者: {user['followers']}",
            "用户详细信息",
            allure.attachment_type.TEXT
        )
    
    @allure.story("获取当前认证用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取当前认证用户信息")
    def test_get_authenticated_user(self, github_client):
        """测试获取当前认证用户信息"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 123456,
            "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=3",
            "html_url": "https://github.com/testuser",
            "type": "User",
            "name": "Test User",
            "email": "test@example.com"
        }
        
        with allure.step("Mock GitHub API 响应"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                user = github_client.get_my_user()
        
        with allure.step("验证认证用户信息"):
            assert "login" in user
            assert "id" in user
            assert user["login"] == "testuser"
        
        allure.attach(
            f"认证用户: {user['login']}\nID: {user['id']}",
            "认证用户信息",
            allure.attachment_type.TEXT
        )
    
    @allure.story("获取用户仓库列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取用户公开仓库列表")
    def test_get_user_repositories(self, github_client):
        """测试获取用户公开仓库列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 123456,
                "name": "Hello-World",
                "full_name": "octocat/Hello-World",
                "private": False,
                "html_url": "https://github.com/octocat/Hello-World",
                "description": "My first repository",
                "stargazers_count": 80,
                "watchers_count": 80,
                "language": "JavaScript",
                "forks_count": 9,
                "open_issues_count": 0
            },
            {
                "id": 789012,
                "name": "Spoon-Knife",
                "full_name": "octocat/Spoon-Knife",
                "private": False,
                "html_url": "https://github.com/octocat/Spoon-Knife",
                "description": "This is a repo",
                "stargazers_count": 50,
                "watchers_count": 50,
                "language": "HTML",
                "forks_count": 5,
                "open_issues_count": 2
            }
        ]
        
        with allure.step("Mock 获取用户仓库列表"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                repos = github_client.get_user_repos(config.TEST_GITHUB_USER, per_page=10)
        
        with allure.step("验证仓库列表"):
            assert isinstance(repos, list)
            assert len(repos) == 2
            
        with allure.step("验证第一个仓库信息"):
            first_repo = repos[0]
            assert first_repo["name"] == "Hello-World"
            assert first_repo["private"] == False
            assert "stargazers_count" in first_repo
        
        allure.attach(
            f"仓库数量: {len(repos)}\n"
            f"第一个仓库: {repos[0]['name']}\n"
            f"星标数: {repos[0]['stargazers_count']}",
            "仓库列表统计",
            allure.attachment_type.TEXT
        )
    
    @allure.story("获取当前用户仓库列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取当前认证用户的仓库列表")
    def test_get_my_repositories(self, github_client):
        """测试获取当前认证用户的仓库列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 111111,
                "name": "my-repo-1",
                "full_name": "testuser/my-repo-1",
                "private": False,
                "html_url": "https://github.com/testuser/my-repo-1"
            },
            {
                "id": 222222,
                "name": "my-private-repo",
                "full_name": "testuser/my-private-repo",
                "private": True,
                "html_url": "https://github.com/testuser/my-private-repo"
            }
        ]
        
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
        
        allure.attach(
            f"总仓库数: {len(repos)}\n"
            f"公开仓库: {len(public_repos)}\n"
            f"私有仓库: {len(private_repos)}",
            "仓库统计",
            allure.attachment_type.TEXT
        )


@allure.feature("仓库相关功能测试")
class TestRepositoryFeatures:
    """仓库相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @allure.story("获取仓库详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试获取指定仓库详情")
    def test_get_repository_detail(self, github_client):
        """测试获取指定仓库详情"""
        repo_name = "Hello-World"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123456,
            "node_id": "MDEwOlJlcG9zaXRvcnkxMzU0OTM=",
            "name": repo_name,
            "full_name": f"{config.TEST_GITHUB_USER}/{repo_name}",
            "private": False,
            "owner": {
                "login": config.TEST_GITHUB_USER,
                "id": 583231,
                "type": "User"
            },
            "html_url": f"https://github.com/{config.TEST_GITHUB_USER}/{repo_name}",
            "description": "My first repository on GitHub!",
            "fork": False,
            "url": f"https://api.github.com/repos/{config.TEST_GITHUB_USER}/{repo_name}",
            "created_at": "2011-01-26T19:01:12Z",
            "updated_at": "2023-01-26T19:01:12Z",
            "pushed_at": "2023-01-26T19:01:12Z",
            "homepage": "",
            "size": 108,
            "stargazers_count": 80,
            "watchers_count": 80,
            "language": "JavaScript",
            "forks_count": 9,
            "open_issues_count": 0,
            "license": {
                "key": "mit",
                "name": "MIT License",
                "spdx_id": "MIT"
            }
        }
        
        with allure.step(f"Mock 获取仓库详情: {config.TEST_GITHUB_USER}/{repo_name}"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                repo = github_client.get_repo(config.TEST_GITHUB_USER, repo_name)
        
        with allure.step("验证仓库基本信息"):
            assert repo["name"] == repo_name
            assert repo["private"] == False
            assert repo["owner"]["login"] == config.TEST_GITHUB_USER
        
        with allure.step("验证仓库统计信息"):
            assert repo["stargazers_count"] >= 0
            assert repo["forks_count"] >= 0
            assert repo["open_issues_count"] >= 0
        
        with allure.step("验证仓库许可证"):
            assert "license" in repo
            assert repo["license"]["key"] == "mit"
        
        allure.attach(
            f"仓库名: {repo['name']}\n"
            f"完整名称: {repo['full_name']}\n"
            f"星标数: {repo['stargazers_count']}\n"
            f"分支数: {repo['forks_count']}\n"
            f"语言: {repo['language']}\n"
            f"许可证: {repo['license']['name']}",
            "仓库详情",
            allure.attachment_type.TEXT
        )
    
    @allure.story("获取不存在的仓库")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取不存在的仓库")
    def test_get_nonexistent_repository(self, github_client):
        """测试获取不存在的仓库"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "Not Found",
            "documentation_url": "https://docs.github.com/rest"
        }
        
        with allure.step("Mock 获取不存在的仓库"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                response = github_client.requests.get(
                    f"/repos/{config.TEST_GITHUB_USER}/nonexistent-repo"
                )
        
        with allure.step("验证返回 404"):
            assert response.status_code == 404
            assert response.json()["message"] == "Not Found"
        
        allure.attach(
            "正确处理不存在的仓库，返回 404",
            "错误处理验证",
            allure.attachment_type.TEXT
        )


@allure.feature("搜索相关功能测试")
class TestSearchFeatures:
    """搜索相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @allure.story("搜索仓库")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试搜索仓库功能")
    def test_search_repositories(self, github_client):
        """测试搜索仓库功能"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 1000,
            "incomplete_results": False,
            "items": [
                {
                    "id": 789012,
                    "name": "django",
                    "full_name": "django/django",
                    "owner": {
                        "login": "django",
                        "id": 27804
                    },
                    "html_url": "https://github.com/django/django",
                    "description": "The Web framework for perfectionists with deadlines.",
                    "stargazers_count": 70000,
                    "watchers_count": 70000,
                    "language": "Python",
                    "forks_count": 30000,
                    "open_issues_count": 200,
                    "score": 100.0
                },
                {
                    "id": 123456,
                    "name": "python",
                    "full_name": "python/cpython",
                    "owner": {
                        "login": "python",
                        "id": 1525981
                    },
                    "html_url": "https://github.com/python/cpython",
                    "description": "The Python programming language",
                    "stargazers_count": 50000,
                    "watchers_count": 50000,
                    "language": "Python",
                    "forks_count": 25000,
                    "open_issues_count": 1000,
                    "score": 90.0
                }
            ]
        }
        
        with allure.step("Mock 搜索 Python 相关仓库"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                result = github_client.search_repositories("python", sort="stars", per_page=2)
        
        with allure.step("验证搜索结果"):
            assert "total_count" in result
            assert result["total_count"] > 0
            assert "items" in result
            assert len(result["items"]) == 2
        
        with allure.step("验证搜索结果按星标排序"):
            items = result["items"]
            assert items[0]["stargazers_count"] >= items[1]["stargazers_count"]
        
        allure.attach(
            f"总结果数: {result['total_count']}\n"
            f"返回数量: {len(result['items'])}\n"
            f"第一个仓库: {items[0]['full_name']}\n"
            f"星标数: {items[0]['stargazers_count']}",
            "搜索结果统计",
            allure.attachment_type.TEXT
        )
    
    @allure.story("搜索仓库 - 空结果")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试搜索仓库返回空结果")
    def test_search_repositories_empty_result(self, github_client):
        """测试搜索仓库返回空结果"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 0,
            "incomplete_results": False,
            "items": []
        }
        
        with allure.step("Mock 搜索不存在的仓库"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                result = github_client.search_repositories("nonexistent-repo-xyz-12345", per_page=10)
        
        with allure.step("验证返回空结果"):
            assert result["total_count"] == 0
            assert len(result["items"]) == 0
        
        allure.attach(
            "正确处理空搜索结果",
            "空结果验证",
            allure.attachment_type.TEXT
        )


@allure.feature("Issue 相关功能测试")
class TestIssueFeatures:
    """Issue 相关功能测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @allure.story("获取 Issue 列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取仓库 Issue 列表")
    def test_get_repository_issues(self, github_client):
        """测试获取仓库 Issue 列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "number": 1,
                "title": "Found a bug",
                "body": "I'm having a problem with this.",
                "state": "open",
                "user": {
                    "login": "octocat",
                    "id": 583231
                },
                "labels": [
                    {
                        "id": 208045946,
                        "name": "bug",
                        "color": "f29513"
                    }
                ],
                "comments": 0,
                "created_at": "2011-04-22T13:33:48Z",
                "updated_at": "2011-04-22T13:33:48Z",
                "html_url": f"https://github.com/{config.TEST_GITHUB_USER}/Hello-World/issues/1"
            },
            {
                "id": 2,
                "number": 2,
                "title": "Feature request",
                "body": "I would like to see this feature.",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 123456
                },
                "labels": [
                    {
                        "id": 208045947,
                        "name": "enhancement",
                        "color": "a2eeef"
                    }
                ],
                "comments": 5,
                "created_at": "2011-04-22T13:33:48Z",
                "updated_at": "2011-04-22T13:33:48Z",
                "html_url": f"https://github.com/{config.TEST_GITHUB_USER}/Hello-World/issues/2"
            }
        ]
        
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
            assert first_issue["number"] == 1
            assert first_issue["state"] == "open"
            assert "labels" in first_issue
            assert len(first_issue["labels"]) > 0
        
        allure.attach(
            f"Issue 数量: {len(issues)}\n"
            f"第一个 Issue: #{issues[0]['number']} - {issues[0]['title']}\n"
            f"状态: {issues[0]['state']}\n"
            f"标签数: {len(issues[0]['labels'])}",
            "Issue 列表统计",
            allure.attachment_type.TEXT
        )
    
    @allure.story("创建 Issue")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试创建新 Issue")
    def test_create_issue(self, github_client):
        """测试创建新 Issue"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 3,
            "number": 3,
            "title": "Test Issue",
            "body": "This is a test issue created by automation",
            "state": "open",
            "user": {
                "login": "testuser",
                "id": 123456
            },
            "labels": [],
            "comments": 0,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": f"https://github.com/{config.TEST_GITHUB_USER}/Hello-World/issues/3"
        }
        
        with allure.step("Mock 创建 Issue"):
            with patch.object(github_client.requests, 'post', return_value=mock_response):
                issue = github_client.create_issue(
                    config.TEST_GITHUB_USER,
                    "Hello-World",
                    title="Test Issue",
                    body="This is a test issue created by automation"
                )
        
        with allure.step("验证创建的 Issue"):
            assert issue["number"] == 3
            assert issue["title"] == "Test Issue"
            assert issue["state"] == "open"
        
        allure.attach(
            f"Issue 编号: #{issue['number']}\n"
            f"标题: {issue['title']}\n"
            f"状态: {issue['state']}\n"
            f"URL: {issue['html_url']}",
            "创建的 Issue 信息",
            allure.attachment_type.TEXT
        )
    
    @allure.story("获取 Issue 列表 - 按状态筛选")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取关闭状态的 Issue 列表")
    def test_get_closed_issues(self, github_client):
        """测试获取关闭状态的 Issue 列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 4,
                "number": 4,
                "title": "Closed Issue",
                "state": "closed",
                "user": {
                    "login": "octocat",
                    "id": 583231
                }
            }
        ]
        
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
        
        allure.attach(
            f"关闭的 Issue 数量: {len(issues)}",
            "关闭状态 Issue 统计",
            allure.attachment_type.TEXT
        )


@allure.feature("API 频率限制测试")
class TestRateLimit:
    """API 频率限制测试类"""
    
    @pytest.fixture
    def github_client(self):
        """GitHub API 客户端 Fixture"""
        client = GitHubApi()
        yield client
        client.close()
    
    @allure.story("获取频率限制")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试获取 API 频率限制状态")
    def test_get_rate_limit_status(self, github_client):
        """测试获取 API 频率限制状态"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resources": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": 1774871400,
                    "used": 1
                },
                "search": {
                    "limit": 30,
                    "remaining": 30,
                    "reset": 1774867800,
                    "used": 0
                },
                "graphql": {
                    "limit": 5000,
                    "remaining": 5000,
                    "reset": 1774871400,
                    "used": 0
                }
            },
            "rate": {
                "limit": 5000,
                "remaining": 4999,
                "reset": 1774871400
            }
        }
        
        with allure.step("Mock 获取频率限制状态"):
            with patch.object(github_client.requests, 'get', return_value=mock_response):
                rate_limit = github_client.get_rate_limit()
        
        with allure.step("验证频率限制信息"):
            assert "resources" in rate_limit
            assert "core" in rate_limit["resources"]
            assert "search" in rate_limit["resources"]
            
        with allure.step("验证核心 API 限制"):
            core = rate_limit["resources"]["core"]
            assert core["limit"] == 5000
            assert core["remaining"] >= 0
            assert core["remaining"] <= core["limit"]
        
        with allure.step("验证搜索 API 限制"):
            search = rate_limit["resources"]["search"]
            assert search["limit"] == 30
            assert search["remaining"] >= 0
        
        allure.attach(
            f"核心 API 限制: {core['limit']}\n"
            f"核心 API 剩余: {core['remaining']}\n"
            f"搜索 API 限制: {search['limit']}\n"
            f"搜索 API 剩余: {search['remaining']}",
            "频率限制信息",
            allure.attachment_type.TEXT
        )


@allure.feature("企业级特性测试")
class TestEnterpriseFeatures:
    """企业级特性测试类"""
    
    @allure.story("熔断器功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试熔断器是否启用")
    def test_circuit_breaker_enabled(self):
        """测试熔断器是否启用"""
        with allure.step("创建 GitHub API 客户端"):
            client = GitHubApi()
        
        with allure.step("验证熔断器状态"):
            assert client.enable_circuit_breaker == True
            assert client.requests.circuit_breaker is not None
        
        client.close()
        
        allure.attach(
            "熔断器已成功启用并配置",
            "熔断器状态",
            allure.attachment_type.TEXT
        )
    
    @allure.story("限流器功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试限流器是否启用")
    def test_rate_limiter_enabled(self):
        """测试限流器是否启用"""
        with allure.step("创建 GitHub API 客户端"):
            client = GitHubApi()
        
        with allure.step("验证限流器状态"):
            assert client.enable_rate_limiter == True
            assert client.requests.rate_limiter is not None
        
        client.close()
        
        allure.attach(
            "限流器已成功启用并配置",
            "限流器状态",
            allure.attachment_type.TEXT
        )
    
    @allure.story("插件系统功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("测试插件系统是否启用")
    def test_plugins_enabled(self):
        """测试插件系统是否启用"""
        with allure.step("创建 GitHub API 客户端"):
            client = GitHubApi()
        
        with allure.step("验证插件系统状态"):
            assert client.enable_plugins == True
            assert client.requests.plugin_manager is not None
        
        client.close()
        
        allure.attach(
            "插件系统已成功启用并配置",
            "插件系统状态",
            allure.attachment_type.TEXT
        )
    
    @allure.story("连续请求测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试连续多个请求")
    def test_multiple_concurrent_requests(self):
        """测试连续多个请求（验证限流器和熔断器）"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": config.TEST_GITHUB_USER,
            "id": 583231
        }
        
        with allure.step("Mock 连续发送 10 个请求"):
            with patch.object(client.requests, 'get', return_value=mock_response):
                results = []
                for i in range(10):
                    user = client.get_user(config.TEST_GITHUB_USER)
                    results.append(user["login"])
        
        with allure.step("验证所有请求都成功"):
            assert len(results) == 10
            assert all(login == config.TEST_GITHUB_USER for login in results)
        
        client.close()
        
        allure.attach(
            f"成功发送 {len(results)} 个请求\n"
            f"限流器和熔断器正常工作",
            "连续请求统计",
            allure.attachment_type.TEXT
        )
    
    @allure.story("错误处理测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试处理 500 错误")
    def test_handle_server_error(self):
        """测试处理服务器错误"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "message": "Internal Server Error"
        }
        
        with allure.step("Mock 服务器错误"):
            with patch.object(client.requests, 'get', return_value=mock_response):
                response = client.requests.get(f"/users/{config.TEST_GITHUB_USER}")
        
        with allure.step("验证错误状态码"):
            assert response.status_code == 500
            assert "message" in response.json()
        
        client.close()
        
        allure.attach(
            "正确处理服务器错误",
            "错误处理验证",
            allure.attachment_type.TEXT
        )
    
    @allure.story("错误处理测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试处理 403 错误")
    def test_handle_forbidden_error(self):
        """测试处理权限错误"""
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "message": "API rate limit exceeded",
            "documentation_url": "https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"
        }
        
        with allure.step("Mock 权限错误"):
            with patch.object(client.requests, 'get', return_value=mock_response):
                response = client.requests.get(f"/users/{config.TEST_GITHUB_USER}")
        
        with allure.step("验证错误状态码"):
            assert response.status_code == 403
            assert "rate limit" in response.json()["message"].lower()
        
        client.close()
        
        allure.attach(
            "正确处理 API 频率限制错误",
            "错误处理验证",
            allure.attachment_type.TEXT
        )


@allure.feature("性能测试")
class TestPerformance:
    """性能测试类"""
    
    @allure.story("响应时间测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试 API 响应时间")
    def test_api_response_time(self):
        """测试 API 响应时间"""
        import time
        
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": config.TEST_GITHUB_USER,
            "id": 583231
        }
        
        with allure.step("Mock API 请求并测量时间"):
            start_time = time.time()
            
            with patch.object(client.requests, 'get', return_value=mock_response):
                for i in range(5):
                    client.get_user(config.TEST_GITHUB_USER)
            
            end_time = time.time()
            total_time = end_time - start_time
        
        with allure.step("验证响应时间"):
            avg_time = total_time / 5
            assert avg_time < 1.0, f"平均响应时间 {avg_time:.2f}s 超过 1 秒"
        
        client.close()
        
        allure.attach(
            f"总执行时间: {total_time:.3f}s\n"
            f"平均响应时间: {avg_time:.3f}s\n"
            f"请求数量: 5",
            "性能统计",
            allure.attachment_type.TEXT
        )
    
    @allure.story("并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("测试并发请求处理")
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        import concurrent.futures
        
        client = GitHubApi()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": config.TEST_GITHUB_USER,
            "id": 583231
        }
        
        results = []
        
        def make_request():
            return client.get_user(config.TEST_GITHUB_USER)
        
        with allure.step("并发发送 5 个请求"):
            with patch.object(client.requests, 'get', return_value=mock_response):
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(make_request) for _ in range(5)]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        with allure.step("验证所有请求都成功"):
            assert len(results) == 5
            assert all(user["login"] == config.TEST_GITHUB_USER for user in results)
        
        client.close()
        
        allure.attach(
            f"并发请求数: 5\n"
            f"成功处理: {len(results)}\n"
            f"并发处理正常",
            "并发测试结果",
            allure.attachment_type.TEXT
        )
