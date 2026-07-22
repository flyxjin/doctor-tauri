# 中药材销售管理系统

基于 Python + PySide6 开发的原生 Windows 桌面应用，面向药店医生的中药材销售与处方管理工具。双击即用，无需浏览器，无需安装运行时。

## 功能模块

| 模块 | 功能 |
|------|------|
| **首页概览** | 今日营收/处方数/药材数/低库存预警卡片、近 7 天营收趋势条形图、最近处方列表 |
| **药材管理** | 药材信息录入、查询、编辑、删除、批量导入（内置 300 味中药材数据） |
| **开处方** | 患者信息录入、药材选择、自动计价、**十八反十九畏配伍禁忌预警** |
| **库存管理** | 入库、出库、库存调整、低库存预警、库存历史记录 |
| **处方历史** | 历史处方查询、详情查看、删除、操作日志 |
| **销售统计** | 时间范围筛选（今日/本周/本月/本年/全部）、热销药材 TOP10、营收趋势分析 |

## 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 8.1 / 10 / 11 |
| **处理器** | 1 GHz 或更快 |
| **内存** | 512 MB RAM |
| **硬盘** | 100 MB 可用空间 |
| **运行时** | 无需安装（exe 已打包所有依赖） |

## 安装与运行

### 方法一：直接运行打包版本（推荐）

双击 `中药材销售管理系统.exe` 即可运行，无需安装 Python 或其他依赖。

### 方法二：从源码运行

1. 安装 Python 3.9+（勾选 "Add Python to PATH"）
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行：
   ```bash
   python main.py
   ```

### 方法三：自行打包

```bash
pip install -r requirements.txt
pyinstaller --clean 中药材销售管理系统.spec
```

产物位于 `dist/中药材销售管理系统.exe`。

## 项目结构

```
python_app/
├── main.py                          # 主程序入口、主窗口、视图切换
├── medicines_data_300.py            # 内置 300 味中药材数据
├── requirements.txt                 # 运行依赖
├── requirements-dev.txt             # 开发依赖（测试、lint）
├── pytest.ini                       # pytest 配置
├── 中药材销售管理系统.spec           # PyInstaller 打包配置
├── core/                            # 核心业务层
│   ├── database.py                  # 数据库连接 + schema 自动迁移
│   ├── models.py                    # 数据模型（Medicine/Inventory/Prescription 等）
│   ├── services.py                  # 业务服务层 + 缓存同步
│   ├── cache.py                     # LRU 缓存 + MedicineCache
│   ├── validators.py                # 数据验证器
│   ├── compatibility.py             # 十八反十九畏配伍禁忌检查
│   ├── exceptions.py                # 统一异常体系
│   ├── logger.py                    # 日志（RotatingFileHandler）
│   ├── theme.py                     # UI 主题配色
│   └── performance.py               # 性能监控
├── views/                           # 视图层
│   ├── base_view.py                 # 基础视图（响应式表格、按钮工厂）
│   ├── dashboard_view.py            # 首页概览仪表盘
│   ├── medicine_view.py             # 药材管理
│   ├── prescription_view.py         # 开处方
│   ├── inventory_view.py            # 库存管理
│   ├── history_view.py              # 处方历史
│   ├── statistics_view.py           # 销售统计
│   └── batch_import_view.py         # 批量导入
├── widgets/                         # 自定义控件
│   ├── page_header.py               # 页面标题栏
│   └── update_dialog.py             # 更新对话框
├── utils/                           # 工具模块
│   ├── version.py                   # 版本管理 + 更新日志
│   ├── updater.py                   # 自动更新
│   └── responsive_font.py           # 响应式字体
└── tests/                           # 单元测试
    ├── conftest.py                  # pytest fixtures
    ├── test_services.py             # Service 层测试
    ├── test_cache_sync.py           # 缓存同步测试
    └── test_compatibility.py        # 配伍禁忌测试
```

## 数据存储

| 类型 | 路径 |
|------|------|
| 数据库 | `%APPDATA%\MedicineSystem\medicine_system.db`（SQLite） |
| 日志 | `%APPDATA%\MedicineSystem\logs\`（10MB 轮转，保留 5 份） |
| 备份 | `%APPDATA%\MedicineSystem\backups\` |

数据库在应用启动时自动创建并执行 schema 迁移，兼容旧版本数据库升级。

## 技术栈

- **GUI 框架**: PySide6 6.6+（Qt 官方维护，LGPL 授权）
- **数据库**: SQLite3（线程安全单例 + schema 自动迁移）
- **ORM**: SQLAlchemy 2.0（Repository 分层，只读走 ORM，写操作保留原生 SQL 维持跨 Repository 事务原子性）
- **打包工具**: PyInstaller 6.x
- **开发语言**: Python 3.9+
- **测试框架**: pytest + pytest-qt
- **缓存**: LRU 缓存 + 读写穿透

## 开发

### 运行测试

```bash
pip install -r requirements-dev.txt
pytest
```

当前测试覆盖：Service 层、缓存同步、配伍禁忌检查，共 52 个单元测试。

### 架构分层

```
main.py (入口/主窗口)
   │
   ├── views/ (视图层，继承 BaseDataView)
   │      └── 调用 Service 层
   │
   └── core/ (业务层)
          ├── services.py      → 业务逻辑 + 缓存同步
          ├── repositories/    → Repository 层（SQL 下沉，只读走 ORM）
          ├── orm_models.py    → SQLAlchemy 2.0 ORM 模型
          ├── db_session.py    → Engine/Session 管理
          ├── cache.py         → LRU 缓存
          ├── validators.py    → 数据验证
          ├── compatibility.py → 配伍禁忌
          └── database.py      → SQLite 单例 + schema 迁移 + Engine 持有
```

## 常见问题

### 1. 双击 exe 闪退

在命令行运行 `中药材销售管理系统.exe` 查看错误输出。常见原因：
- 旧数据库 schema 不兼容 → v3.3.2+ 已自动迁移
- 数据库文件损坏 → 备份后删除 `%APPDATA%\MedicineSystem\medicine_system.db` 重启

### 2. 入库/出库失败

升级到 v3.3.2+，启动时会自动补全旧数据库缺失的 `updated_at`/`created_at` 列。

### 3. 批量导入后药材不显示

v3.3.1+ 已修复：导入完成后自动失效缓存并重建，无需手动刷新。

### 4. 数据库文件丢失

系统会自动创建新数据库并加载内置 300 味中药材数据。

## 版本信息

- 当前版本: **4.0.0**
- 发布日期: 2026-07-04
- 开发语言: Python 3.9+
- 界面框架: PySide6 6.6+
- ORM: SQLAlchemy 2.0

## 更新日志

### v4.0.0 (2026-07-04) — 技术栈升级

- **GUI 框架升级**：PyQt5 5.15 → PySide6 6.6+（Qt 官方维护，LGPL 授权）
- **引入 SQLAlchemy 2.0 ORM**：7 张表 ORM 映射，Engine/Session 管理，工作线程独立 Session
- **Repository 分层架构**：Service 层通过 Repository 访问数据，SQL 下沉到 Repository；只读方法走 ORM（select 语句），写方法保留原生 SQL 维持跨 Repository 事务原子性
- **Database 持有 Engine**：表结构改由 `Base.metadata.create_all()` 创建
- 修复 `Database.close()` 单例 bug 与非幂等问题
- 新增 32 个 Repository ORM 回归测试，总测试数 61 个全部通过
- 清理 Win7 兼容代码（PySide6 不支持 Windows 7）

### v3.3.2 (2026-06-21)
- 修复旧数据库缺少 `updated_at`/`created_at` 列导致入库/出库失败
- 新增数据库 schema 自动迁移：启动时检测并补全所有表缺失的列，兼容旧版本数据库升级

### v3.3.1 (2026-06-21)
- 修复操作日志对话框 NameError（`get_font_manager`/`get_table_style` 未导入）
- 修复处方历史选中非 ID 列时 ValueError 崩溃
- 修复 `BaseDataView` 未初始化 `ResponsiveWidget` 导致响应式自动刷新失效
- 修复批量导入后缓存未重建导致新药材不显示
- 修复 `Inventory` 模型缺少 `category` 字段导致库存分类列空白
- 修复统计视图 SUM 为 NULL 时 TypeError
- 修复库存入库/出库/调整空值时 ValueError 崩溃
- 清理开处方模块语义错误的禁忌字段检查

### v3.3.0 (2026-06-21)
- 新增首页概览仪表盘：今日营收/处方/药材数/低库存预警卡片、近 7 天营收趋势条形图、最近处方列表
- 新增销售统计报表：时间范围筛选、热销药材 TOP10、营收趋势分析
- 新增配伍禁忌预警：基于十八反十九畏规则，添加药材时实时提醒，保存处方前最终确认
- 修复 `ImportThread` 线程安全问题：改用独立 worker 连接，避免与主线程共享 cursor
- Service 层统一缓存同步：create/update/delete 自动失效缓存
- 日志改用 `RotatingFileHandler`：单文件 10MB，保留 5 个备份
- 引入 pytest 测试框架：新增 26 个单元测试，配置 GitHub Actions CI

### v3.2.3 (2026-06-12)
- View 层统一继承 `BaseDataView`，消除响应式表格重复代码
- 所有 View 通过 Service 层访问数据，不再直接写 SQL
- `MedicineDialog` 添加/编辑时调用 `MedicineValidator` 完整验证
- `InventoryView` 库存状态过滤下推到 SQL WHERE 子句
- `MedicineView` 缓存初始化改用 `MedicineService.get_all_as_dicts()`
- `PrescriptionService.get_all` 新增 `load_items` 参数支持
- `InventoryService.get_all` 新增 `keyword` 和 `stock_status` 过滤参数

### v3.0.0 (2026-05-14)
- 修复数据导出崩溃问题（dict 切片 TypeError）
- 修复处方删除快速双击竞态问题
- 修复数据库事务原子性（execute 自动 commit 破坏显式事务）
- 修复 Database 单例线程安全（添加 threading.Lock 保护）
- 修复自动更新 SSL 证书验证（移除不安全的 CERT_NONE）
- 统一 Service 层验证器调用（使用 `MedicineValidator` 替代宽松验证）
- 声明 openpyxl 依赖
