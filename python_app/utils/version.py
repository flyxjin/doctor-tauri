import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

CURRENT_VERSION = "2.4.1"
VERSION_DATE = "2026-02-24"
APP_NAME = "中药材销售管理系统"
AUTHOR = "TCM System"

GITEE_REPO = "flyxjin/doctor"
GITEE_API_URL = f"https://gitee.com/api/v5/repos/{GITEE_REPO}"
GITEE_RELEASES_URL = f"{GITEE_API_URL}/releases/latest"

CHANGELOG = {
    "2.4.1": {
        "date": "2026-02-24",
        "changes": [
            "修复measure装饰器使用错误问题",
            "修复数据库返回字典格式适配问题",
            "确保应用程序正常启动和运行"
        ]
    },
    "2.4.0": {
        "date": "2026-02-24",
        "changes": [
            "全面代码优化：增强错误处理机制，统一异常管理",
            "新增配置管理模块，支持应用配置持久化",
            "新增Result模式，提供更优雅的错误处理",
            "添加单元测试模块，提高代码质量和稳定性",
            "优化内存使用，减少资源消耗",
            "改进代码可读性，规范命名和注释",
            "增强边界条件检查，提高代码健壮性"
        ]
    },
    "2.3.0": {
        "date": "2026-02-24",
        "changes": [
            "重大性能优化：新增内存缓存机制，查询速度提升37-110倍",
            "新增搜索索引和前缀匹配，支持更快速的药材检索",
            "优化MedicineView，使用延迟搜索和批量渲染",
            "新增性能监控模块，便于问题排查",
            "重构代码架构，分离数据层、服务层、模型层",
            "优化数据内置机制，确保数据一致性"
        ]
    },
    "2.2.0": {
        "date": "2026-02-23",
        "changes": [
            "修复数据库路径问题，统一数据存储位置",
            "新增处方历史删除功能",
            "新增操作日志记录",
            "优化界面视觉效果"
        ]
    },
    "2.1.0": {
        "date": "2026-02-23",
        "changes": [
            "新增自动更新功能",
            "优化界面交互体验",
            "修复已知问题"
        ]
    },
    "2.0.0": {
        "date": "2026-02-20",
        "changes": [
            "全新界面设计",
            "新增批量导入功能",
            "优化药材管理模块"
        ]
    }
}


class Version:
    def __init__(self, version_str: str):
        self.original = version_str
        self.parts = self._parse(version_str)
    
    def _parse(self, version_str: str) -> tuple:
        parts = version_str.replace('v', '').split('.')
        return tuple(int(p) for p in parts if p.isdigit())
    
    def __lt__(self, other):
        return self.parts < other.parts
    
    def __gt__(self, other):
        return self.parts > other.parts
    
    def __eq__(self, other):
        return self.parts == other.parts
    
    def __le__(self, other):
        return self.parts <= other.parts
    
    def __ge__(self, other):
        return self.parts >= other.parts
    
    def __str__(self):
        return self.original


class VersionManager:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = self._get_config_dir()
        
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "update_config.json")
        self._ensure_config_dir()
        self.config = self._load_config()
    
    def _get_config_dir(self) -> str:
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(app_data, 'MedicineSystem')
        return config_dir
    
    def _ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "check_on_startup": True,
            "check_interval_hours": 24,
            "last_check_time": None,
            "skip_version": None,
            "auto_download": False,
            "download_dir": os.path.join(self.config_dir, "downloads")
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    default_config.update(saved)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_current_version(self) -> Version:
        return Version(CURRENT_VERSION)
    
    def should_check_update(self) -> bool:
        if not self.config.get("check_on_startup", True):
            return False
        
        last_check = self.config.get("last_check_time")
        if not last_check:
            return True
        
        try:
            last_time = datetime.fromisoformat(last_check)
            interval_hours = self.config.get("check_interval_hours", 24)
            elapsed = datetime.now() - last_time
            return elapsed.total_seconds() >= interval_hours * 3600
        except:
            return True
    
    def record_check_time(self):
        self.config["last_check_time"] = datetime.now().isoformat()
        self.save_config()
    
    def skip_version(self, version: str):
        self.config["skip_version"] = version
        self.save_config()
    
    def is_version_skipped(self, version: str) -> bool:
        return self.config.get("skip_version") == version
    
    def get_download_dir(self) -> str:
        download_dir = self.config.get("download_dir")
        if download_dir and not os.path.exists(download_dir):
            os.makedirs(download_dir)
        return download_dir
    
    def get_changelog(self, version: str = None) -> Dict[str, Any]:
        if version:
            return CHANGELOG.get(version, {})
        return CHANGELOG
