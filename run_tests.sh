#!/bin/bash
# TakeoutSystem 测试框架运行脚本
# 用法: ./run_tests.sh [api|ui|all] [mock|real]

set -e

MODE="${2:-real}"
SCOPE="${1:-all}"

if [ "$MODE" = "mock" ]; then
  ENV_SETTING="USE_MOCK=true"
elif [ "$MODE" = "real" ]; then
  ENV_SETTING="USE_MOCK=false HEADLESS=false ENV=dev"
fi

echo "============================================"
echo "   TakeoutSystem 测试运行"
echo "   范围: $SCOPE"
echo "   模式: $MODE"
echo "============================================"
echo ""

run_api() {
  echo ">>> 运行 API 测试..."
  eval "$ENV_SETTING python -m pytest test_cases/api/ -v --tb=short"
}

run_ui() {
  echo ">>> 运行 UI 测试..."
  eval "$ENV_SETTING python -m pytest test_cases/web/ -v --tb=short"
}

case "$SCOPE" in
  api)  run_api ;;
  ui)   run_ui ;;
  all)  run_api && echo "" && run_ui ;;
  *)
    echo "用法: $0 [api|ui|all] [mock|real]"
    exit 1
    ;;
esac

echo ""
echo "============================================"
echo "   测试完成"
echo "============================================"
