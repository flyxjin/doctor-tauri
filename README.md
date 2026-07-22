# 中药材销售管理系统 v0.3.0

> 面向中医诊所 / 中药房的桌面端开方与销售管理软件，内置 319 味药材库、32 张经典方剂模板、十八反十九畏配伍禁忌实时预警。

基于 **Tauri 2.x + React 18 + Rust** 构建，安装包仅 3 MB，启动秒开，原生 Windows 体验。

---

## 截图与特性

- **首页看板**：今日营收、处方数、低库存预警、近 7 天营收趋势
- **药材管理**：319 味内置药材（含市场参考价）、分类筛选、CSV 批量导入导出
- **智能开方**：药材检索 + 32 张经典方剂一键导入 + 十八反十九畏自动预警
- **库存管理**：入库 / 出库 / 变更历史 Drawer、低库存 / 零库存分级预警、库存总价值统计
- **处方历史**：日期范围 + 关键字后端筛选、处方打印、删除自动回扣库存
- **销售统计**：5 种时间范围（日/周/月/季/年）、热销药材 TOP10、每日趋势
- **患者档案**：患者 CRUD + 历史处方关联 + 消费统计
- **系统设置**：数据备份与还原（MD5 校验）、操作日志查询、Gitee 自动更新
- **安全加固**：CSP 策略、SQL 全参数化、路径遍历防护、金额服务端重算、CRUD 全事务原子化

---

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端 | Rust + Tauri 2.x | `#[tauri::command]` 暴露 31 个 IPC 命令 |
| 数据库 | rusqlite (bundled SQLite) | WAL 模式 + 5 项 PRAGMA 优化，7 张业务表 |
| 前端 | React 18 + TypeScript 严格模式 | 函数组件 + Hooks |
| UI 库 | Ant Design 5.x | 中文 locale，路由懒加载 |
| 状态 | TanStack Query 5 | 服务端状态 + 自动失效 |
| 构建 | Vite 5 | 生产产物分包：antd / react / query / icons 四 vendor chunk |
| 测试 | Vitest + cargo test | 前端 35 测试 + 后端 46 测试 |

---

## 快速开始

### 环境要求

- **Node.js** ≥ 18
- **Rust** ≥ 1.70（推荐 stable-msvc 工具链）
- Windows 10/11 x64（需 WebView2 Runtime，Win11 自带）

### 开发模式

```powershell
cd tauri_app
npm install
npm run tauri:dev
```

首次启动需编译 Rust 依赖（约 3-5 分钟），后续启动 < 30 秒。前端热更新即时生效。

### 生产构建

```powershell
npm run tauri:build
```

产物位置：
- **NSIS 安装包**：`src-tauri/target/release/bundle/nsis/中药材销售管理系统_0.3.0_x64-setup.exe`（约 3 MB）
- **便携 EXE**：`src-tauri/target/release/medicine-system.exe`（约 7 MB）

> NSIS 安装包采用 `perMachine` 模式，安装到 `Program Files`（所有用户可用），简体中文向导，运行时自动请求 UAC 提权。

### 便携版使用

将 `distrib/` 目录整体复制到目标机器，右键 `install.bat` → 以管理员身份运行，自动安装到 `Program Files`、创建桌面与开始菜单快捷方式、注册到「添加/删除程序」。

---

## 功能模块详解

### 1. 首页概览（Dashboard）

- 今日营收、今日处方数、药材总数、低库存品种数四张统计卡片
- 近 7 天营收条形图
- 低库存预警列表（点击直达入库）
- 最近 5 张处方快速查看

### 2. 药材管理（MedicineList）

- 内置 319 味中药材（含别名、分类、药性、归经、功效、主治、用法、用量、禁忌、备注）
- 按名称 / 别名 / 功效 / 主治模糊搜索
- 按分类（补虚药 / 清热药 / 解表药等 18 类）+ 药性筛选
- 新增 / 编辑 / 删除（删除前自动检查处方引用，被引用时禁止删除）
- 一键导出全量药材 CSV（UTF-8 BOM，Excel 直接打开）

### 3. 开处方（Prescription）

- 左侧药材搜索面板：支持拼音 / 汉字 / 别名检索
- 右侧处方编辑：数量、单价可编辑，小计与总金额实时计算
- **配伍禁忌预警**：完整实现中医十八反（31 对）+ 十九畏（10 对），匹配采用「包含」策略兼容炮制前后缀（如「生甘草」匹配「甘草」）
- **经典方剂模板**：32 张经典方（四君子汤、六味地黄丸、桂枝汤等）一键导入，自动匹配药材
- 保存处方时原子扣减库存（事务保证，库存不足自动回滚）
- 处方日期可手动指定（保留历史开方时间）
- 总金额由服务端重新 sum 计算，不信任前端传入

### 4. 库存管理（Inventory）

- 四张统计卡片：在库品种、低库存预警、零库存、库存总价值
- Segmented 三态筛选：全部 / 低库存 / 零库存
- 入库 / 出库 Modal：操作人、备注、数量校验
- **库存变更历史 Drawer**（v0.3.0 新增）：点击「历史」按钮查看该药材所有出入库记录，支持类型颜色标识（入库=绿、出库=橙、退库=蓝）
- 出库时自动检查库存不足，事务保证数据一致

### 5. 处方历史（History）

- **后端日期范围筛选**（v0.3.0 优化）：RangePicker 选择起止日期，后端 SQL `date(created_at) BETWEEN` 过滤
- 患者姓名 / 诊断关键字搜索
- 处方详情 Modal：药材明细表 + 总金额 + 配伍禁忌提示
- 删除处方：事务内回扣库存 + 删除明细 + 删除主表
- 打印处方：iframe srcdoc 方案，HTML 转义防 XSS

### 6. 销售统计（Statistics）

- 5 种时间范围快捷切换：今日 / 本周 / 本月 / 本季 / 本年
- 营收、处方数、药材消耗总览
- 热销药材 TOP10 横向条形图
- 每日销售趋势折线图

### 7. 患者档案（Patients）

- 患者 CRUD：姓名、性别、年龄、电话、地址、过敏史、既往病史、备注
- 点击患者行展开：历史处方列表 + 消费统计（总消费 / 处方数 / 首次就诊 / 末次就诊）
- 通过 `patient_name` 与处方表关联

### 8. 批量导入（BatchImport）

- CSV 文件格式：16 字段（name, alias, category, ..., quantity, unit, price, min_stock）
- **N+1 查询优化**（v0.3.0）：循环前 `SELECT ... WHERE name IN (...)` 一次性预查所有已存在药材到 HashMap，循环内 O(1) 查找，同批次重复名称自动走 UPDATE
- 预览表格：红色行表示数据问题
- 实时进度 + 错误日志
- UPSERT 语义：同名药材自动更新，不会重复创建

### 9. 系统设置（Settings）

- **版本信息**：当前版本 + 最新版本对比 + 更新日志
- **自动更新**：检查更新 → 下载（实时进度条）→ 启动安装程序，源为 Gitee Releases API
- **数据备份**：一键创建备份（含 MD5 校验），备份列表支持还原
- **操作日志**（v0.3.0 新增）：最近 100 条操作记录，按类型筛选（CREATE / UPDATE / DELETE / STOCK / IMPORT），颜色标识

---

## 数据库设计

数据库文件位于 `%APPDATA%\com.medicine.system\medicine_system.db`，7 张业务表 + 1 张迁移追踪表：

| 表名 | 用途 |
|------|------|
| `medicines` | 药材信息（名称 / 别名 / 分类 / 药性 / 功效等 12 字段） |
| `inventory` | 库存记录（数量 / 单位 / 单价 / 最低库存） |
| `prescriptions` | 处方主表（患者信息 / 诊断 / 总金额 / 开方日期） |
| `prescription_items` | 处方明细（药材 / 数量 / 单价 / 小计） |
| `inventory_history` | 库存变更历史（入库 / 出库 / 退库 + 操作人 + 金额） |
| `operation_logs` | 操作日志（CREATE / UPDATE / DELETE / STOCK / IMPORT） |
| `data_version` | 内置数据装载版本追踪 |
| `schema_migrations` | SQL 迁移版本追踪（幂等执行） |

迁移脚本位于 `src-tauri/migrations/`，编译期 `include_str!` 嵌入二进制，启动时自动执行未应用的迁移。

### SQLite 性能优化（v0.3.0）

```sql
PRAGMA journal_mode = WAL;       -- 读写并发
PRAGMA synchronous = NORMAL;     -- WAL 模式下安全
PRAGMA busy_timeout = 5000;      -- 锁等待 5 秒
PRAGMA cache_size = -8000;       -- 8MB 页缓存
PRAGMA foreign_keys = ON;        -- 外键级联
```

---

## 配伍禁忌规则

完整保留中医十八反、十九畏配伍禁忌规则，源码位于 [compatibility.rs](src-tauri/src/compatibility.rs)：

- **十八反·甘草反甘遂/大戟/海藻/芫花**（4 对）
- **十八反·乌头（川乌/草乌/附子）反贝母/瓜蒌/半夏/白蔹/白及**（20 对）
- **十八反·藜芦反人参/沙参/丹参/玄参/苦参/细辛/芍药**（7 对）
- **十九畏**（10 对，如硫黄畏朴硝、巴豆畏牵牛、人参畏五灵脂等）

匹配采用「包含」策略：`"生甘草"` 匹配 `"甘草"`，兼容炮制前后缀。

---

## 项目结构

```
tauri_app/
├── src/                          # React 前端
│   ├── api/tauri.ts              # Tauri invoke 封装（31 个命令）
│   ├── components/               # EmptyState / ErrorBoundary / StatCard 等
│   ├── data/                     # 处方模板 JSON
│   ├── hooks/useCrudMutations.ts # 通用 CRUD mutation Hook
│   ├── layouts/MainLayout.tsx    # 侧边栏 + 内容区布局
│   ├── pages/                    # 9 个页面
│   │   ├── Dashboard.tsx         # 首页概览
│   │   ├── MedicineList.tsx      # 药材管理
│   │   ├── Prescription.tsx      # 开处方
│   │   ├── Inventory.tsx         # 库存管理
│   │   ├── History.tsx           # 处方历史
│   │   ├── Statistics.tsx        # 销售统计
│   │   ├── Patients.tsx          # 患者档案
│   │   ├── BatchImport.tsx       # 批量导入
│   │   └── Settings.tsx          # 系统设置
│   ├── services/templateService.ts # 方剂模板服务
│   ├── types/index.ts            # TypeScript 类型定义
│   └── utils/                    # csv / format / print 工具
├── src-tauri/                    # Rust 后端
│   ├── src/
│   │   ├── lib.rs                # 应用入口 + 命令注册
│   │   ├── commands.rs           # 31 个 Tauri 命令 + 46 个单元测试
│   │   ├── compatibility.rs      # 配伍禁忌引擎
│   │   ├── db.rs                 # 数据库管理 + 迁移
│   │   ├── models.rs             # 数据模型
│   │   └── updater.rs            # 自动更新
│   ├── migrations/               # SQL 迁移（5 个文件）
│   └── tauri.conf.json           # Tauri 配置
├── distrib/                      # 便携版分发目录
│   ├── medicine-system.exe       # 便携 EXE
│   ├── install.bat               # 安装脚本
│   └── uninstall.bat             # 卸载脚本
├── package.json
└── vite.config.ts                # 生产分包配置
```

---

## 测试

### 后端测试（46 个）

```powershell
cd src-tauri
cargo test
```

覆盖：
- HTML 转义（2）、CSV 模板（1）、序列化往返（2）
- 库存出入库事务（3）、处方创建扣库存 + 不足回滚 + 删除回扣（3）
- 批量查询 N+1 消除（1）
- 库存变更历史筛选（2，v0.3.0 新增）
- 操作日志筛选（2，v0.3.0 新增）
- batch_import HashMap 预查模式（2，v0.3.0 新增）
- 配伍禁忌（10）
- 数据库迁移与外键（10）

### 前端测试（35 个）

```powershell
npm test
```

覆盖：
- `format.ts` 工具函数（10）
- `csv.ts` 解析与生成（15）
- `templateService.ts` 方剂模板（10）

### 代码质量

```powershell
npx tsc --noEmit   # TypeScript 严格模式 0 错误
npx eslint src     # 0 错误
```

---

## 开发指南

### 添加新的 Tauri 命令

1. 在 [commands.rs](src-tauri/src/commands.rs) 定义：

```rust
#[tauri::command]
pub fn my_command(arg: String, state: State<'_, DbState>) -> Result<String, String> {
    let conn = state.lock()?;
    // 业务逻辑
    Ok("result".to_string())
}
```

2. 在 [lib.rs](src-tauri/src/lib.rs) 注册：

```rust
.invoke_handler(tauri::generate_handler![
    commands::my_command,
    // ...
])
```

3. 前端调用：

```typescript
import { invoke } from '@tauri-apps/api/core';
const result = await invoke<string>('my_command', { arg: 'value' });
```

### 添加数据库迁移

1. 创建 `src-tauri/migrations/006_new_feature.sql`
2. 在 [db.rs](src-tauri/src/db.rs) 的 `MIGRATIONS` 数组注册：

```rust
const MIGRATIONS: &[(&str, &str)] = &[
    ("001_init", include_str!("../migrations/001_init.sql")),
    // ...
    ("006_new_feature", include_str!("../migrations/006_new_feature.sql")),
];
```

迁移系统自动执行新迁移，已执行过的跳过（幂等）。

### 发布新版本

1. 更新版本号：`Cargo.toml` + `tauri.conf.json` + `package.json` + `Settings.tsx` + `install.bat`
2. 运行 `npm run tauri:build`
3. 拷贝产物到 `distrib/`
4. 在 Gitee 创建新 Release，上传 NSIS 安装包
5. 用户端启动时自动检测并提示更新

---

## 常见问题

**Q: 启动时白屏？**
A: 检查 WebView2 Runtime 是否安装（Win11 自带，Win10 需手动安装）；确认 `npm install` 已执行。

**Q: 数据库文件在哪？**
A: `%APPDATA%\com.medicine.system\medicine_system.db`。删除后重启应用会自动重建表结构与种子数据。

**Q: 如何重置数据？**
A: 删除数据库文件后重启，或在 Settings 页面还原早期备份。

**Q: 打印无响应？**
A: 确保系统已安装打印机驱动，Tauri 使用系统打印对话框。

**Q: 自动更新失败？**
A: 检查网络、确认 Gitee Release 已发布且包含 `.exe` 安装包，或手动下载覆盖安装。

---

## 版本历史

详见 [CHANGELOG.md](CHANGELOG.md)。

- **v0.3.0**（2026-07-22）：库存变更历史、操作日志查询、batch_import N+1 优化、6 个 CRUD 事务原子化、WAL 模式、路径遍历防护
- **v0.2.0**（2026-07-21）：319 味药材、32 张方剂模板、真实市场价、自定义图标
- **v0.1.0**（2026-07-20）：初始版本，基础 CRUD + 开方 + 库存 + 统计

---

## License

[MIT License](../LICENSE) — Copyright (c) 2026 东方本草

本项目继承根仓库的 MIT 协议，允许商用、闭源衍生，仅需保留版权声明。
