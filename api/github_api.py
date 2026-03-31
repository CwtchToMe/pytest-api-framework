"""
GitHub API 封装类

功能：
1. 获取用户信息
2. 获取仓库列表
3. 获取仓库详情
4. 创建 Issue
5. 获取 Issue 列表

特性：
- 自动添加认证 token
- 处理 GitHub API 的频率限制
- 集成熔断器和限流器
"""
import logging
from typing import Dict, Any, Optional, List
from api.base_api import BaseApi
from config.config import config

logger = logging.getLogger(__name__)


class GitHubApi(BaseApi):
    """GitHub API 封装类"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化 GitHub API 客户端
        
        Args:
            token: GitHub Personal Access Token（可选，如果不提供则从配置读取）
        """
        super().__init__(
            base_url=config.GITHUB_API_URL,
            enable_circuit_breaker=config.ENABLE_CIRCUIT_BREAKER,
            enable_rate_limiter=config.ENABLE_RATE_LIMITER,
            enable_plugins=config.ENABLE_PLUGINS
        )
        self.token = token or config.GITHUB_TOKEN
        self.enable_circuit_breaker = config.ENABLE_CIRCUIT_BREAKER
        self.enable_rate_limiter = config.ENABLE_RATE_LIMITER
        self.enable_plugins = config.ENABLE_PLUGINS
        
        if not self.token:
            logger.warning("GitHub Token 未设置，某些 API 可能无法访问")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头（包含认证信息）
        
        Returns:
            Dict[str, str]: 请求头
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AutoTest-Framework/1.0"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        return headers
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            username: GitHub 用户名
        
        Returns:
            Dict[str, Any]: 用户信息
        """
        logger.info(f"获取用户信息: {username}")
        response = self.get(
            f"/users/{username}",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_my_user(self) -> Dict[str, Any]:
        """
        获取当前认证用户信息
        
        Returns:
            Dict[str, Any]: 当前用户信息
        """
        logger.info("获取当前认证用户信息")
        response = self.get(
            "/user",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_user_repos(
        self,
        username: str,
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取用户的仓库列表
        
        Args:
            username: GitHub 用户名
            page: 页码（从 1 开始）
            per_page: 每页数量（最大 100）
        
        Returns:
            List[Dict[str, Any]]: 仓库列表
        """
        logger.info(f"获取用户 {username} 的仓库列表（第 {page} 页）")
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "sort": "updated",
            "direction": "desc"
        }
        response = self.get(
            f"/users/{username}/repos",
            params=params,
            headers=self._get_headers()
        )
        return response.json()
    
    def get_my_repos(
        self,
        page: int = 1,
        per_page: int = 30,
        visibility: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        获取当前认证用户的仓库列表
        
        Args:
            page: 页码（从 1 开始）
            per_page: 每页数量（最大 100）
            visibility: 可见性（all/public/private）
        
        Returns:
            List[Dict[str, Any]]: 仓库列表
        """
        logger.info(f"获取当前用户的仓库列表（第 {page} 页）")
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "sort": "updated",
            "direction": "desc",
            "visibility": visibility
        }
        response = self.get(
            "/user/repos",
            params=params,
            headers=self._get_headers()
        )
        return response.json()
    
    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        获取仓库详情
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
        
        Returns:
            Dict[str, Any]: 仓库详情
        """
        logger.info(f"获取仓库详情: {owner}/{repo}")
        response = self.get(
            f"/repos/{owner}/{repo}",
            headers=self._get_headers()
        )
        return response.json()
    
    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建 Issue
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            title: Issue 标题
            body: Issue 内容
            labels: 标签列表
            assignees: 负责人列表
        
        Returns:
            Dict[str, Any]: 创建的 Issue 信息
        """
        logger.info(f"创建 Issue: {owner}/{repo} - {title}")
        
        data = {"title": title}
        if body:
            data["body"] = body
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        
        response = self.post(
            f"/repos/{owner}/{repo}/issues",
            json_data=data,
            headers=self._get_headers()
        )
        return response.json()
    
    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取仓库的 Issue 列表
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            state: Issue 状态（open/closed/all）
            page: 页码（从 1 开始）
            per_page: 每页数量（最大 100）
        
        Returns:
            List[Dict[str, Any]]: Issue 列表
        """
        logger.info(f"获取 {owner}/{repo} 的 Issue 列表（状态: {state}）")
        params = {
            "state": state,
            "page": page,
            "per_page": min(per_page, 100),
            "sort": "created",
            "direction": "desc"
        }
        response = self.get(
            f"/repos/{owner}/{repo}/issues",
            params=params,
            headers=self._get_headers()
        )
        return response.json()
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """
        获取当前 API 频率限制状态
        
        Returns:
            Dict[str, Any]: 频率限制信息
        """
        logger.info("获取 API 频率限制状态")
        response = self.get(
            "/rate_limit",
            headers=self._get_headers()
        )
        return response.json()
    
    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        page: int = 1,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        搜索仓库
        
        Args:
            query: 搜索关键词
            sort: 排序方式（stars/forks/help-wanted-issues）
            order: 排序顺序（asc/desc）
            page: 页码（从 1 开始）
            per_page: 每页数量（最大 100）
        
        Returns:
            Dict[str, Any]: 搜索结果
        """
        logger.info(f"搜索仓库: {query}")
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": min(per_page, 100)
        }
        response = self.get(
            "/search/repositories",
            params=params,
            headers=self._get_headers()
        )
        return response.json()
