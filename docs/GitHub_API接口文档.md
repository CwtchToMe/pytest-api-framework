# GitHub API 接口文档

## 一、API 概述

GitHub REST API v3 是 GitHub 提供的官方 API 接口，用于程序化访问 GitHub 资源。

- **Base URL**: `https://api.github.com`
- **认证方式**: Personal Access Token (PAT)
- **请求格式**: JSON
- **响应格式**: JSON
- **频率限制**: 认证用户 5000 次/小时，未认证 60 次/小时

## 二、认证方式

### Personal Access Token

```http
Authorization: token ghp_xxxxxxxxxxxxxxxxxxxx
```

### 请求头

```http
Accept: application/vnd.github.v3+json
User-Agent: AutoTest-Framework/1.0
```

## 三、用户相关接口

### 1. 获取指定用户信息

```http
GET /users/{username}
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | GitHub 用户名 |

**响应示例:**

```json
{
  "login": "octocat",
  "id": 583231,
  "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=3",
  "html_url": "https://github.com/octocat",
  "type": "User",
  "name": "The Octocat",
  "company": "GitHub",
  "blog": "https://github.blog",
  "location": "San Francisco",
  "public_repos": 8,
  "followers": 5000,
  "following": 9
}
```

### 2. 获取当前认证用户

```http
GET /user
```

**需要认证**: 是

**响应示例:**

```json
{
  "login": "testuser",
  "id": 123456,
  "name": "Test User",
  "email": "test@example.com"
}
```

### 3. 获取用户仓库列表

```http
GET /users/{username}/repos
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | GitHub 用户名 |
| type | string | 否 | all, owner, member (默认: owner) |
| sort | string | 否 | created, updated, pushed, full_name (默认: full_name) |
| direction | string | 否 | asc, desc |
| per_page | int | 否 | 每页数量 (默认: 30, 最大: 100) |
| page | int | 否 | 页码 |

### 4. 获取当前用户仓库列表

```http
GET /user/repos
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| visibility | string | 否 | all, public, private |
| affiliation | string | 否 | owner, collaborator, organization_member |
| type | string | 否 | all, owner, public, private, member |
| sort | string | 否 | created, updated, pushed, full_name |
| direction | string | 否 | asc, desc |
| per_page | int | 否 | 每页数量 |
| page | int | 否 | 页码 |

## 四、仓库相关接口

### 1. 获取仓库详情

```http
GET /repos/{owner}/{repo}
```

**响应示例:**

```json
{
  "id": 123456,
  "name": "Hello-World",
  "full_name": "octocat/Hello-World",
  "private": false,
  "owner": {
    "login": "octocat",
    "id": 583231
  },
  "html_url": "https://github.com/octocat/Hello-World",
  "description": "My first repository on GitHub!",
  "stargazers_count": 80,
  "watchers_count": 80,
  "language": "JavaScript",
  "forks_count": 9,
  "open_issues_count": 0,
  "license": {
    "key": "mit",
    "name": "MIT License"
  }
}
```

### 2. 搜索仓库

```http
GET /search/repositories
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| q | string | 是 | 搜索关键词 |
| sort | string | 否 | stars, forks, help-wanted-issues |
| order | string | 否 | asc, desc (默认: desc) |
| per_page | int | 否 | 每页数量 |
| page | int | 否 | 页码 |

**响应示例:**

```json
{
  "total_count": 1000,
  "incomplete_results": false,
  "items": [
    {
      "id": 789012,
      "name": "django",
      "full_name": "django/django",
      "stargazers_count": 70000,
      "language": "Python"
    }
  ]
}
```

## 五、Issue 相关接口

### 1. 获取仓库 Issue 列表

```http
GET /repos/{owner}/{repo}/issues
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| owner | string | 是 | 仓库所有者 |
| repo | string | 是 | 仓库名称 |
| state | string | 否 | open, closed, all (默认: open) |
| labels | string | 否 | 标签名称，逗号分隔 |
| sort | string | 否 | created, updated, comments |
| direction | string | 否 | asc, desc |
| per_page | int | 否 | 每页数量 |
| page | int | 否 | 页码 |

### 2. 创建 Issue

```http
POST /repos/{owner}/{repo}/issues
```

**请求体:**

```json
{
  "title": "Found a bug",
  "body": "I'm having a problem with this.",
  "labels": ["bug", "help wanted"],
  "assignees": ["octocat"]
}
```

**响应示例:**

```json
{
  "id": 1,
  "number": 1347,
  "title": "Found a bug",
  "body": "I'm having a problem with this.",
  "state": "open",
  "user": {
    "login": "octocat",
    "id": 1
  },
  "labels": [
    {
      "id": 208045946,
      "name": "bug",
      "color": "f29513"
    }
  ],
  "html_url": "https://github.com/octocat/Hello-World/issues/1347"
}
```

## 六、频率限制接口

### 获取当前频率限制状态

```http
GET /rate_limit
```

**响应示例:**

```json
{
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
    }
  },
  "rate": {
    "limit": 5000,
    "remaining": 4999,
    "reset": 1774871400
  }
}
```

## 七、错误响应

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 成功（无内容） |
| 400 | 请求格式错误 |
| 401 | 未授权 |
| 403 | 权限不足或频率限制 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest"
}
```

## 八、分页

### Link Header

```http
Link: <https://api.github.com/repos/octocat/Hello-World/issues?page=2>; rel="next",
      <https://api.github.com/repos/octocat/Hello-World/issues?page=5>; rel="last"
```

### 分页参数

- `page`: 页码（从 1 开始）
- `per_page`: 每页数量（默认 30，最大 100）
