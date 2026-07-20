# pytest-api-framework — TakeoutSystem 外卖系统自动化测试框架

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-9.1-green?logo=pytest)](https://pytest.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-brightgreen?logo=selenium)](https://selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

面向 **TakeoutSystem 外卖点餐系统** 的全链路自动化测试框架，覆盖后端 REST API 与三个前端应用（H5/商家端/管理后台）。

**核心特色：** Mock/真实双模式 | 插件化 HTTP 客户端 | 熔断器+限流器 | Allure 报告 | 多端 UI 覆盖 | 零 time.sleep

## 测试覆盖

| 测试类型 | 覆盖范围 | 技术栈 | 数量 |
|----------|----------|--------|:----:|
| **API 测试** | 认证/商家/商品/购物车/订单/支付/评价/优惠券/收藏/健康检查 | Requests + Mock | **38 + 4 xpass** |
| **UI 测试** | H5 消费者端 / 商家端 / 管理后台 | Selenium + Page Object | **19 + 1 xfail** |
| **预期失败** | 已知后端缺陷 | xfail 标记 | **3** |
| **意外通过** | 已修复的后端缺陷 | xpass 跟踪 | **4** |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制环境配置
cp .env.example .env

# 3. 运行 API 测试（Mock 模式，无需后端）
python -m pytest test_cases/api/ -v

# 4. 运行 API 测试（真实模式，需后端 :8080）
USE_MOCK=false python -m pytest test_cases/api/ -v

# 5. 运行 UI 测试（可见浏览器窗口）
USE_MOCK=false ENV=dev python -m pytest test_cases/web/ -v

# 6. 运行全部测试
./run_tests.sh all real
```

## 项目结构

```
pytest-api-framework/
├── config/
│   └── config.py                    # 多环境配置（dev/test/staging/prod）
│
├── api/                             # API 封装层（API Object 模式）
│   ├── base_api.py                  # API 基类（@allure.step + 统一日志）
│   └── takeout_api.py              # 10 个业务 API 类（Auth/Merchant/Product/Cart/Order/...）
│
├── common/                          # 基础工具层
│   ├── base_requests.py            # HTTP 引擎（requests.Session + 重试 + 插件钩子）
│   ├── mock_util.py                # Mock 模式切换（session 层 patch）
│   ├── security.py                 # 敏感信息脱敏
│   ├── test_helpers.py             # 统一登录（get_customer_token / get_merchant_token）
│   ├── yaml_util.py                # YAML 测试数据加载
│   ├── circuit_breaker.py          # 熔断器（三态状态机）
│   ├── rate_limiter.py             # 限流器（滑动窗口）
│   └── plugins/                    # 插件系统
│       ├── core/                   # 熔断器、限流器（不可禁用）
│       └── normal/                 # 日志、Allure 附件（可禁用）
│
├── page_objects/                   # 页面对象层（Page Object 模式）
│   ├── base_page.py                # Selenium 基类（显式等待，零 time.sleep）
│   ├── h5/                         # H5 端 — 7 个页面（登录/首页/商家详情/购物车/结算/订单/我的）
│   ├── merchant_web/              # 商家端 — 3 个页面（登录/订单/店铺管理）
│   └── admin_web/                 # 管理后台 — 4 个页面（登录/商家/订单/用户管理）
│
├── test_cases/
│   ├── api/                        # API 测试（4 个模块，44 个测试）
│   │   ├── test_auth_api.py              # 认证模块
│   │   ├── test_merchant_product_api.py  # 商家+商品
│   │   ├── test_order_flow_api.py        # 购物车→订单→支付→评价
│   │   └── test_user_coupon_favorite_api.py  # 用户+优惠券+收藏
│   │
│   └── web/                        # UI 测试（3 个文件，20 个综合测试）
│       ├── conftest.py             # WebDriver fixture（module 共享浏览器）
│       ├── test_h5_ui.py           # H5 端 12 个测试（登录→首页→搜索→商家→加购→下单→...）
│       ├── test_merchant_web_ui.py # 商家端 4 个测试（登录→订单→店铺→订单处理）
│       └── test_admin_web_ui.py    # 管理后台 4 个测试（登录→商家→订单→用户）
│
├── conftest.py                     # 全局 pytest 配置（--mock/--env + 健康检查）
├── pytest.ini                      # markers / 日志 / addopts
├── pyproject.toml                  # 项目元数据与依赖
├── requirements.txt                # pip 依赖锁
├── .env.example                    # 环境配置模板
├── .gitignore
└── run_tests.sh                    # 批量运行脚本
```

## 运行指南

### 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 Redis 短信验证码（真实模式需要）
redis-cli SET "sms:code:13800000003" "123456" EX 3600
redis-cli SET "sms:code:13800000002" "123456" EX 3600
redis-cli SET "sms:code:13800000001" "123456" EX 3600
```

### 运行命令

```bash
# ---- API 测试 ----

# Mock 模式（不需要后端）
python -m pytest test_cases/api/ -v

# 真实模式（需要后端 :8080）
USE_MOCK=false python -m pytest test_cases/api/ -v

# ---- UI 测试 ----

# 无头模式（CI 环境）
USE_MOCK=false python -m pytest test_cases/web/ -v

# 可见浏览器模式（看测试过程）
USE_MOCK=false ENV=dev python -m pytest test_cases/web/ -v

# ---- 批量运行 ----
./run_tests.sh api real       # API 真实模式
./run_tests.sh ui real        # UI 真实模式（看得见浏览器）
./run_tests.sh all mock       # 全量 Mock 模式
```

### 常用参数

| 参数 | 说明 |
|------|------|
| `-v` | 显示每个测试名称和结果 |
| `--tb=short` | 失败时短错误 |
| `-k "login or order"` | 按名称过滤测试 |
| `-m "smoke"` | 按 marker 过滤 |
| `-p no:warnings` | 关闭告警噪音 |
| `--alluredir=reports/allure-results` | 生成 Allure 报告数据 |

## CI/CD 集成

项目已集成 **GitHub Actions** 自动化 CI/CD 流水线，配置见 `.github/workflows/test.yml`。

### 触发方式

| 触发方式 | API 测试 | UI 测试 | Allure 报告 | 适用场景 |
|---------|:--------:|:-------:|:----------:|---------|
| **Push / PR** (main/develop) | ✅ Mock 模式 | ❌ 不运行 | ✅ 生成 | 提交时快速验证 |
| **每日定时** (06:00 UTC+8) | ✅ | ✅ 需外部服务 | ✅ 发布到 Pages | 全量回归 |
| **手动 workflow_dispatch** | 按需选择 | 按需选择 | ✅ | 灵活组合 |

### 分层测试策略

- **API 测试**（`test_cases/api/`）：始终使用 **Mock 模式**（`USE_MOCK=true`），无需任何后端服务，CI 中 5 分钟内完成
- **UI 测试**（`test_cases/web/`）：需要部署的前端服务和后端 API，仅在**定时构建**和**手动触发**时运行
- **代码风格检查**：`black` + `isort` 自动校验代码格式

### 流水线 Job 说明

```yaml
lint          # 代码风格检查（black + isort）
api-tests     # API Mock 测试（pytest-xdist 并行）
ui-tests      # UI 测试（Chrome Headless，需外部环境）
allure-report # Allure 报告生成 → GitHub Pages 发布
notify        # 失败通知（支持 Slack Webhook）
```

### Allure 报告

测试通过后，Allure 报告自动部署到 GitHub Pages：
`https://<你的用户名>.github.io/pytest-api-framework/allure-report/`

也可在 Actions 运行页面下载 `allure-report` Artifact 本地查看。

### 手动触发测试

在 GitHub 仓库页面 → **Actions** → **TakeoutSystem CI/CD** → **Run workflow**，可选择：
- **测试范围**：`api` / `ui` / `full`
- **Mock 模式**：是否启用 Mock

### 配置外部 UI 环境（可选）

UI 测试需要部署的前端服务。在 GitHub 仓库 **Settings → Secrets and variables → Actions** 中配置：

| Secret | 说明 | 默认值 |
|--------|------|--------|
| `H5_BASE_URL` | H5 前端地址 | `http://localhost:3001` |
| `MERCHANT_BASE_URL` | 商家端地址 | `http://localhost:3002` |
| `ADMIN_BASE_URL` | 管理后台地址 | `http://localhost:3003` |
| `TAKEOUT_API_URL` | 后端 API 地址 | `http://localhost:8080` |
| `SLACK_WEBHOOK` | Slack 通知（可选） | — |

也可以使用 `docker-compose.ci.yml` 在本地或 CI 中拉起完整环境。

## 架构设计

### 分层架构

```
测试用例层 (test_cases/)
    │
    ├── 调用 API 封装层 (api/takeout_api.py)
    │       └── 继承 BaseApi → common/base_requests.py (HTTP + 插件)
    │
    └── 调用页面对象层 (page_objects/*.py)
            └── 继承 BasePage (Selenium + 显式等待)
```

### 复用机制

| 层级 | 复用内容 | 省去的工作 |
|------|----------|-----------|
| **fixture** | `mobile_driver` / `desktop_driver`（scope=module） | 浏览器启动/配置/关闭全自动 |
| **Page 继承** | `BasePage.click()` / `input_text()` / `wait_for_*()` / `is_visible()` | 显式等待、超时控制、异常处理 |
| **API 继承** | `BaseApi.get()` / `post()` / `put()` / `delete()` | HTTP 会话、日志、allure 附件 |
| **test_helpers** | `get_customer_token()` / `get_merchant1_token()` / `get_admin_token()` | Token 获取与缓存 |
| **config** | `API_BASE_URL` / `TEST_SMS_CODE` / `H5_BASE_URL` / `ENV` | 环境差异统一管理 |
| **YAML 数据** | `api_test_data.yaml` / `web_test_data.yaml` | 测试数据与代码分离 |

### 高效等待策略

所有页面操作使用 Selenium 显式等待（`WebDriverWait` + `expected_conditions`），**没有 `time.sleep`**：

```python
# 不用 time.sleep(1)
self.wait.until(EC.element_to_be_clickable(locator)).click()

# 不用 time.sleep(2)
self.wait_for_url_not_contains("/login")

# 不用 time.sleep(3)
self.wait_for_text(self.MERCHANT_NAME, timeout=8)
```

## 测试账号

| 角色 | 手机号 | 验证码 | 用途 |
|------|--------|--------|------|
| 普通用户 | 13800000003 | 123456 | API 认证、H5 UI |
| 商家1（辣味馆） | 13800000002 | 123456 | 商家 API、商家端 UI |
| 商家2（快乐汉堡） | 13800000004 | 123456 | 多商家场景 |
| 平台管理员 | 13800000001 | 123456 | 管理后台 UI |

## 技术栈

| 依赖 | 用途 | 关键能力 |
|------|------|----------|
| pytest 9.1 | 测试框架 | fixture / parametrize / xfail / marker |
| requests | HTTP 客户端 | Session 复用、重试策略 |
| selenium 4 | 浏览器自动化 | Page Object、CDP、显式等待 |
| allure-pytest | 测试报告 | 步骤追踪、请求/响应附件 |
| webdriver-manager | ChromeDriver 管理 | 自动下载匹配版本 |
| PyYAML + Faker | 数据管理 | 数据驱动、随机生成 |
| python-dotenv | 环境变量 | .env 文件加载 |

## 已知问题（xfail）

| 测试 | 文件 | 问题描述 |
|------|------|----------|
| `test_add_dish_negative_price` | test_merchant_product_api | 后端未校验 `price<0` |
| `test_claim_coupon` | test_user_coupon_favorite_api | 优惠券领取接口异常 |
| `test_merchant_detail_browse` | test_h5_ui | Vue SPA token 重定向问题 |
