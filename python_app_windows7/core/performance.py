# -*- coding: utf-8 -*-
"""
性能监控模块 - 测量和分析系统性能
"""
import time
import statistics
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from dataclasses import dataclass, field
from collections import defaultdict
import threading


@dataclass
class PerformanceMetrics:
    name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    times: List[float] = field(default_factory=list)
    
    def record(self, duration: float) -> None:
        self.call_count += 1
        self.total_time += duration
        if duration < self.min_time:
            self.min_time = duration
        if duration > self.max_time:
            self.max_time = duration
        self.times.append(duration)
        if len(self.times) > 1000:
            self.times = self.times[-1000:]
    
    def get_average(self) -> float:
        if self.call_count == 0:
            return 0.0
        return self.total_time / self.call_count
    
    def get_median(self) -> float:
        if not self.times:
            return 0.0
        return statistics.median(self.times)
    
    def get_percentile(self, percentile: float = 95) -> float:
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(idx, len(sorted_times) - 1)]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'call_count': self.call_count,
            'total_time': round(self.total_time, 4),
            'avg_time': round(self.get_average(), 4),
            'min_time': round(self.min_time, 4) if self.min_time != float('inf') else 0,
            'max_time': round(self.max_time, 4),
            'median_time': round(self.get_median(), 4),
            'p95_time': round(self.get_percentile(95), 4),
            'p99_time': round(self.get_percentile(99), 4)
        }


class PerformanceMonitor:
    _instance: Optional['PerformanceMonitor'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'PerformanceMonitor':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._metrics: Dict[str, PerformanceMetrics] = {}
        self._lock = threading.RLock()
        self._initialized = True
    
    def record(self, name: str, duration: float) -> None:
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = PerformanceMetrics(name=name)
            self._metrics[name].record(duration)
    
    def get_metrics(self, name: str) -> Optional[PerformanceMetrics]:
        with self._lock:
            return self._metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        with self._lock:
            return dict(self._metrics)
    
    def reset(self, name: Optional[str] = None) -> None:
        with self._lock:
            if name:
                if name in self._metrics:
                    del self._metrics[name]
            else:
                self._metrics.clear()
    
    def get_report(self) -> Dict[str, Any]:
        with self._lock:
            report = {
                'total_functions': len(self._metrics),
                'total_calls': sum(m.call_count for m in self._metrics.values()),
                'total_time': sum(m.total_time for m in self._metrics.values()),
                'functions': [m.to_dict() for m in self._metrics.values()]
            }
            report['functions'].sort(key=lambda x: x['total_time'], reverse=True)
            return report
    
    def print_report(self) -> None:
        report = self.get_report()
        print("\n" + "=" * 80)
        print("性能报告")
        print("=" * 80)
        print(f"总函数数: {report['total_functions']}")
        print(f"总调用次数: {report['total_calls']}")
        print(f"总耗时: {report['total_time']:.4f}秒")
        print("\n按总耗时排序的函数:")
        print("-" * 80)
        for func in report['functions'][:10]:
            print(f"{func['name']:<40} 调用:{func['call_count']:>6}  平均:{func['avg_time']:>8.4f}s  总计:{func['total_time']:>8.4f}s")
        print("=" * 80 + "\n")


def measure(func: Optional[Callable] = None, name: Optional[str] = None):
    def decorator(f: Callable) -> Callable:
        metric_name = name or f"{f.__module__}.{f.__name__}"
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return f(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start
                monitor = PerformanceMonitor()
                monitor.record(metric_name, duration)
        
        return wrapper
    
    if func is not None:
        if callable(func):
            return decorator(func)
        else:
            name = func
            return decorator
    return decorator


def measure_async(func: Optional[Callable] = None, name: Optional[str] = None):
    def decorator(f: Callable) -> Callable:
        metric_name = name or f"{f.__module__}.{f.__name__}"
        
        @wraps(f)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await f(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start
                monitor = PerformanceMonitor()
                monitor.record(metric_name, duration)
        
        return wrapper
    
    if func is not None:
        if callable(func):
            return decorator(func)
        else:
            name = func
            return decorator
    return decorator


class Timer:
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.monitor = PerformanceMonitor()
    
    def __enter__(self) -> 'Timer':
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            self.monitor.record(self.name, duration)
    
    def start(self) -> None:
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        if self.start_time is None:
            return 0.0
        duration = time.perf_counter() - self.start_time
        self.monitor.record(self.name, duration)
        self.start_time = None
        return duration


_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def performance_report() -> Dict[str, Any]:
    return get_performance_monitor().get_report()


def print_performance_report() -> None:
    get_performance_monitor().print_report()
