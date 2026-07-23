# pytest-api-framework — TakeoutSystem 自动化测试框架

## 项目简介

自动化测试框架，用于测试 **TakeoutSystem**（外卖点餐系统）项目的 API 和 UI。

## CI/CD

通过 **GitHub Actions**（`.github/workflows/test.yml`）驱动：

- **Push/PR** → main/develop：Lint + API Mock 测试
- **定时**（每日 UTC 22:00）：全量真实模式测试（API + UI）
- **手动触发**：灵活选择 scope（api/ui/full）和 mock_mode

Docker 镜像从 **Docker Hub** 拉取：
- `cwtchtome/takeout-backend:latest`
- `cwtchtome/takeout-h5:latest`
- `cwtchtome/takeout-merchant:latest`
- `cwtchtome/takeout-admin:latest`

## 快速运行

```bash
# Mock 模式（无需后端）
USE_MOCK=true python -m pytest test_cases/api/ -v

# 真实模式（需 Docker 后端）
USE_MOCK=false python -m pytest test_cases/api/ -v

# 健康检查
curl http://localhost:8080/api/health
```

详细说明见 `.claude/skills/takeout-ci.md`
