# Pytest 自动化测试框架

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4-green?logo=pytest)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CwtchToMe/pytest-api-framework/actions/workflows/test.yml/badge.svg)](https://github.com/CwtchToMe/pytest-api-framework/actions/workflows/test.yml)

基于 GitHub 平台的 Pytest 自动化测试框架，集成熔断器、限流器、插件系统等高级特性，**同时支持 API 测试和 Web UI 测试**。

## 项目定位

这是一个**全栈自动化测试框架**项目，用于测试 GitHub API 接口和 Web 页面。框架采用分层架构设计，实现了数据与方法的解耦：

**两大测试方向：**

| 测试类型 | 测试对象 | 技术栈 | 测试数量 |
|----------|----------|--------|----------|
| **API 测试** | GitHub REST API | Requests + Mock | 55 个 |
| **Web UI 测试** | GitHub Web 页面 | Selenium + POM | 10 个 |

**框架核心能力：**

- HTTP 请求封装（带重试、熔断、限流）
- 高级特性（熔断器、限流器、插件系统）
- 安全模块（敏感信息过滤、数据加密）
- Web UI 自动化（Selenium 页面对象模式）
- 数据驱动测试（YAML 数据文件）
- 测试报告生成（Allure）

## 项目特点

- **分层架构设计**：配置层、API 封装层、公共组件层、测试用例层、页面对象层、数据层
- **数据驱动测试**：测试数据与测试代码分离，支持 YAML 数据文件
- **高级特性**：熔断器、限流器、插件系统、敏感信息过滤
- **双测试模式**：API 测试和 Web UI 测试同等重要，独立运行
- **多环境支持**：dev/test/staging/prod 环境配置
- **完善的日志系统**：轮转日志、敏感信息自动脱敏
- **Allure 报告**：可视化测试报告，支持图表统计
- **CI/CD 集成**：GitHub Actions 自动化测试

## 目录结构

```
pytest-api-framework/
├── config/                    # 配置层
│   ├── __init__.py
│   └── config.py             # 多环境配置管理
├── api/                       # API 封装层
│   ├── __init__.py
│   ├── base_api.py           # API 基类
│   └── github_api.py         # GitHub API 封装
├── common/                    # 公共组件层
│   ├── __init__.py
│   ├── base_requests.py      # HTTP 请求基类（核心）
│   ├── circuit_breaker.py    # 熔断器
│   ├── rate_limiter.py       # 限流器
│   ├── plugin_system.py      # 插件系统
│   ├── security.py           # 安全模块
│   ├── secure_config.py      # 安全配置（加密）
│   └── yaml_util.py          # YAML 工具 + 数据加载器
├── page_objects/             # 页面对象层
│   ├── __init__.py
│   ├── base_page.py          # 页面基类
│   ├── login_page.py         # 登录页面
│   └── home_page.py          # 首页
├── test_cases/               # 测试用例层
│   ├── __init__.py
│   ├── api/                  # API 测试
│   │   ├── __init__.py
│   │   ├── test_github_api.py         # GitHub API 功能测试
│   │   ├── test_enterprise_features.py # 高级特性测试
│   │   └── test_stress_performance.py  # 压力性能测试
│   └── web/                  # Web UI 测试
│       ├── __init__.py
│       └── test_github_web.py         # GitHub Web 测试
├── data/                     # 数据层（数据驱动）
│   ├── api_test_data.yaml    # API 测试数据
│   ├── web_test_data.yaml    # Web UI 测试数据
│   └── framework_test_data.yaml # 框架测试数据
├── docs/                     # 文档目录
│   ├── GitHub_API接口文档.md
│   ├── 测试用例设计文档.md
│   └── 项目需求文档.md
├── .github/workflows/        # GitHub Actions CI/CD
│   └── test.yml
├── conftest.py               # Pytest 全局配置
├── pytest.ini                # Pytest 配置
├── pyproject.toml            # 项目配置（black/isort/mypy）
├── .pre-commit-config.yaml   # Git 钩子配置
├── .env.example              # 环境变量示例
├── requirements.txt          # 依赖列表
├── LICENSE                   # MIT 许可证
└── README.md                 # 项目说明
```

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              测试执行入口                                    │
│                         pytest / conftest.py                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│        API 测试流程          │   │       Web UI 测试流程        │
│    test_cases/api/           │   │    test_cases/web/           │
│                              │   │                              │
│  ┌────────────────────────┐  │   │  ┌────────────────────────┐  │
│  │  读取测试数据           │  │   │  │  读取测试数据           │  │
│  │  data/api_test_data.yaml│  │   │  │  data/web_test_data.yaml│  │
│  └────────────────────────┘  │   │  └────────────────────────┘  │
└──────────────────────────────┘   └──────────────────────────────┘
                    │                               │
                    ▼                               ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│      API 封装层              │   │      页面对象层              │
│  api/github_api.py           │   │  page_objects/               │
│  api/base_api.py             │   │  ├── base_page.py            │
└──────────────────────────────┘   │  ├── login_page.py           │
                    │               │  └── home_page.py            │
                    ▼               └──────────────────────────────┘
┌──────────────────────────────┐                   │
│    公共组件层                │                   ▼
│  common/                     │   ┌──────────────────────────────┐
│  ├── base_requests.py        │   │      Selenium WebDriver      │
│  ├── circuit_breaker.py      │   │      浏览器驱动              │
│  ├── rate_limiter.py         │   └──────────────────────────────┘
│  ├── plugin_system.py        │
│  ├── security.py             │
│  └── secure_config.py        │
└──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────┐
│      配置层                  │
│  config/config.py            │
│  .env 环境变量               │
└──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────┐
│      外部服务                │
│  GitHub API / GitHub Web     │
└──────────────────────────────┘
```

### 数据驱动设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据驱动测试架构                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   data/                                                                     │
│   ├── api_test_data.yaml      ─────────► test_cases/api/                   │
│   │   ├── users              用户数据        ├── test_github_api.py         │
│   │   ├── repositories       仓库数据        ├── test_enterprise_features.py │
│   │   ├── issues             Issue数据       └── test_stress_performance.py │
│   │   └── search             搜索数据                                       │
│   │                                                                         │
│   ├── web_test_data.yaml      ─────────► test_cases/web/                   │
│   │   ├── login              登录数据        └── test_github_web.py         │
│   │   ├── home               首页数据                                       │
│   │   └── elements           元素定位                                       │
│   │                                                                         │
│   └── framework_test_data.yaml ────────► common/ 测试                       │
│       ├── circuit_breaker    熔断器数据                                      │
│       ├── rate_limiter       限流器数据                                      │
│       └── security           安全模块数据                                    │
│                                                                             │
│   数据加载器：common/yaml_util.py → DataHelper 类                            │
│                                                                             │
│   使用示例：                                                                 │
│   from common.yaml_util import DataHelper                                   │
│   users = DataHelper.get_api_users()                                        │
│   login_data = DataHelper.get_web_login_data()                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### API 测试完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        API 测试执行流程                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  第 1 步：测试启动                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ pytest 读取 pytest.ini 配置                                         │   │
│  │ 加载 conftest.py 中的 fixtures                                       │   │
│  │ 读取 .env 环境变量                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 2 步：加载测试数据                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ DataHelper.load_api_data()                                           │   │
│  │ ├── 加载 data/api_test_data.yaml                                    │   │
│  │ └── 缓存数据，避免重复读取                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 3 步：创建 API 客户端                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ GitHubApi.__init__()                                                 │   │
│  │ ├── 调用 BaseApi.__init__()                                         │   │
│  │ │   └── 创建 BaseRequests 实例                                      │   │
│  │ │       ├── 初始化 CircuitBreaker (熔断器)                          │   │
│  │ │       ├── 初始化 RateLimiter (限流器)                             │   │
│  │ │       └── 初始化 PluginManager (插件管理器)                       │   │
│  │ └── 设置认证 headers                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 4 步：执行测试用例                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ test_get_user_info():                                                │   │
│  │ ├── users = DataHelper.get_api_users()                              │   │
│  │ ├── client.get_user(users['valid'][0]['username'])                  │   │
│  │ │   └── GitHubApi.get_user()                                        │   │
│  │ │       └── BaseApi.get("/users/octocat")                           │   │
│  │ │           └── BaseRequests.request("GET", url)                    │   │
│  │ │               ├── 检查熔断器状态                                   │   │
│  │ │               ├── 检查限流器                                       │   │
│  │ │               ├── 执行插件钩子 before_request()                   │   │
│  │ │               ├── 发送 HTTP 请求                                   │   │
│  │ │               ├── 执行插件钩子 after_request()                    │   │
│  │ │               └── 返回响应                                         │   │
│  │ └── assert user["login"] == "octocat"                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 5 步：生成测试报告                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ allure-pytest 收集测试结果                                           │   │
│  │ ├── 记录测试步骤                                                     │   │
│  │ ├── 记录断言结果                                                     │   │
│  │ └── 生成 allure-results/                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Web UI 测试完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Web UI 测试执行流程                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  第 1 步：测试启动                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ pytest 读取 pytest.ini 配置                                         │   │
│  │ 加载 conftest.py 中的 fixtures                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 2 步：加载测试数据                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ DataHelper.load_web_data()                                           │   │
│  │ ├── 加载 data/web_test_data.yaml                                    │   │
│  │ ├── 获取登录测试数据                                                 │   │
│  │ └── 获取页面元素定位                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 3 步：初始化 WebDriver                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 创建 Selenium WebDriver 实例                                         │   │
│  │ ├── driver = webdriver.Chrome()                                     │   │
│  │ └── 配置浏览器选项                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 4 步：创建页面对象                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ login_page = LoginPage(driver)                                       │   │
│  │ ├── 继承 BasePage                                                    │   │
│  │ ├── 加载页面元素定位                                                 │   │
│  │ └── 初始化 WebDriverWait                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 5 步：执行测试用例                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ test_login_success():                                                │   │
│  │ ├── login_data = DataHelper.get_web_login_data()                    │   │
│  │ ├── elements = DataHelper.get_web_elements('login_page')            │   │
│  │ ├── login_page.open_login_page()                                    │   │
│  │ │   └── driver.get("https://github.com/login")                      │   │
│  │ ├── login_page.login(username, password)                            │   │
│  │ │   ├── find_element(elements['username_input'])                    │   │
│  │ │   ├── element.send_keys(username)                                 │   │
│  │ │   ├── find_element(elements['password_input'])                    │   │
│  │ │   ├── element.send_keys(password)                                 │   │
│  │ │   └── find_element(elements['login_button']).click()              │   │
│  │ └── assert login successful                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  第 6 步：生成测试报告                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ allure-pytest 收集测试结果                                           │   │
│  │ ├── 截图保存                                                         │   │
│  │ └── 生成 allure-results/                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 核心功能

### 1. 熔断器 (Circuit Breaker)

三态模型实现，防止级联故障：

- **CLOSED（关闭）**：正常工作状态
- **OPEN（开启）**：熔断状态，快速失败
- **HALF_OPEN（半开）**：尝试恢复状态

```python
# 配置参数
failure_threshold = 5    # 失败阈值
timeout = 60            # 熔断超时时间（秒）
```

### 2. 限流器 (Rate Limiter)

三种算法实现：

| 算法 | 类 | 适用场景 |
|------|-----|---------|
| 滑动窗口 | `RateLimiter` | 精确控制请求频率 |
| 令牌桶 | `TokenBucket` | 允许突发流量 |
| 漏桶 | `LeakyBucket` | 平滑流量输出 |

### 3. 插件系统

生命周期钩子支持：

- `before_request` / `after_request`：请求前后处理
- `before_test` / `after_test`：测试前后处理
- `on_test_failure` / `on_test_success`：测试结果处理

内置插件：日志插件、指标插件、缓存插件

### 4. 安全模块

- 日志敏感信息自动过滤
- 数据脱敏工具（邮箱、手机号、密码等）
- Fernet 加密（AES-128）

### 5. 数据驱动测试

测试数据与代码分离，支持 YAML 数据文件：

```python
from common.yaml_util import DataHelper

# 加载 API 测试数据
users = DataHelper.get_api_users()
repos = DataHelper.get_api_repositories()

# 加载 Web 测试数据
login_data = DataHelper.get_web_login_data()
elements = DataHelper.get_web_elements('login_page')

# 加载框架测试数据
cb_data = DataHelper.get_circuit_breaker_data()
```

### 6. Web UI 自动化

- 基于 Selenium 的页面对象模式
- 支持多浏览器（Chrome、Firefox、Edge）
- 显式等待和隐式等待
- 截图和日志记录

## 快速开始

### 环境要求

- Python 3.8+
- pip
- Chrome/Firefox 浏览器（Web UI 测试需要）

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/CwtchToMe/pytest-api-framework.git
cd pytest-api-framework

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 pre-commit 钩子（可选）
pip install pre-commit
pre-commit install
```

### 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件
GITHUB_API_URL=https://api.github.com
GITHUB_TOKEN=your_github_token_here
TEST_GITHUB_USER=octocat
```

### 运行测试

```bash
# 运行所有测试
pytest

# 只运行 API 测试
pytest test_cases/api/ -v

# 只运行 Web UI 测试
pytest test_cases/web/ -v

# 生成 Allure 报告
pytest --alluredir=./allure-results
allure serve allure-results
```

## 文档说明

本项目的文档来源如下：

| 文档 | 来源 | 说明 |
|------|------|------|
| [GitHub_API接口文档.md](docs/GitHub_API接口文档.md) | [GitHub REST API 官方文档](https://docs.github.com/en/rest) | 基于 GitHub 官方 API 文档整理，包含本项目测试涉及的所有接口 |
| [测试用例设计文档.md](docs/测试用例设计文档.md) | 根据项目需求编写 | 包含测试范围、测试策略、测试用例清单、测试数据设计 |
| [项目需求文档.md](docs/项目需求文档.md) | 根据项目目标编写 | 包含功能需求、非功能需求、架构设计、验收标准 |

### 文档结构

```
docs/
├── GitHub_API接口文档.md    # API 接口文档
│   ├── API 概述（Base URL、认证方式、频率限制）
│   ├── 用户相关接口（获取用户信息、仓库列表等）
│   ├── 仓库相关接口（获取仓库详情、搜索仓库）
│   ├── Issue 相关接口（获取列表、创建 Issue）
│   ├── 频率限制接口
│   ├── 错误响应说明
│   └── 分页机制
│
├── 测试用例设计文档.md      # 测试用例设计
│   ├── 测试范围（API 测试、Web UI 测试）
│   ├── 测试用例清单（按模块分类）
│   ├── 测试数据设计
│   ├── 测试策略（Mock 测试策略）
│   └── 测试执行说明
│
└── 项目需求文档.md          # 项目需求规格
    ├── 项目概述（背景、目标、技术栈）
    ├── 功能需求（API 测试、Web 测试、高级特性）
    ├── 非功能需求（性能、可维护性、可扩展性）
    ├── 架构设计（分层架构、模块职责）
    └── 验收标准
```

### 文档与代码的对应关系

```
docs/GitHub_API接口文档.md  ──────►  api/github_api.py
                                   (API 接口封装)

docs/测试用例设计文档.md    ──────►  test_cases/
                                   (测试用例实现)

docs/项目需求文档.md        ──────►  整体项目架构
                                   (分层设计、模块划分)
```

## 测试用例

当前共 **65 个测试用例**，API 测试和 Web UI 测试同等重要：

### API 测试（55 个）

| 模块 | 测试数量 | 覆盖内容 |
|------|----------|----------|
| 用户功能 | 4 | 用户信息、认证用户、仓库列表 |
| 仓库功能 | 2 | 仓库详情、异常处理 |
| 搜索功能 | 2 | 仓库搜索、空结果处理 |
| Issue 功能 | 3 | Issue 列表、创建、状态筛选 |
| 频率限制 | 1 | API 频率限制状态 |
| 高级特性 | 18 | 熔断器、限流器、插件、安全模块 |
| 压力测试 | 4 | 高并发、持续压力、负载测试 |
| 性能测试 | 2 | 响应时间、并发请求 |

### Web UI 测试（10 个）

| 模块 | 测试数量 | 覆盖内容 |
|------|----------|----------|
| 登录功能 | 3 | 登录成功、登录失败、表单验证 |
| 首页功能 | 4 | 页面加载、导航、搜索、仓库列表 |
| 用户操作 | 3 | 个人中心、仓库创建、设置 |

## 关于覆盖率

本项目是一个**测试框架**，API 层覆盖率达到 **95%**：

- **GitHub API 封装层**：95% 覆盖率
- **核心业务逻辑**：充分测试
- **高级特性**：熔断器、限流器、插件系统均有测试

在实际工作中：
- **测试人员**通常无法访问业务代码，只能测试 API 接口
- **开发人员**负责业务代码的单元测试和覆盖率
- **本项目**展示的是测试框架的开发能力

## CI/CD 集成

项目使用 GitHub Actions 进行持续集成：

- **多 Python 版本测试**：3.8、3.9、3.10、3.11
- **自动覆盖率报告**：上传至 Codecov
- **Allure 报告**：自动部署至 GitHub Pages
- **代码质量检查**：black、isort、flake8、mypy

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 测试框架 | pytest | 7.4 |
| HTTP 请求 | requests | 2.31 |
| Web 自动化 | selenium | 4.15 |
| 测试报告 | allure-pytest | 2.13 |
| 数据生成 | Faker | 20.1 |
| 加密 | cryptography | 41.0 |
| 配置管理 | python-dotenv | 1.0 |
| 数据格式 | PyYAML | 6.0 |

## 许可证

[MIT License](LICENSE)
