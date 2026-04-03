"""
普通插件 - 指标插件

功能：收集性能和测试指标
"""
import logging
import time
from typing import Dict, Any

from ..base import Plugin


logger = logging.getLogger(__name__)


class MetricsPlugin(Plugin):
    """指标插件 - 收集性能指标"""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'request_success': 0,
            'request_failed': 0,
            'test_count': 0,
            'test_passed': 0,
            'test_failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    @property
    def name(self) -> str:
        return "metrics"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "收集性能和测试指标"
    
    @property
    def author(self) -> str:
        return "System"
    
    def on_enable(self):
        self.metrics['start_time'] = time.time()
        super().on_enable()
    
    def on_disable(self):
        self.metrics['end_time'] = time.time()
        super().on_disable()
    
    def after_request(self, response, method: str, url: str, **kwargs):
        self.metrics['request_count'] += 1
        if hasattr(response, 'status_code') and response.status_code < 400:
            self.metrics['request_success'] += 1
        else:
            self.metrics['request_failed'] += 1
    
    def on_request_error(self, error: Exception, method: str, url: str, **kwargs):
        self.metrics['request_count'] += 1
        self.metrics['request_failed'] += 1
    
    def before_test(self, test_name: str):
        self.metrics['test_count'] += 1
    
    def on_test_success(self, test_name: str):
        self.metrics['test_passed'] += 1
    
    def on_test_failure(self, test_name: str, error):
        self.metrics['test_failed'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        metrics = self.metrics.copy()
        if metrics['start_time']:
            metrics['duration'] = time.time() - metrics['start_time']
        return metrics
    
    def get_summary(self) -> str:
        """获取指标摘要"""
        m = self.metrics
        duration = time.time() - m['start_time'] if m['start_time'] else 0
        return (
            f"测试统计:\n"
            f"  - 总测试数: {m['test_count']}\n"
            f"  - 通过: {m['test_passed']}\n"
            f"  - 失败: {m['test_failed']}\n"
            f"  - 请求次数: {m['request_count']}\n"
            f"  - 请求成功: {m['request_success']}\n"
            f"  - 请求失败: {m['request_failed']}\n"
            f"  - 执行时长: {duration:.2f}s"
        )
