"""
数据生成工具类 - 基于 Faker

职责：
1. 生成随机测试数据（正常流程测试）
2. 支持手动指定参数覆盖（边界值测试）
3. 支持随机种子（可重复测试）

注意：
- 边界值测试数据 → data/boundary_test_data.yaml
- 异常测试数据 → data/invalid_test_data.yaml
- API 测试数据 → data/api_test_data.yaml

使用指南：参见 docs/数据管理指南.md
"""
from faker import Faker
from typing import Dict, List, Any, Optional
import random
import time


class DataGenerator:
    """
    GitHub API 测试数据生成器
    
    使用方式：
    1. 正常流程测试：DataGenerator.generate_github_user()
    2. 边界值测试：DataGenerator.generate_github_user(login="a" * 40)
    3. 异常测试：DataGenerator.generate_github_user(login="")
    4. 可重复测试：DataGenerator.set_seed(12345)
    
    边界值和异常数据请使用 YAML 文件：
    - from common.yaml_util import DataHelper
    - DataHelper.load_boundary_data()
    - DataHelper.load_invalid_data()
    """
    
    _faker = None
    _seed = None
    
    @classmethod
    def set_seed(cls, seed: int):
        """
        设置随机种子，确保数据可重复
        
        Args:
            seed: 随机种子值
            
        使用场景：
            - CI/CD 中需要稳定的测试结果
            - 调试时需要可重复的数据
        """
        cls._seed = seed
        Faker.seed(seed)
        cls._faker = Faker('zh_CN')
    
    @classmethod
    def get_faker(cls) -> Faker:
        """获取 Faker 实例"""
        if cls._faker is None:
            cls._faker = Faker('zh_CN')
        return cls._faker
    
    @classmethod
    def generate_github_user(cls, 
                              login: Optional[str] = None,
                              user_id: Optional[int] = None,
                              name: Optional[str] = None,
                              email: Optional[str] = None,
                              company: Optional[str] = None,
                              followers: Optional[int] = None,
                              public_repos: Optional[int] = None,
                              **kwargs) -> Dict[str, Any]:
        """
        生成 GitHub 用户数据
        
        手动指定的参数会覆盖 Faker 生成的值，适用于：
        - 边界值测试：login="a" * 40
        - 异常测试：login=""
        - 特定场景测试：followers=0
        
        Args:
            login: 用户名（None 则自动生成）
            user_id: 用户ID（None 则自动生成）
            name: 姓名（None 则自动生成）
            email: 邮箱（None 则自动生成）
            company: 公司（None 则自动生成）
            followers: 关注者数（None 则自动生成）
            public_repos: 公开仓库数（None 则自动生成）
            **kwargs: 其他自定义字段
            
        Returns:
            Dict: GitHub API 用户格式数据
        """
        fake = cls.get_faker()
        username = login if login is not None else fake.user_name().lower().replace('_', '').replace('-', '')[:15]
        uid = user_id if user_id is not None else fake.random_int(min=1, max=10000000)
        
        base_data = {
            "login": username,
            "id": uid,
            "node_id": f"MDQ6VXNlcj{uid}",
            "avatar_url": f"https://avatars.githubusercontent.com/u/{uid}?v=3",
            "gravatar_id": "",
            "url": f"https://api.github.com/users/{username}",
            "html_url": f"https://github.com/{username}",
            "followers_url": f"https://api.github.com/users/{username}/followers",
            "following_url": f"https://api.github.com/users/{username}/following{{/other_user}}",
            "gists_url": f"https://api.github.com/users/{username}/gists{{/gist_id}}",
            "starred_url": f"https://api.github.com/users/{username}/starred{{/owner}}{{/repo}}",
            "subscriptions_url": f"https://api.github.com/users/{username}/subscriptions",
            "organizations_url": f"https://api.github.com/users/{username}/orgs",
            "repos_url": f"https://api.github.com/users/{username}/repos",
            "events_url": f"https://api.github.com/users/{username}/events{{/privacy}}",
            "received_events_url": f"https://api.github.com/users/{username}/received_events",
            "type": "User",
            "site_admin": False,
            "name": name if name is not None else fake.name(),
            "company": company if company is not None else (fake.company() if fake.boolean(chance_of_getting_true=50) else None),
            "blog": fake.url() if fake.boolean(chance_of_getting_true=30) else "",
            "location": fake.city() if fake.boolean(chance_of_getting_true=40) else None,
            "email": email if email is not None else (fake.email() if fake.boolean(chance_of_getting_true=30) else None),
            "hireable": fake.boolean(chance_of_getting_true=20) if fake.boolean(chance_of_getting_true=30) else None,
            "bio": fake.sentence(nb_words=10) if fake.boolean(chance_of_getting_true=40) else None,
            "twitter_username": None,
            "public_repos": public_repos if public_repos is not None else fake.random_int(min=0, max=100),
            "public_gists": fake.random_int(min=0, max=50),
            "followers": followers if followers is not None else fake.random_int(min=0, max=10000),
            "following": fake.random_int(min=0, max=500),
            "created_at": fake.date_time_between(start_date='-10y', end_date='-1y').strftime('%Y-%m-%dT%H:%M:%SZ'),
            "updated_at": fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        
        base_data.update(kwargs)
        return base_data
    
    @classmethod
    def generate_github_repository(cls,
                                    owner: Optional[str] = None,
                                    repo_name: Optional[str] = None,
                                    private: Optional[bool] = None,
                                    stargazers_count: Optional[int] = None,
                                    forks_count: Optional[int] = None,
                                    open_issues_count: Optional[int] = None,
                                    language: Optional[str] = None,
                                    description: Optional[str] = None,
                                    **kwargs) -> Dict[str, Any]:
        """
        生成 GitHub 仓库数据
        
        手动指定的参数会覆盖 Faker 生成的值，适用于：
        - 边界值测试：stargazers_count=0
        - 异常测试：repo_name=""
        - 特定场景测试：private=True
        
        Args:
            owner: 仓库所有者
            repo_name: 仓库名称
            private: 是否私有
            stargazers_count: 星标数
            forks_count: 分支数
            open_issues_count: 开放 Issue 数
            language: 编程语言
            description: 描述
            **kwargs: 其他自定义字段
            
        Returns:
            Dict: GitHub API 仓库格式数据
        """
        fake = cls.get_faker()
        owner_login = owner if owner is not None else fake.user_name().lower().replace('_', '')[:15]
        name = repo_name if repo_name is not None else fake.slug()[:30].replace('-', '_')
        repo_id = fake.random_int(min=1, max=100000000)
        languages = ['Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust', 'C++', 'C', 'Ruby', 'PHP', 'Swift', 'Kotlin']
        
        base_data = {
            "id": repo_id,
            "node_id": f"MDEwOlJlcG9zaXRvcnk{repo_id}",
            "name": name,
            "full_name": f"{owner_login}/{name}",
            "private": private if private is not None else False,
            "owner": {
                "login": owner_login,
                "id": fake.random_int(min=1, max=10000000),
                "node_id": f"MDQ6VXNlcj{fake.random_int(min=1, max=10000000)}",
                "avatar_url": f"https://avatars.githubusercontent.com/u/{fake.random_int(min=1, max=10000000)}?v=3",
                "gravatar_id": "",
                "url": f"https://api.github.com/users/{owner_login}",
                "html_url": f"https://github.com/{owner_login}",
                "type": "User",
                "site_admin": False
            },
            "html_url": f"https://github.com/{owner_login}/{name}",
            "description": description if description is not None else (fake.sentence(nb_words=8) if fake.boolean(chance_of_getting_true=70) else None),
            "fork": False,
            "url": f"https://api.github.com/repos/{owner_login}/{name}",
            "stargazers_count": stargazers_count if stargazers_count is not None else fake.random_int(min=0, max=100000),
            "watchers_count": stargazers_count if stargazers_count is not None else fake.random_int(min=0, max=100000),
            "language": language if language is not None else random.choice(languages),
            "forks_count": forks_count if forks_count is not None else fake.random_int(min=0, max=10000),
            "open_issues_count": open_issues_count if open_issues_count is not None else fake.random_int(min=0, max=500),
            "created_at": fake.date_time_between(start_date='-5y', end_date='-1m').strftime('%Y-%m-%dT%H:%M:%SZ'),
            "updated_at": fake.date_time_between(start_date='-1m', end_date='now').strftime('%Y-%m-%dT%H:%M:%SZ'),
            "pushed_at": fake.date_time_between(start_date='-1w', end_date='now').strftime('%Y-%m-%dT%H:%M:%SZ'),
            "homepage": fake.url() if fake.boolean(chance_of_getting_true=30) else None,
            "size": fake.random_int(min=0, max=500000),
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": fake.boolean(chance_of_getting_true=10),
            "forks": forks_count if forks_count is not None else fake.random_int(min=0, max=10000),
            "open_issues": open_issues_count if open_issues_count is not None else fake.random_int(min=0, max=500),
            "watchers": stargazers_count if stargazers_count is not None else fake.random_int(min=0, max=100000),
            "default_branch": "main",
            "visibility": "private" if private else "public",
        }
        
        base_data.update(kwargs)
        return base_data
    
    @classmethod
    def generate_github_repositories(cls, 
                                      count: int = 5,
                                      owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """批量生成 GitHub 仓库数据"""
        return [cls.generate_github_repository(owner=owner) for _ in range(count)]
    
    @classmethod
    def generate_github_issue(cls,
                               owner: Optional[str] = None,
                               repo: Optional[str] = None,
                               issue_number: Optional[int] = None,
                               state: Optional[str] = None,
                               title: Optional[str] = None,
                               body: Optional[str] = None,
                               labels: Optional[List[str]] = None,
                               **kwargs) -> Dict[str, Any]:
        """
        生成 GitHub Issue 数据
        
        手动指定的参数会覆盖 Faker 生成的值，适用于：
        - 边界值测试：title=""
        - 异常测试：body=None
        - 特定场景测试：state="closed"
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: Issue 编号
            state: Issue 状态
            title: 标题
            body: 内容
            labels: 标签列表
            **kwargs: 其他自定义字段
            
        Returns:
            Dict: GitHub API Issue 格式数据
        """
        fake = cls.get_faker()
        owner_login = owner if owner is not None else fake.user_name().lower().replace('_', '')[:15]
        repo_name = repo if repo is not None else fake.slug()[:30]
        num = issue_number if issue_number is not None else fake.random_int(min=1, max=10000)
        issue_id = fake.random_int(min=1, max=100000000)
        
        labels_list = ['bug', 'enhancement', 'documentation', 'help wanted', 'question', 'good first issue']
        selected_labels = labels if labels is not None else random.sample(labels_list, k=random.randint(0, 3))
        
        base_data = {
            "id": issue_id,
            "node_id": f"MDU6SXNzdWU{issue_id}",
            "url": f"https://api.github.com/repos/{owner_login}/{repo_name}/issues/{num}",
            "repository_url": f"https://api.github.com/repos/{owner_login}/{repo_name}",
            "labels_url": f"https://api.github.com/repos/{owner_login}/{repo_name}/issues/{num}/labels{{/name}}",
            "comments_url": f"https://api.github.com/repos/{owner_login}/{repo_name}/issues/{num}/comments",
            "events_url": f"https://api.github.com/repos/{owner_login}/{repo_name}/issues/{num}/events",
            "html_url": f"https://github.com/{owner_login}/{repo_name}/issues/{num}",
            "number": num,
            "state": state if state is not None else "open",
            "title": title if title is not None else fake.sentence(nb_words=6),
            "body": body if body is not None else (fake.paragraph(nb_sentences=3) if fake.boolean(chance_of_getting_true=80) else None),
            "user": {
                "login": fake.user_name().lower().replace('_', '')[:15],
                "id": fake.random_int(min=1, max=10000000),
                "type": "User",
                "site_admin": False
            },
            "labels": [
                {
                    "id": fake.random_int(min=1, max=100000000),
                    "name": label,
                    "color": fake.hex_color()[1:]
                } for label in selected_labels
            ],
            "locked": False,
            "comments": fake.random_int(min=0, max=50),
            "created_at": fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%dT%H:%M:%SZ'),
            "updated_at": fake.date_time_between(start_date='-1w', end_date='now').strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        
        base_data.update(kwargs)
        return base_data
    
    @classmethod
    def generate_github_issues(cls,
                                count: int = 5,
                                owner: Optional[str] = None,
                                repo: Optional[str] = None,
                                state: str = "open") -> List[Dict[str, Any]]:
        """批量生成 GitHub Issue 数据"""
        return [cls.generate_github_issue(owner=owner, repo=repo, state=state) for _ in range(count)]
    
    @classmethod
    def generate_search_result(cls,
                                query: str = '',
                                total_count: Optional[int] = None) -> Dict[str, Any]:
        """生成 GitHub 搜索结果数据"""
        fake = cls.get_faker()
        count = total_count if total_count is not None else fake.random_int(min=0, max=100000)
        
        return {
            "total_count": count,
            "incomplete_results": False,
            "items": cls.generate_github_repositories(min(count, 30))
        }
    
    @classmethod
    def generate_rate_limit(cls, 
                             remaining: Optional[int] = None,
                             limit: int = 5000) -> Dict[str, Any]:
        """
        生成 GitHub 频率限制数据
        
        Args:
            remaining: 剩余次数（None 则随机生成）
            limit: 总限制次数
            
        适用于：
            - 正常场景：remaining=4000
            - 边界场景：remaining=0
            - 异常场景：remaining=-1
        """
        fake = cls.get_faker()
        reset_time = int(time.time()) + 3600
        remaining_val = remaining if remaining is not None else fake.random_int(min=0, max=limit)
        
        return {
            "resources": {
                "core": {
                    "limit": limit,
                    "remaining": remaining_val,
                    "reset": reset_time,
                    "used": limit - remaining_val
                },
                "search": {
                    "limit": 30,
                    "remaining": fake.random_int(min=0, max=30),
                    "reset": reset_time,
                    "used": fake.random_int(min=0, max=30)
                }
            },
            "rate": {
                "limit": limit,
                "remaining": remaining_val,
                "reset": reset_time
            }
        }
    
    @classmethod
    def generate_error_response(cls,
                                  status_code: int = 404,
                                  message: Optional[str] = None) -> Dict[str, Any]:
        """
        生成 GitHub 错误响应
        
        Args:
            status_code: HTTP 状态码
            message: 错误消息
            
        适用于：
            - 404: 资源不存在
            - 401: 认证失败
            - 403: 权限不足/频率限制
            - 422: 参数验证失败
            - 500: 服务器错误
        """
        error_messages = {
            400: "Bad Request",
            401: "Bad credentials",
            403: "API rate limit exceeded",
            404: "Not Found",
            422: "Validation Failed",
            500: "Internal Server Error"
        }
        
        return {
            "message": message or error_messages.get(status_code, "Error"),
            "documentation_url": f"https://docs.github.com/rest",
            "status": status_code
        }
