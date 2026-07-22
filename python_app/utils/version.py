import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

CURRENT_VERSION = "4.2.0"
VERSION_DATE = "2026-07-22"
APP_NAME = "中药材销售管理系统"
AUTHOR = "TCM System"

GITEE_REPO = "flyxjin/doctor"
GITEE_API_URL = f"https://gitee.com/api/v5/repos/{GITEE_REPO}"
GITEE_RELEASES_URL = f"{GITEE_API_URL}/releases/latest"

CHANGELOG = {
    "4.2.0": {
        "date": "2026-07-22",
        "changes": [
            "UI 风格升级：新极简主义 + 东方雅致设计系统",
            "配色调整：宣纸米白底 + 本草青主色 + 墨黑文字 + 朱砂红警示，呼应中医药文化属性",
            "语义色优化：古铜黄替代刺眼橙黄，朱砂红替代亮红，长时间使用更舒适",
            "触觉质感增强：表格行悬停高亮，侧栏导航选中态改用本草青主色",
            "阴影系统柔和化：漫射阴影替代硬边框，营造层次纵深",
            "Dashboard 库存预警颜色统一到主题色板（朱砂红/古铜黄）",
            "修复窗口缩放显示异常：font_manager 单例化，所有组件共享同一信号源",
            "修复最小窗口下显示不完整：主窗口最小尺寸提升至 1024x720，各视图设置最小宽度 760px，侧边栏在小窗口下自动收窄",
            "修复双重缓存同步：移除 View 层手动缓存操作，统一由 Service 层同步（含库存字段）",
            "修复 PrescriptionService 事务隔离：库存扣减/回退改为在主事务内通过 SQL 执行，避免跨 Service 事务读旧数据",
            "修复 PrescriptionView N+1 查询：一次联表查询替换循环内 get_by_medicine_id，搜索响应从秒级降为毫秒级",
            "补充 4 个缺失的数据库索引：prescription_items.prescription_id/medicine_id、operation_logs.target_type、inventory_history.created_at",
            "修复 BatchImportView worker 关闭时未取消：新增 closeEvent 取消 worker，信号回调加 RuntimeError 保护",
            "修复更新前备份失败静默吞没：备份失败时弹窗询问用户是否继续",
            "修复 worker 通过私有方法关闭连接：改用公开的 close() 方法",
            "批量导入新增 MedicineValidator 校验和数值字段显式转换",
            "保存处方新增 PrescriptionValidator 校验",
            "修复 table.item().text() 链式调用无 None 检查：新增 _get_cell_text 安全方法",
            "配置加载/保存异常改为记录日志而非静默吞没",
            "缓存 update/delete 优化为 O(1) 定向索引更新，替代全量重建",
            "修复药性筛选器列表不一致：补充微寒/微温/大寒选项",
            "修复 insert_prescription 未写入 created_at 字段导致日期过滤失效",
            "修复库存管理与药材管理种类不一致：update_with_inventory 改为 UPSERT 补建缺失 inventory 记录，启动时自动修复历史数据",
            "库存管理统计口径统一：药材种类基于 medicines 表 COUNT（与药材管理/仪表盘/统计页一致）",
            "测试覆盖从 61 个增至 207 个：新增 PrescriptionService、Repository 写方法、DataLoader 测试"
        ]
    },
    "4.1.0": {
        "date": "2026-07-05",
        "changes": [
            "UI 风格升级：新极简主义 + 东方雅致设计系统",
            "配色调整：宣纸米白底 + 本草青主色 + 墨黑文字 + 朱砂红警示，呼应中医药文化属性",
            "语义色优化：古铜黄替代刺眼橙黄，朱砂红替代亮红，长时间使用更舒适",
            "触觉质感增强：表格行悬停高亮，侧栏导航选中态改用本草青主色",
            "阴影系统柔和化：漫射阴影替代硬边框，营造层次纵深",
            "Dashboard 库存预警颜色统一到主题色板（朱砂红/古铜黄）",
            "修复窗口缩放显示异常：font_manager 单例化，所有组件共享同一信号源",
            "修复最小窗口下显示不完整：主窗口最小尺寸提升至 1024x720，各视图设置最小宽度 760px，侧边栏在小窗口下自动收窄",
            "修复双重缓存同步：移除 View 层手动缓存操作，统一由 Service 层同步（含库存字段）",
            "修复 PrescriptionService 事务隔离：库存扣减/回退改为在主事务内通过 SQL 执行，避免跨 Service 事务读旧数据",
            "修复 PrescriptionView N+1 查询：一次联表查询替换循环内 get_by_medicine_id，搜索响应从秒级降为毫秒级",
            "补充 4 个缺失的数据库索引：prescription_items.prescription_id/medicine_id、operation_logs.target_type、inventory_history.created_at",
            "修复 BatchImportView worker 关闭时未取消：新增 closeEvent 取消 worker，信号回调加 RuntimeError 保护",
            "修复更新前备份失败静默吞没：备份失败时弹窗询问用户是否继续",
            "修复 worker 通过私有方法关闭连接：改用公开的 close() 方法",
            "批量导入新增 MedicineValidator 校验和数值字段显式转换",
            "保存处方新增 PrescriptionValidator 校验",
            "修复 table.item().text() 链式调用无 None 检查：新增 _get_cell_text 安全方法",
            "配置加载/保存异常改为记录日志而非静默吞没",
            "缓存 update/delete 优化为 O(1) 定向索引更新，替代全量重建",
            "修复药性筛选器列表不一致：补充微寒/微温/大寒选项",
            "修复 insert_prescription 未写入 created_at 字段导致日期过滤失效",
            "修复库存管理与药材管理种类不一致：update_with_inventory 改为 UPSERT 补建缺失 inventory 记录，启动时自动修复历史数据",
            "库存管理统计口径统一：药材种类基于 medicines 表 COUNT（与药材管理/仪表盘/统计页一致）",
            "测试覆盖从 61 个增至 90 个：新增 PrescriptionService、Repository 写方法、DataLoader 测试"
        ]
    },
    "4.0.0": {
        "date": "2026-07-04",
        "changes": [
            "GUI 框架升级：PyQt5 5.15 → PySide6 6.6+（Qt 官方维护，LGPL 授权）",
            "引入 SQLAlchemy 2.0 ORM：7 张表 ORM 映射，Engine/Session 管理，工作线程独立 Session",
            "Repository 分层架构：Service 层通过 Repository 访问数据，SQL 下沉到 Repository",
            "Repository 只读方法切换到 ORM（select 语句），写方法保留原生 SQL 维持跨 Repository 事务原子性",
            "Database 持有 SQLAlchemy Engine：表结构改由 Base.metadata.create_all() 创建，手写索引保留",
            "修复 Database.close() 单例 bug：close() 后再调用 reset_instance() 误清空新实例的 Engine",
            "修复 Database.close() 非幂等问题：重复调用 close() 会关闭被新单例复用的连接",
            "新增 32 个 Repository ORM 回归测试，总测试数 61 个全部通过",
            "清理 Win7 兼容代码：PySide6 不支持 Windows 7，移除 Win7 spec/guide/requirements"
        ]
    },
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
        from core.database import get_app_data_dir
        return get_app_data_dir()

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
            except (json.JSONDecodeError, OSError) as e:
                logging.getLogger('MedicineSystem').warning(f"加载更新配置失败: {e}")
            except Exception as e:
                # 配置结构异常（如字段类型错误）时回退到默认配置，避免崩溃
                logging.getLogger('MedicineSystem').warning(f"更新配置解析异常，使用默认配置: {e}")

        return default_config

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logging.getLogger('MedicineSystem').warning(f"保存更新配置失败: {e}")

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
        except (ValueError, TypeError):
            # last_check_time 格式异常或字段类型错误时，触发检查
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
