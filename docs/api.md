# pytest-api-framework 接口测试架构文档

> 版本：2.0 | 最后更新：2026-07-11 | 覆盖范围：API 接口测试层

---

## 目录

1. [架构总览](#1-架构总览)
2. [分层架构详解](#2-分层架构详解)
3. [请求-响应生命周期](#3-请求-响应生命周期)
4. [测试用例结构](#4-测试用例结构)
5. [Mock / 真实双模式设计](#5-mock--真实双模式设计)
6. [插件系统](#6-插件系统)
7. [配置系统](#7-配置系统)
8. [公共 Fixture](#8-公共-fixture)
9. [架构评估与改进记录](#9-架构评估与改进记录)

---

## 1. 架构总览

### 1.1 设计目标

框架针对 **TakeoutSystem 外卖点餐系统** 后端 API（Spring Boot, `localhost:8080`）设计，核心目标：

| 目标 | 说明 |
|------|------|
| **接口与 UI 双覆盖** | 同一框架同时支持 HTTP 接口（requests）和浏览器 UI（selenium） |
| **Mock/真实双模式** | 不依赖后端即可运行（Mock），也可对接真实环境验证完整链路 |
| **插件化扩展** | 日志、Allure 附件等横切关注点通过插件挂载，核心代码零侵入 |
| **数据驱动** | 测试数据存于 YAML，通过 `@pytest.mark.parametrize` 实现数据与逻辑分离 |

### 1.2 三层架构总览

```
┌─────────────────────────────────────────────────┐
│                测试用例层                         │
│  test_auth_api  test_merchant_product_api        │
│  test_order_flow_api  test_user_coupon_favorite  │
├─────────────────────────────────────────────────┤
│                 API 对象层                        │
│  BaseApi (get/post/put/delete + Allure 装饰)      │
│  AuthApi  UserApi  CartApi  OrderApi ...         │
├─────────────────────────────────────────────────┤
│               HTTP 传输层                         │
│  BaseRequests (Session + 重试 + 插件钩子链)       │
├──────────────┬──────────────────────────────────┤
│  common/     │  config/        data/             │
│  mock_util   │  config.py      api_test_data.yaml│
│  test_helpers│  .env                             │
│  yaml_util   │                                   │
└──────────────┴──────────────────────────────────┘
```

### 1.3 目录结构（API 相关）

```
pytest-api-framework/
├── api/                          # API 对象层
│   ├── base_api.py               # BaseApi 基类（支持 requests 注入复用）
│   └── takeout_api.py            # 11 个业务 API 类
│
├── common/                       # 基础工具层
│   ├── base_requests.py          # HTTP 执行引擎（Session + 插件钩子）
│   ├── mock_util.py              # Mock 响应构造与上下文管理器
│   ├── yaml_util.py              # YAML 加载 + DataHelper
│   ├── test_helpers.py           # TokenManager（Mock 模式返回 mock token）
│   ├── security.py               # 敏感数据脱敏
│   └── plugins/                  # 插件系统
│       ├── __init__.py           # 全局单例工厂
│       ├── base.py               # Plugin 基类
│       ├── manager.py            # PluginManager
│       └── normal/
│           ├── logging_plugin.py  # 请求/测试日志
│           └── allure_plugin.py   # Allure JSON 附件
│
├── config/config.py              # 多环境配置（dev/test/staging/prod）
├── data/api_test_data.yaml       # API 测试数据
│
├── test_cases/api/               # API 测试用例
│   ├── test_auth_api.py
│   ├── test_merchant_product_api.py
│   ├── test_order_flow_api.py
│   └── test_user_coupon_favorite_api.py
│
├── conftest.py                   # 全局 fixtures、CLI 参数、生命周期
├── pytest.ini                    # 标记注册、日志格式、测试发现
└── pyproject.toml                # 包元数据、依赖声明
```

---

## 2. 分层架构详解

### 2.1 API 对象层（`api/`）

#### 2.1.1 BaseApi 基类

`api/base_api.py` 是所有 API 类的父类，封装了四个 HTTP 方法：

```python
class BaseApi:
    def __init__(self, base_url=None, timeout=30, enable_plugins=True, requests=None):
        self.base_url = base_url or config.API_BASE_URL
        if requests:
            self.requests = requests  # 复用已有的 BaseRequests（session 共享）
        else:
            self.requests = BaseRequests(...)

    @allure.step("GET 请求: {url}")
    def get(self, url, **kwargs) -> Dict[str, Any]: ...

    @allure.step("POST 请求: {url}")
    def post(self, url, json_data=None, **kwargs) -> Dict[str, Any]: ...

    @allure.step("PUT 请求: {url}")
    def put(self, url, json_data=None, **kwargs) -> Dict[str, Any]: ...

    @allure.step("DELETE 请求: {url}")
    def delete(self, url, **kwargs) -> Dict[str, Any]: ...
```

**关键设计**：

- `requests` 参数允许注入已有的 `BaseRequests` 实例，通过 `conftest.py` 中的 session-scoped `http_session` fixture 实现 HTTP 连接池共享。
- `@allure.step` 自动生成 Allure 步骤节点。
- 方法不直接断言，只返回 `requests.Response` 对象，断言由测试层负责。

#### 2.1.2 业务 API 类（takeout_api.py）

`api/takeout_api.py` 采用 **API Object 模式**，每个业务模块一个类：

| 类名 | 业务模块 | Token 依赖 |
|------|----------|------------|
| `AuthApi` | 登录、登出、Token 刷新 | 不需要 |
| `UserApi` | 用户资料、地址 CRUD | 需要 |
| `MerchantApi` | 商家搜索、详情、营业状态 | 需要 |
| `ProductApi` | 菜品列表、分类、上下架 | 需要 |
| `CartApi` | 购物车增删改查 | 需要 |
| `OrderApi` | 下单、列表、详情、取消；商家接单/拒单/配送 | 需要 |
| `PayApi` | 创建支付、查询状态、模拟回调 | 需要 |
| `ReviewApi` | 提交评价、查看评价 | 需要 |
| `CouponApi` | 优惠券领取、列表 | 需要 |
| `FavoriteApi` | 收藏/取消收藏商家 | 需要 |
| `HealthApi` | 健康检查（MySQL + Redis） | 不需要 |

所有 API 类构造时支持 `requests=None` 参数，用于注入 session-scoped 的 `BaseRequests` 实例。

---

### 2.2 HTTP 传输层（`common/base_requests.py`）

#### 2.2.1 职责

- 封装 `requests.Session`，提供统一的重试策略（`HTTPAdapter` + `Retry`）
- 通过插件钩子链集成日志和 Allure 附件
- 管理 HTTP 连接池和 Session 级 header

#### 2.2.2 重试策略

| 参数 | 值 | 说明 |
|------|-----|------|
| `total` | 3 | 最大重试次数 |
| `backoff_factor` | 1.0 | 退避基数：第 1 次 1s，第 2 次 2s，第 3 次 4s |
| `status_forcelist` | [429, 500, 502, 503, 504] | 触发重试的状态码 |
| `raise_on_status` | False | 不自动抛异常 |

---

## 3. 请求-响应生命周期

一次完整请求（以 `POST` 为例）的调用链：

```
测试: auth.login(phone, code)
  |
  ▼
BaseApi.post("/api/auth/login", json_data=...)
  |  @allure.step("POST 请求: /api/auth/login")
  |  self._log_request("POST", url, json=json_data)
  |
  ▼
BaseRequests.post(endpoint, json=json_data)
  |  拼接完整 URL: base_url + endpoint
  |  构造 request_func 闭包
  |
  ▼
_execute_with_plugins(method, url, request_func, **kwargs)
  |
  ├─ [阶段1] before_request 钩子
  |   └── LoggingPlugin        ← 记录 "[请求前] POST /api/..."
  |
  ├─ [阶段2] request_func()
  |   └── session.post(url, timeout=30)
  |       └── HTTPAdapter 自动重试（最多 3 次，针对 429/5xx）
  |
  ├─ [阶段3] after_request 钩子（成功时）
  |   ├── AllurePlugin         ← 请求/响应 JSON 附加到 Allure 报告
  |   └── LoggingPlugin        ← 记录 "[请求后] 200"
  |
  └─ [阶段4] on_request_error 钩子（异常时）
      └── LoggingPlugin        ← 记录异常详情
  |
  ▼
BaseApi._log_response(response)  ← 记录状态码与响应体（最多 500 字符）
  |
  ▼
测试: is_success(response) → assert 业务状态
```

---

## 4. 测试用例结构

### 4.1 通用模式

所有 API 测试文件遵循相同结构：

```python
import pytest
import allure
from api.takeout_api import AuthApi, is_success
from common.mock_util import is_mock_mode
from config.config import config


class TestSomething:
    @pytest.fixture(autouse=True)
    def setup(self, http_session):
        """所有测试方法共享 API 对象和 session"""
        self.auth = AuthApi(requests=http_session)

    def test_success(self, mock_helper):
        """Mock 模式：显式 mock_request 拦截请求
           真实模式：直接调用后端"""
        resp = mock_helper.create_mock_response(200, {"code": 200, "success": True})
        with mock_helper.mock_request(self.auth, "post", resp):
            result = self.auth.login(config.TEST_CUSTOMER_PHONE, config.TEST_SMS_CODE)

        assert is_success(result)
```

**模式要点**：

- `http_session` fixture（session-scoped）注入给 API 对象，共享连接池
- `mock_helper` fixture 提供 Mock 能力，只在使用时生效（不再有全局 auto_mock）
- `mock.mock_request()` 在 `requests.Session` 层 patch，保留完整的插件调用链
- `@pytest.fixture(autouse=True)` 在类级别统一 setup，减少重复

### 4.2 数据驱动

通过 `@pytest.mark.parametrize` 结合 YAML 测试数据：

```python
@allure.title("登录失败 - {case}")
@pytest.mark.parametrize("phone,code,resp_data,case", [
    ("13800000003", "000000", {"code": 400, "success": False, "msg": "验证码错误"}, "错误验证码"),
    ("", "123456", {"code": 400, "success": False, "msg": "手机号不能为空"}, "空手机号"),
], ids=["wrong_code", "empty_phone"])
def test_login_failed(self, mock_helper, phone, code, resp_data, case):
    resp = mock_helper.create_mock_response(400, resp_data)
    with mock_helper.mock_request(self.auth, "post", resp):
        result = self.auth.login(phone, code)
    assert not is_success(result)
```

### 4.3 订单流程的集成测试

`_create_test_order()` 等前置条件辅助函数在 Mock 模式下直接返回模拟订单号，不依赖真实后端：

```python
def _create_test_order(http_session, customer_token=None, ...):
    if config.USE_MOCK:
        return "ORD_MOCK_" + str(hash(f"{merchant_id}-{dish_id}") & 0xFFFFF)
    # 真实模式：调用真实后端链路，失败返回 None
    ...
```

---

## 5. Mock / 真实双模式设计

### 5.1 模式切换

| 方式 | 命令 |
|------|------|
| 环境变量 | `USE_MOCK=true` / `USE_MOCK=false` |
| CLI 参数 | `pytest --mock` |
| .env 文件 | `USE_MOCK=false` |

### 5.2 核心设计：显式 Mock，取消全局拦截

**v1 → v2 的关键变更**：

- 移除全局 `auto_mock` fixture（不再自动 patch 所有 `requests.Session.request`）
- Mock 必须通过 `mock_helper` fixture 显式启用
- `common/test_helpers.py` 中的 `login_and_get_token()` 在 Mock 模式下直接返回 mock token，不发起真实 HTTP 请求

这样做的好处：

| 维度 | 全局 auto_mock（v1） | 显式 mock（v2） |
|------|----------------------|-----------------|
| 透明性 | 所有请求被静默拦截 | 每个 mock 操作在代码中可见 |
| 可预测性 | 忘记 mock 的测试也"通过"（返回固定响应） | 忘记 mock 的测试会报连接错误 |
| 测试价值 | 可能掩盖真实问题 | 真实行为可见 |

### 5.3 MockHelper 核心接口

```python
class MockHelper:
    def __init__(self):
        self.use_mock = config.USE_MOCK

    def create_mock_response(self, status_code=200, json_data=None, text="", headers=None):
        """构造模拟响应对象"""

    @contextmanager
    def mock_request(self, client, method, mock_response):
        """在 session 层 patch，保留完整插件链"""
```

### 5.4 关键设计：在 session 层 patch

```
patch session.get   → BaseApi.get 正常执行 → @allure.step 触发
                       → _execute_with_plugins 正常执行 → 插件全部触发
                       → 只有最底层的 session.get 被替换为 mock 响应
```

---

## 6. 插件系统

### 6.1 当前注册的插件

| 插件 | 功能 | 状态 |
|------|------|------|
| `LoggingPlugin` | 记录请求/测试日志 | 默认启用 |
| `AllurePlugin` | 自动附加 HTTP 请求/响应到 Allure 报告 | 默认启用 |

可通过 `--disable-plugins` 命令行参数禁用。

### 6.2 插件钩子

| 钩子 | 触发时机 | 短路语义 |
|------|----------|----------|
| `before_request` | 请求发送前 | 返回非 None 则跳过后续插件和真实请求 |
| `after_request` | 请求成功后 | 无 |
| `on_request_error` | 请求异常时 | 无 |
| `before_test` | 测试用例开始前 | 无 |
| `after_test` | 测试用例结束后 | 无 |
| `on_test_failure` | 测试断言失败时 | 无 |
| `on_test_success` | 测试通过时 | 无 |

### 6.3 已移除的组件（v1 → v2）

| 组件 | 原因 |
|------|------|
| `CircuitBreakerPlugin` | 测试框架不需要自我保护，失败应直接暴露 |
| `RateLimiterPlugin` | 测试框架不需要限制自己的请求速率 |
| `CachePlugin` | 未注册的半成品代码 |
| `MetricsPlugin` | 测试统计等价于 pytest 终端输出 |
| `common/circuit_breaker.py` | 对应的独立算法模块 |
| `common/rate_limiter.py` | 对应的独立算法模块 |

---

## 7. 配置系统

### 7.1 配置层次

```
环境变量（最高优先级）
    ↓
.env 文件（本地兜底）
    ↓
代码默认值（最低优先级）
```

### 7.2 关键配置项

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| `USE_MOCK` | `USE_MOCK` | `true` | 是否启用 Mock 模式 |
| `ENABLE_PLUGINS` | `ENABLE_PLUGINS` | `true` | 插件系统总开关 |
| `API_BASE_URL` | `TAKEOUT_API_URL` | `http://localhost:8080` | 后端地址 |
| `API_TIMEOUT` | `API_TIMEOUT` | `30` | 请求超时（秒） |

---

## 8. 公共 Fixture

定义在 `conftest.py` 中：

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `http_session` | `session` | 共享的 `BaseRequests` 实例，维护连接池 |
| `mock_helper` | `function` | `MockHelper` 实例，用于显式 Mock |
| `test_data` | `function` | YAML API 测试数据加载器 |
| `web_data` | `function` | YAML Web 测试数据加载器 |
| `session_start_end` | `session`（autouse） | 会话生命周期日志 |
| `test_start_end` | `function`（autouse） | 测试生命周期日志 + 插件钩子 |

### http_session 使用示例

```python
@pytest.fixture(autouse=True)
def setup(self, http_session):
    """API 对象共享 session，减少连接建立开销"""
    self.auth = AuthApi(requests=http_session)
    self.user = UserApi(token, requests=http_session)
```

---

## 9. 架构评估与改进记录

### 9.1 当前架构优势

| 维度 | 评价 |
|------|------|
| **分层设计** | API Object 模式是行业最佳实践，三层分离职责清晰 |
| **双模式策略** | Mock 显式可控，真实模式可验证集成正确性 |
| **插件钩子机制** | 横切关注点与业务代码解耦 |
| **Session 复用** | `http_session` fixture 共享连接池，减少创建开销 |
| **数据驱动** | `@pytest.mark.parametrize` + YAML 实现数据与逻辑分离 |
| **Mock 注入位置** | 在 session 层 patch 确保插件行为一致 |

### 9.2 v2 改进记录（2026-07-11）

| 改进项 | 变更内容 |
|--------|----------|
| 移除熔断器/限流器 | 删除 2 个核心插件 + 2 个独立算法模块（~800 行代码） |
| 统一 Mock 系统 | 移除全局 `auto_mock`，改为显式 `mock_helper` fixture |
| 移除未注册插件 | 删除 CachePlugin（半成品）和 MetricsPlugin（冗余统计） |
| 数据驱动改造 | 测试类使用 `@pytest.mark.parametrize` + 有意义的 test_id |
| Session 级 fixture | 新增 `http_session`（session-scoped），支持连接池复用 |
| 订单测试优化 | Mock 模式 setup 函数直接返回 mock 数据，真实模式 `pytest.skip` 优雅跳过 |
| 简化插件系统 | 移除 `CorePlugin` 基类、`PluginType.CORE` 枚举及相关逻辑 |
| BaseApi 增强 | 支持 `requests` 参数注入，兼容 session 复用 |

### 9.3 未来改进方向

| 方向 | 说明 |
|------|------|
| Token 自动刷新 | 在 BaseRequests 中监听 401 响应自动换 token |
| xdist 兼容 | 插件系统全局状态需要隔离，多 worker 下自动禁用 |
| 异步支持 | 如需测试 WebSocket/SSE，引入 `pytest-asyncio` |
