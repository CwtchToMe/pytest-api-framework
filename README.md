# Pytest 自动化测试框架

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4-green?logo=pytest)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 GitHub 平台的 Pytest 自动化测试框架，集成熔断器、限流器、插件系统等高级特性，**同时支持 API 测试和 Web UI 测试**。

## 项目定位

这是一个**全栈自动化测试框架**项目，用于测试 GitHub API 接口和 Web 页面。框架采用分层架构设计，实现了数据与方法的解耦：

**两大测试方向：**

| 测试类型 | 测试对象 | 技术栈 | 测试数量 |
|----------|----------|--------|----------|
| **API 测试** | GitHub REST API | Requests + Mock | 77 个 |
| **Web UI 测试** | GitHub Web 页面 | Selenium + Mock | 19 个 |

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
- **"硬逻辑 + 软钩子"插件系统**：核心插件强制加载，普通插件可选加载
- **双测试模式**：API 测试和 Web UI 测试同等重要，独立运行
- **多环境支持**：dev/test/staging/prod 环境配置
- **完善的日志系统**：轮转日志、敏感信息自动脱敏
- **Allure 报告**：可视化测试报告，支持图表统计

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
│   ├── plugin_system.py      # 插件系统入口
│   ├── security.py           # 安全模块
│   ├── secure_config.py      # 安全配置（加密）
│   ├── yaml_util.py          # YAML 工具 + 数据加载器
│   ├── data_generator.py     # Faker 数据生成器
│   └── plugins/              # 插件系统
│       ├── base.py           # 插件基类
│       ├── manager.py        # 插件管理器
│       ├── core/             # 核心插件（不可禁用）
│       │   ├── circuit_breaker.py  # 熔断器插件
│       │   └── rate_limiter.py     # 限流器插件
│       └── normal/           # 普通插件（可禁用）
│           ├── logging_plugin.py   # 日志插件
│           ├── metrics_plugin.py   # 指标插件
│           └── cache_plugin.py     # 缓存插件
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
│   │   ├── test_stress_performance.py  # 压力性能测试
│   │   └── test_boundary_and_invalid.py # 边界值和异常测试
│   └── web/                  # Web UI 测试
│       ├── __init__.py
│       └── test_github_web.py         # GitHub Web 测试
├── data/                     # 数据层（数据驱动）
│   ├── api_test_data.yaml    # API 测试数据
│   ├── web_test_data.yaml    # Web UI 测试数据
│   ├── framework_test_data.yaml # 框架测试数据
│   ├── boundary_test_data.yaml  # 边界值测试数据
│   └── invalid_test_data.yaml   # 异常测试数据
├── docs/                     # 文档目录
│   ├── GitHub_API接口文档.md
│   ├── 测试用例设计文档.md
│   ├── 项目需求文档.md
│   ├── 数据管理指南.md
│   └── 插件系统指南.md
├── .github/workflows/        # GitHub Actions CI/CD
│   └── test.yml              # 自动化测试配置
├── .gitignore               # Git 忽略配置
├── conftest.py               # Pytest 全局配置
├── pytest.ini                # Pytest 配置
├── pyproject.toml            # 项目配置（black/isort/mypy/coverage）
├── .pre-commit-config.yaml   # Git 钩子配置
├── .env.example              # 环境变量示例
├── requirements.txt          # 依赖列表
├── LICENSE                   # MIT 许可证
└── README.md                 # 项目说明

# 以下目录为运行时自动生成，无需提交到 Git
# .pytest_cache/    - pytest 缓存
# allure-report/    - Allure HTML 报告
# allure-results/   - Allure 原始结果
# logs/             - 日志文件
# reports/          - 测试报告
# __pycache__/      - Python 缓存
# .venv/            - 虚拟环境
```

## 核心功能

### 1. 插件系统（"硬逻辑 + 软钩子"模式）

参考 Pytest、Scrapy 等顶级框架的设计理念：

| 插件类型 | 插件名称 | 功能 | 可禁用 |
|----------|----------|------|--------|
| **核心插件** | CircuitBreakerPlugin | 熔断器保护 | ❌ 不可禁用 |
| **核心插件** | RateLimiterPlugin | 限流器控制 | ❌ 不可禁用 |
| 普通插件 | LoggingPlugin | 日志记录 | ✅ 可禁用 |
| 普通插件 | MetricsPlugin | 指标收集 | ✅ 可禁用 |
| 普通插件 | CachePlugin | 请求缓存 | ✅ 可禁用 |

**钩子接口：**

```python
class Plugin:
    # 生命周期钩子
    def on_load(self): pass
    def on_enable(self): pass
    def on_disable(self): pass
    
    # 请求钩子
    def before_request(self, method, url, **kwargs): pass
    def after_request(self, response, method, url, **kwargs): pass
    def on_request_error(self, error, method, url, **kwargs): pass
    
    # 测试钩子
    def before_test(self, test_name): pass
    def after_test(self, test_name, result): pass
    def on_test_failure(self, test_name, error): pass
    def on_test_success(self, test_name): pass
```

### 2. 熔断器 (Circuit Breaker)

三态模型实现，防止级联故障：

```
CLOSED（关闭）──失败次数达到阈值──► OPEN（开启）
      ▲                              │
      │                              │ 超时后
      │                              ▼
      └────成功──── HALF_OPEN（半开）
```

**配置参数：**
- `failure_threshold = 5`：失败阈值
- `timeout = 60`：熔断超时时间（秒）

### 3. 限流器 (Rate Limiter)

三种算法实现：

| 算法 | 类 | 适用场景 |
|------|-----|---------|
| 滑动窗口 | `RateLimiter` | 精确控制请求频率 |
| 令牌桶 | `TokenBucket` | 允许突发流量 |
| 漏桶 | `LeakyBucket` | 平滑流量输出 |

**默认配置：** 100 次请求 / 60 秒

### 4. 安全模块

- 日志敏感信息自动过滤
- 数据脱敏工具（邮箱、手机号、密码等）
- Fernet 加密（AES-128）

### 5. 数据驱动测试

测试数据与代码分离，支持 YAML 数据文件：

```python
from common.yaml_util import DataHelper

# 加载 API 测试数据
api_data = DataHelper.load_api_data()
users = DataHelper.get_api_users()

# 加载 Web 测试数据
web_data = DataHelper.load_web_data()
login_data = DataHelper.get_web_login_data()

# 加载边界值数据
boundary_data = DataHelper.load_boundary_data()

# 加载异常测试数据
invalid_data = DataHelper.load_invalid_data()
```

### 6. 数据生成器

使用 Faker 生成随机测试数据：

```python
from common.data_generator import DataGenerator

# 生成随机用户
user = DataGenerator.generate_github_user()

# 生成随机仓库
repo = DataGenerator.generate_github_repository()

# 生成随机 Issue
issue = DataGenerator.generate_github_issue()

# 设置随机种子（可重复）
DataGenerator.set_seed(12345)
```

## 快速开始

### 环境要求

- Python 3.8+
- pip

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
# 运行所有测试（96 个测试用例）
pytest

# 只运行 API 测试
pytest test_cases/api/ -v

# 只运行 Web UI 测试
pytest test_cases/web/ -v

# 禁用普通插件（核心插件不可禁用）
pytest --disable-plugins

# 生成 Allure 报告
pytest --alluredir=./allure-results
allure serve allure-results
```

## 测试用例

当前共 **96 个测试用例**，全部通过：

### API 测试（80 个）

| 模块 | 测试数量 | 覆盖内容 |
|------|----------|----------|
| 用户功能 | 6 | 用户信息、认证用户、仓库列表、无效用户 |
| 仓库功能 | 2 | 仓库详情、异常处理 |
| 搜索功能 | 2 | 仓库搜索、空结果处理 |
| Issue 功能 | 4 | Issue 列表、创建、状态筛选 |
| 频率限制 | 1 | API 频率限制状态 |
| 错误响应 | 4 | HTTP 错误响应测试 |
| 高级特性 | 21 | 熔断器、限流器、插件系统、安全模块、配置验证 |
| 压力测试 | 6 | 高并发、持续压力、负载测试、性能基准 |
| 边界值测试 | 4 | 用户名、星标数、Issue 标题、频率限制边界 |
| 异常测试 | 30 | SQL 注入、XSS 攻击、无效邮箱、特殊字符、类型错误 |

### Web UI 测试（16 个）

| 模块 | 测试数量 | 覆盖内容 |
|------|----------|----------|
| 登录功能 | 4 | 登录成功、登录失败、表单验证、空用户名 |
| 首页功能 | 4 | 页面加载、导航、搜索、仓库列表 |
| 用户操作 | 2 | 个人中心、设置导航 |
| 仓库页面 | 2 | 创建仓库数据、页面元素定位 |
| 通用元素 | 1 | 通用元素定位 |
| 配置测试 | 3 | 超时配置、截图配置、首页导航元素 |

## 数据文件使用情况

所有 YAML 数据文件 100% 被测试使用：

| 数据文件 | 数据节点数 | 使用率 |
|----------|------------|--------|
| api_test_data.yaml | 11 | 100% |
| web_test_data.yaml | 14 | 100% |
| framework_test_data.yaml | 13 | 100% |
| boundary_test_data.yaml | 4 | 100% |
| invalid_test_data.yaml | 6 | 100% |

## 测试策略

### Mock 测试策略

由于 GitHub API 有频率限制，本项目采用 Mock 测试策略：

| 限制类型 | 频率 | Mock 策略 |
|----------|------|----------|
| 未认证 | 60 次/小时 | 使用 Mock 模拟响应 |
| 已认证 | 5000 次/小时 | 使用 Mock 模拟响应 |

**Mock 测试优势：**
- 避免 GitHub API 频率限制
- 测试结果稳定可重复
- 测试速度快（96 个测试约 14 秒）
- CI/CD 流程稳定可靠

## CI/CD 集成

项目配置了 GitHub Actions 自动化测试（`.github/workflows/test.yml`）：

| 功能 | 说明 |
|------|------|
| **多版本测试** | Python 3.8, 3.9, 3.10, 3.11 |
| **代码覆盖率** | pytest-cov 生成覆盖率报告 |
| **Allure 报告** | 自动部署到 GitHub Pages |
| **Codecov** | 上传覆盖率到 Codecov |

**触发条件：**
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支

**使用方式：**
1. 将项目推送到 GitHub
2. 在 GitHub 仓库中启用 Actions
3. 配置 GitHub Pages（可选，用于 Allure 报告）

## 代码质量工具

项目配置了 pre-commit 钩子（`.pre-commit-config.yaml`），在提交代码前自动执行代码检查：

| 工具 | 功能 |
|------|------|
| **black** | Python 代码格式化 |
| **isort** | import 语句排序 |
| **flake8** | 代码风格检查 |
| **mypy** | 静态类型检查 |
| **check-yaml** | YAML 文件语法检查 |
| **trailing-whitespace** | 删除行尾空白 |

**使用方式：**

```bash
# 安装 pre-commit
pip install pre-commit

# 在项目中安装 git 钩子
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

## 文档说明

| 文档 | 说明 |
|------|------|
| [GitHub_API接口文档.md](docs/GitHub_API接口文档.md) | GitHub REST API 接口文档 |
| [测试用例设计文档.md](docs/测试用例设计文档.md) | 测试范围、策略、用例清单 |
| [项目需求文档.md](docs/项目需求文档.md) | 功能需求、非功能需求、验收标准 |
| [数据管理指南.md](docs/数据管理指南.md) | 数据架构、使用场景、API 参考 |
| [插件系统指南.md](docs/插件系统指南.md) | 插件架构、接口定义、使用示例 |

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
