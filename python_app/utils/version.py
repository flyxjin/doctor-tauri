import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

CURRENT_VERSION = "3.3.2"
VERSION_DATE = "2026-06-21"
APP_NAME = "中药材销售管理系统"
AUTHOR = "TCM System"

GITEE_REPO = "flyxjin/doctor"
GITEE_API_URL = f"https://gitee.com/api/v5/repos/{GITEE_REPO}"
GITEE_RELEASES_URL = f"{GITEE_API_URL}/releases/latest"

CHANGELOG = {
    "3.3.2": {
        "date": "2026-06-21",
        "changes": [
            "修复旧数据库缺少 updated_at/created_at 列导致入库/出库/调整失败（sqlite3.OperationalError: no such column）",
            "新增数据库 schema 自动迁移：启动时检测并补全所有表缺失的列，兼容旧版本数据库升级"
        ]
    },
    "3.3.1": {
        "date": "2026-06-21",
        "changes": [
            "修复 history_view 操作日志对话框 NameError（get_font_manager / get_table_style 未导入）",
            "修复 history_view show_detail 选中非ID列时 ValueError 崩溃",
            "修复 base_view ResponsiveWidget 未初始化导致响应式自动刷新失效",
            "修复 main.py 批量导入后缓存未重建导致新药材不显示",
            "修复 Inventory 模型缺少 category 字段导致库存分类列空白",
            "修复 statistics_view / dashboard_view SUM 为 NULL 时 TypeError",
            "修复 inventory_view 入库/出库/调整空值时 ValueError 崩溃",
            "清理 prescription_view 语义错误的 contraindication 字段检查"
        ]
    },
    "3.3.0": {
        "date": "2026-06-21",
        "changes": [
            "新增首页概览仪表盘：今日营收/处方/药材数/低库存预警卡片、近7天营收趋势条形图、最近处方列表",
            "新增销售统计报表：时间范围筛选、热销药材TOP10、营收趋势分析",
            "新增配伍禁忌预警：基于十八反十九畏规则，添加药材时实时提醒，保存处方前最终确认",
            "修复ImportThread线程安全问题：改用独立worker连接，避免与主线程共享cursor",
            "Service层统一缓存同步：create/update/delete自动失效缓存，修复invalidate_medicine_cache调用不存在clear方法的bug",
            "日志改用RotatingFileHandler：单文件10MB，保留5个备份，防止日志无限增长",
            "引入pytest测试框架：新增26个单元测试（Service层、缓存同步、配伍禁忌），配置GitHub Actions CI"
        ]
    },
    "3.2.3": {
        "date": "2026-06-12",
        "changes": [
            "修复medicine_view/inventory_view/prescription_view缺少get_secondary_button_style导入"
        ]
    },
    "3.2.2": {
        "date": "2026-06-12",
        "changes": [
            "修复代码质量：将bare except替换为具体异常类型",
            "清理utils/updater.py、utils/version.py、widgets/update_dialog.py中的异常处理"
        ]
    },
    "3.2.1": {
        "date": "2026-06-12",
        "changes": [
            "修复UI重构后旧颜色常量引用缺失导致的运行时错误",
            "统一TEXT_REGULAR→TEXT_SECONDARY、TEXT_CAPTION→TEXT_MUTED等引用"
        ]
    },
    "3.2.0": {
        "date": "2026-06-12",
        "changes": [
            "UI全面重构为现代极简风格",
            "新配色方案：中性色调+靛蓝点缀",
            "简化侧边栏：白色背景+细边框",
            "优化表格：大留白、细边框、清晰层次",
            "重新设计按钮样式：主按钮+次级按钮分离",
            "优化药材详情弹窗：卡片式信息展示",
            "统一页边距和间距规范",
            "改进表头样式：大写字母+字母间距"
        ]
    },
    "3.1.1": {
        "date": "2026-06-12",
        "changes": [
            "修复删除药材时外键约束报错（prescription_items、inventory_history缺少级联删除）",
            "修复批量导入线程中fetchone()返回dict却用下标访问的TypeError",
            "修复库存视图出入库/调整时med_id字符串转int类型错误",
            "修复处方历史查看详情时pres_id字符串转int类型错误"
        ]
    },
    "3.1.0": {
        "date": "2026-06-12",
        "changes": [
            "View层统一继承BaseDataView，消除_apply_responsive_table重复代码",
            "所有View通过Service层访问数据，不再直接写SQL",
            "MedicineDialog添加/编辑时调用MedicineValidator完整验证",
            "InventoryView库存状态过滤下推到SQL WHERE子句",
            "MedicineView缓存初始化改用MedicineService.get_all_as_dicts()",
            "PrescriptionService.get_all新增load_items参数支持",
            "InventoryService.get_all新增keyword和stock_status过滤参数"
        ]
    },
    "3.0.0": {
        "date": "2026-05-14",
        "changes": [
            "修复数据导出崩溃问题（dict切片TypeError）",
            "修复处方删除快速双击竞态问题",
            "修复数据库事务原子性（execute自动commit破坏显式事务）",
            "修复Database单例线程安全（添加threading.Lock保护）",
            "修复自动更新SSL证书验证（移除不安全的CERT_NONE）",
            "统一Service层验证器调用（使用MedicineValidator替代宽松验证）",
            "声明openpyxl依赖"
        ]
    },
    "2.6.0": {
        "date": "2026-04-30",
        "changes": [
            "prescription_view接入响应式字体系统，支持窗口缩放自适应",
            "history_view接入响应式字体系统，支持窗口缩放自适应",
            "所有视图统一继承ResponsiveWidget，窗口缩放时表格字体自动调整"
        ]
    },
    "2.5.1": {
        "date": "2026-04-30",
        "changes": [
            "将main.py中260行内联CSS提取到theme.py集中管理",
            "新增get_main_window_style()统一生成主窗口样式",
            "main.py._apply_responsive_styles从260行缩减为3行"
        ]
    },
    "2.5.0": {
        "date": "2026-04-30",
        "changes": [
            "View层全面接入Service层，激活数据验证和操作日志",
            "medicine_view使用MedicineService进行增删改",
            "inventory_view使用InventoryService进行出入库和调整",
            "prescription_view使用PrescriptionService保存处方",
            "history_view使用PrescriptionService删除处方",
            "新增InventoryService.adjust_stock方法",
            "简化Medicine.validate()验证规则"
        ]
    },
    "2.4.3": {
        "date": "2026-04-30",
        "changes": [
            "修复InventoryService.update_stock()双重UPDATE语句问题",
            "修复version.py中bare except吞没所有异常的问题",
            "优化PerformanceMetrics使用deque替代列表切片",
            "移除MedicineDialog中废弃的tuple数据路径",
            "修复inventory_view中'全部'过滤时的冗余逻辑",
            "移除history_view中冗余的operation_logs表创建",
            "删除未使用的database_optimized.py"
        ]
    },
    "2.4.2": {
        "date": "2026-02-25",
        "changes": [
            "修复处方开具模块闪退问题",
            "修复数据库字典格式适配问题（prescription_view, history_view, batch_import_view）",
            "增强库存检查逻辑，防止超量添加",
            "添加处方药材删除功能",
            "完善异常处理和日志记录",
            "优化用户交互体验"
        ]
    },
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
            except Exception:
                pass
        
        return default_config
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception:
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
        except Exception:
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
