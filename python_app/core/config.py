# -*- coding: utf-8 -*-
"""
配置管理模块 - 集中管理应用配置
"""
import os
import sys
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from threading import RLock


@dataclass
class DatabaseConfig:
    db_name: str = "medicine_system.db"
    backup_dir: str = "backups"
    max_backups: int = 10
    backup_interval_hours: int = 24
    connection_timeout: int = 30
    enable_wal_mode: bool = True


@dataclass
class CacheConfig:
    max_query_cache_size: int = 100
    query_cache_ttl_seconds: float = 60.0
    enable_search_index: bool = True
    max_search_terms: int = 10000


@dataclass
class PerformanceConfig:
    enable_monitoring: bool = True
    slow_query_threshold_ms: int = 100
    max_metrics_history: int = 1000
    search_debounce_ms: int = 200


@dataclass
class UIConfig:
    default_window_width: int = 1400
    default_window_height: int = 900
    min_window_width: int = 800
    min_window_height: int = 600
    table_row_height: int = 40
    sidebar_width_base: int = 200


@dataclass
class AppConfig:
    app_name: str = "中药材销售管理系统"
    version: str = "2.3.0"
    author: str = "TCM System"
    debug_mode: bool = False
    log_level: str = "INFO"
    log_max_size_mb: int = 10
    log_backup_count: int = 5
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    ui: UIConfig = field(default_factory=UIConfig)


class ConfigManager:
    _instance: Optional['ConfigManager'] = None
    _lock = RLock()
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._config = AppConfig()
        self._config_dir = self._get_config_dir()
        self._config_file = os.path.join(self._config_dir, "config.json")
        self._load_config()
        self._initialized = True
    
    def _get_config_dir(self) -> str:
        if getattr(sys, 'frozen', False):
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(app_data, 'MedicineSystem')
        else:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        return config_dir
    
    def _load_config(self) -> None:
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                self._apply_config(saved_config)
            except Exception:
                pass
    
    def _apply_config(self, config_dict: Dict[str, Any]) -> None:
        if 'debug_mode' in config_dict:
            self._config.debug_mode = config_dict['debug_mode']
        if 'log_level' in config_dict:
            self._config.log_level = config_dict['log_level']
        
        if 'database' in config_dict:
            db_config = config_dict['database']
            for key, value in db_config.items():
                if hasattr(self._config.database, key):
                    setattr(self._config.database, key, value)
        
        if 'cache' in config_dict:
            cache_config = config_dict['cache']
            for key, value in cache_config.items():
                if hasattr(self._config.cache, key):
                    setattr(self._config.cache, key, value)
        
        if 'performance' in config_dict:
            perf_config = config_dict['performance']
            for key, value in perf_config.items():
                if hasattr(self._config.performance, key):
                    setattr(self._config.performance, key, value)
    
    def save_config(self) -> None:
        try:
            config_dict = {
                'debug_mode': self._config.debug_mode,
                'log_level': self._config.log_level,
                'database': {
                    'max_backups': self._config.database.max_backups,
                    'backup_interval_hours': self._config.database.backup_interval_hours,
                },
                'cache': {
                    'max_query_cache_size': self._config.cache.max_query_cache_size,
                    'query_cache_ttl_seconds': self._config.cache.query_cache_ttl_seconds,
                },
                'performance': {
                    'enable_monitoring': self._config.performance.enable_monitoring,
                    'slow_query_threshold_ms': self._config.performance.slow_query_threshold_ms,
                }
            }
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    @property
    def config(self) -> AppConfig:
        return self._config
    
    @property
    def database(self) -> DatabaseConfig:
        return self._config.database
    
    @property
    def cache(self) -> CacheConfig:
        return self._config.cache
    
    @property
    def performance(self) -> PerformanceConfig:
        return self._config.performance
    
    @property
    def ui(self) -> UIConfig:
        return self._config.ui
    
    def get_app_data_dir(self) -> str:
        return self._config_dir
    
    def get_db_path(self) -> str:
        return os.path.join(self._config_dir, self._config.database.db_name)
    
    def get_backup_dir(self) -> str:
        backup_dir = os.path.join(self._config_dir, self._config.database.backup_dir)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return backup_dir
    
    def get_log_dir(self) -> str:
        log_dir = os.path.join(self._config_dir, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir
    
    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None


def get_config() -> ConfigManager:
    return ConfigManager()
