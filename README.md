# 中药材销售管理系统 v1.0.0

> 面向中医诊所 / 中药房的桌面端开方与销售管理软件，内置 400 味药材库、32 张经典方剂模板、十八反十九畏配伍禁忌实时预警、患者过敏史冲突检测、批次效期 FEFO 出库。

基于 **Tauri 2.x + React 18 + Rust** 构建，安装包仅 3 MB，启动秒开，原生 Windows 体验。

---

## 截图与特性

- **首页看板**：今日营收与处方数横幅、近 7 天营收趋势、低库存预警（带「去入库」直达）、最近 5 张处方（双击跳转详情）
- **药材管理**：400 味内置中药材（含别名、分类、药性、归经、功效、主治、用法、用量、禁忌、备注）、按分类筛选、CSV 批量导入导出、详情 Drawer
- **智能开方**：药材检索 + 32 张经典方剂一键导入 + 十八反十九畏自动预警 + **患者过敏史冲突检测** + 默认剂量从 `dosage` 字段解析
- **库存管理**：批次 + 效期管理、FEFO 近效期优先出库、入库/出库 Modal 带余量提示、低/零库存行背景高亮、库存变更历史 Drawer、效期预警横幅
- **处方历史**：日期范围 + 关键字后端筛选、处方打印、删除自动按批次精确回扣库存、CSV 导出、复制到处方（复诊一键带入原方）
- **销售统计**：5 种时间范围 + 纯 SVG 销售趋势折线图（销售额 + 处方数双线）、热销药材 TOP10、CSV 导出
- **患者档案**：患者 CRUD + 过敏史 + 既往病史、详情 Drawer 展示历史处方 + 消费统计 + 复诊一键复制处方
- **系统设置**：数据备份与还原（MD5 校验）+ 备份删除、操作日志查询、Gitee 无感自动更新（启动后台静默下载 + 弹窗提示安装）
- **安全加固**：CSP 策略、SQL 全参数化、路径遍历防护、金额服务端重算、CRUD 全事务原子化、处方删除按批次精确回扣

---

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端 | Rust + Tauri 2.x | `#[tauri::command]` 暴露 39 个 IPC 命令 |
| 数据库 | rusqlite (bundled SQLite) | WAL 模式 + 5 项 PRAGMA 优化，10 张业务表 |
| 前端 | React 18 + TypeScript 严格模式 | 函数组件 + Hooks |
| UI 库 | Ant Design 5.x | 中文 locale，路由懒加载，侧边栏可折叠 |
| 状态 | TanStack Query 5 | 服务端状态 + 自动失效 + staleTime 分级缓存 |
| 构建 | Vite 5 | 生产产物分包：antd / react / query / icons / date 五 vendor chunk |
| 测试 | Vitest + cargo test | 前端 67 测试 + 后端 62 测试 |

---

## 快速开始

### 环境要求

- **Node.js** ≥ 18
- **Rust** ≥ 1.70（推荐 stable-msvc 工具链，GNU 工具链构建可通过但测试 exe 运行报 `STATUS_ENTRYPOINT_NOT_FOUND`）
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
- **NSIS 安装包**：`src-tauri/target/release/bundle/nsis/中药材销售管理系统_1.1.0_x64-setup.exe`（约 3 MB）
- **便携 EXE**：`src-tauri/target/release/medicine-system.exe`（约 7 MB）

> NSIS 安装包采用 `perMachine` 模式，安装到 `Program Files`（所有用户可用），简体中文向导，运行时自动请求 UAC 提权，支持 `/S` 静默安装参数。

### 版本号同步

版本号以 `package.json` 为单一事实源（SSOT），通过 `scripts/sync-version.mjs` 自动同步到：

```
package.json → Cargo.toml / tauri.conf.json / install.bat / distrib/install.bat / Settings.tsx / MainLayout.tsx
```

修改版本号后执行：

```powershell
npm run version:sync
```

---

## 功能模块详解

### 1. 首页概览（Dashboard）

- 今日营收、今日处方数、药材总数、低库存品种数四张统计卡片
- 低库存预警列表（点击「去入库」直达库存管理）
- 最近 5 张处方快速查看（双击跳转历史页并自动打开详情）
- 四个快捷操作入口：开处方 / 新增药材 / 库存管理 / 批量导入

### 2. 药材管理（MedicineList）

- 内置 400 味中药材（含别名、分类、药性、归经、功效、主治、用法、用量、禁忌、备注）
- 按名称 / 别名 / 功效 / 主治模糊搜索
- 按分类（补虚药 / 清热药 / 解表药等 19 类）+ 药性筛选
- 新增 / 编辑 / 删除（删除前自动检查处方引用，被引用时禁止删除）
- 详情 Drawer（双击行或点击「详情」按钮）展示完整药材信息
- 一键导出全量药材 CSV（UTF-8 BOM，Excel 直接打开）

### 3. 开处方（Prescription）

- 左侧药材搜索面板：支持拼音 / 汉字 / 别名检索
- 右侧处方编辑：数量、单价可编辑，小计与总金额实时计算
- **患者姓名 AutoComplete**：选中已有患者自动回填年龄/性别/过敏史
- **过敏史冲突检测**：实时校验处方药材与患者过敏史，区分「药材名直接匹配」与「禁忌字段提及」两种命中
- **默认剂量解析**：从 `Medicine.dosage` 字段（如"3-9g"）解析推荐起始用量取下限，无法解析时回退 10g
- **配伍禁忌预警**：完整实现中医十八反（31 对）+ 十九畏（10 对），匹配采用「包含」策略兼容炮制前后缀（如「生甘草」匹配「甘草」）
- **经典方剂模板**：32 张经典方（四君子汤、六味地黄丸、桂枝汤等）一键导入，自动匹配药材
- **处方明细库存余量**：每味药下方显示当前库存，不足时红色预警
- 保存处方时跨批次 FEFO 扣减库存（事务保证，库存不足自动回滚）
- 总金额由服务端重新 sum 计算，不信任前端传入

### 4. 库存管理（Inventory）

- 四张统计卡片：在库品种、低库存预警、零库存、库存总价值（按药材去重，不因多批次重复计数）
- Segmented 筛选：全部 / 低库存 / 零库存 / 近效期
- **批次 + 效期管理**：一药多批次，每批次独立记录 batch_no / production_date / expiry_date
- **FEFO 近效期优先出库**：出库时自动按「近效期 → 无效期 → 入库时间」顺序跨批次扣减
- 入库 / 出库 Modal：操作人、备注、数量校验、批次号/生产日期/效期录入、库存余量提示
- **库存变更历史 Drawer**：点击「历史」按钮查看该药材所有出入库记录，支持类型颜色标识（入库=绿、出库=橙、退库=蓝）
- **效期预警横幅**：近 30 天到期/已过期批次红色标签提示
- **行背景高亮**：低库存行橙色背景、零库存行红色背景
- 一键导出当前筛选结果 CSV

### 5. 处方历史（History）

- **后端日期范围筛选**：RangePicker 选择起止日期，后端 SQL `date(created_at) BETWEEN` 过滤
- 患者姓名 / 诊断关键字搜索
- 处方详情 Drawer：药材明细表 + 总金额 + 配伍禁忌提示
- **复制到处方**：一键复制原方到处方页，复诊时调整剂量或换药后保存为新处方（sessionStorage 跨页传输，读后即清）
- 删除处方：事务内按 `prescription_item_batches` 关联表逐批次精确回扣库存
- 打印处方：iframe srcdoc 方案，HTML 转义防 XSS
- 处方号列固定左侧，操作列固定右侧，横向滚动不丢列
- CSV 导出当前筛选结果

### 6. 销售统计（Statistics）

- 5 种时间范围快捷切换：今日 / 本周 / 本月 / 本季 / 本年 + 自定义 RangePicker
- 营收、处方数、药材消耗总览
- **纯 SVG 销售趋势折线图**（零依赖）：销售额（朱砂红+面积填充）与处方数（草本绿）双折线，支持悬停查看数值、自动刻度、X 轴日期智能间隔
- 热销药材 TOP10 横向条形图
- 每日趋势明细表格
- CSV 导出（汇总信息头 + 每日趋势 + TOP10）

### 7. 患者档案（Patients）

- 患者 CRUD：姓名、性别、年龄、电话、地址、过敏史、既往病史、备注
- 详情 Drawer：历史处方列表 + 消费统计（总消费 / 处方数 / 首次就诊 / 末次就诊）
- **复诊一键复制处方**：详情页处方历史表格新增「复制」按钮，闭合患者复诊业务流程
- 通过 `patient_name` 与处方表关联
- CSV 导出

### 8. 批量导入（BatchImport）

- CSV 文件格式：16 字段（name, alias, category, ..., quantity, unit, price, min_stock）
- **N+1 查询优化**：循环前 `SELECT ... WHERE name IN (...)` 一次性预查所有已存在药材到 HashMap，循环内 O(1) 查找
- 预览表格：红色行表示数据问题
- 实时进度 + 错误日志
- UPSERT 语义：同名药材自动新建批次行（保留历史批次），不会覆盖库存
- 批次号冲突修复：同一批次时间戳内多行导入追加 `row_no` 区分

### 9. 系统设置（Settings）

- **版本信息**：当前版本 + 最新版本对比 + 更新日志
- **无感自动更新**：启动后延迟 1.5s 后台静默检查 Gitee Release，发现新版本流式下载到 `%APPDATA%/com.medicine.system/downloads/`，下载完成后弹窗提示"立即更新"，用户确认后调用 NSIS 静默安装（`/S`）+ 应用自动退出
- **手动更新路径**：手动点击"启动安装程序"显式走 NSIS 安装向导 UI
- **数据备份**：一键创建备份（含 MD5 校验），备份列表支持还原与删除
- **操作日志**：最近 100 条操作记录，按类型筛选（CREATE / UPDATE / DELETE / STOCK / IMPORT），颜色标识

---

## 数据库设计

数据库文件位于 `%APPDATA%\com.medicine.system\medicine_system.db`，10 张业务表 + 1 张迁移追踪表：

| 表名 | 用途 |
|------|------|
| `medicines` | 药材信息（名称 / 别名 / 分类 / 药性 / 功效等 12 字段） |
| `inventory` | 库存记录（批次号 / 数量 / 单位 / 单价 / 最低库存 / 生产日期 / 效期） |
| `prescriptions` | 处方主表（患者信息 / 诊断 / 总金额 / 开方日期） |
| `prescription_items` | 处方明细（药材 / 数量 / 单价 / 小计 / 批次 ID） |
| `prescription_item_batches` | 处方明细与批次扣减关联表（精确回扣） |
| `inventory_history` | 库存变更历史（入库 / 出库 / 退库 + 操作人 + 金额） |
| `patients` | 患者档案（姓名 / 性别 / 年龄 / 过敏史 / 病史等） |
| `operation_logs` | 操作日志（CREATE / UPDATE / DELETE / STOCK / IMPORT） |
| `schema_migrations` | SQL 迁移版本追踪（幂等执行） |

迁移脚本位于 `src-tauri/migrations/`（9 个文件），编译期 `include_str!` 嵌入二进制，启动时自动执行未应用的迁移。

### SQLite 性能优化

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
│   ├── api/tauri.ts              # Tauri invoke 封装（39 个命令）
│   ├── components/               # EmptyState / ErrorBoundary / StatCard / TrendChart / QueryErrorAlert 等
│   ├── data/                     # 处方模板 JSON
│   ├── hooks/                    # useCrudMutations / useCsvExport / useCopyToPrescription
│   ├── layouts/MainLayout.tsx    # 侧边栏（可折叠）+ 内容区布局
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
│   ├── services/templateService.ts # 方剂模板服务（类型守卫校验 JSON）
│   ├── types/index.ts            # TypeScript 类型定义
│   └── utils/                    # csv / format / print / inventory / allergy / dosage 工具
├── src-tauri/                    # Rust 后端
│   ├── src/
│   │   ├── lib.rs                # 应用入口 + 命令注册
│   │   ├── commands.rs           # 39 个 Tauri 命令 + 62 个单元测试
│   │   ├── compatibility.rs      # 配伍禁忌引擎
│   │   ├── db.rs                 # 数据库管理 + 迁移
│   │   ├── models.rs             # 数据模型
│   │   └── updater.rs            # 自动更新（含静默下载）
│   ├── migrations/               # SQL 迁移（9 个文件）
│   └── tauri.conf.json           # Tauri 配置
├── scripts/sync-version.mjs      # 版本号 SSOT 同步脚本
├── distrib/                      # 便携版分发目录（install.bat / uninstall.bat）
├── package.json
└── vite.config.ts                # 生产分包配置
```

---

## 测试

### 后端测试（62 个）

```powershell
cd src-tauri
cargo test --lib
```

覆盖：
- HTML 转义、CSV 模板、序列化往返
- 库存出入库事务、批次 FEFO 出库、同批合并、跨批扣减
- 处方创建扣库存 + 不足回滚 + 跨批次删除精确回扣
- 效期预警查询、低库存聚合
- 批量查询 N+1 消除、batch_import HashMap 预查模式
- 配伍禁忌（十八反/十九畏）
- 数据库迁移与外键
- 版本比较工具函数

### 前端测试（67 个）

```powershell
npm run test -- --run
```

覆盖：
- `utils/format.ts` 错误映射（10）
- `utils/csv.ts` 解析与生成（15）
- `utils/templateService.ts` 方剂模板（10）
- `utils/allergy.ts` 过敏关键词解析与冲突检测（11）
- `utils/dosage.ts` 默认剂量解析（7）
- `utils/inventory.ts` 库存聚合与效期状态（14）

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

1. 创建 `src-tauri/migrations/010_new_feature.sql`
2. 在 [db.rs](src-tauri/src/db.rs) 的 `MIGRATIONS` 数组注册：

```rust
const MIGRATIONS: &[(&str, &str)] = &[
    ("001_init", include_str!("../migrations/001_init.sql")),
    // ...
    ("010_new_feature", include_str!("../migrations/010_new_feature.sql")),
];
```

迁移系统自动执行新迁移，已执行过的跳过（幂等）。

### 发布新版本

1. 修改 `package.json` 的 `version` 字段
2. 执行 `npm run version:sync` 同步版本号到所有文件
3. 更新 `CHANGELOG.md`
4. 运行 `npm run tauri:build`
5. 提交代码并推送到 Gitee
6. 在 Gitee 创建新 Release（tag `v1.4.x`），上传 NSIS 安装包及配套的 `.sha256` 校验文件（客户端更新时自动做 SHA256 完整性校验）
7. 用户端启动时自动检测并提示更新

---

## 常见问题

**Q: 启动时白屏？**
A: 检查 WebView2 Runtime 是否安装（Win11 自带，Win10 需手动安装）；确认 `npm install` 已执行。

**Q: 数据库文件在哪？**
A: `%APPDATA%\com.medicine.system\medicine_system.db`。删除后重启应用会自动重建表结构与种子数据。

**Q: 如何重置数据？**
A: 删除数据库文件后重启，或在 Settings 页面还原早期备份。应用启动时会检测备份是否超过 7 天并提醒。

**Q: 打印无响应？**
A: 确保系统已安装打印机驱动，Tauri 使用系统打印对话框。

**Q: 自动更新失败？**
A: 检查网络、确认 Gitee Release 已发布且包含 `.exe` 安装包与 `.sha256` 校验文件，或手动下载覆盖安装。

**Q: Windows SmartScreen 提示「未知发布者」？**
A: 因未购买代码签名证书，首次安装时会提示。点击「仍要运行」即可。后续考虑购买 OV/EV 证书消除警告（见 [issue IK3Y7P](https://gitee.com/flyxjin/doctor/issues/IK3Y7P)）。

**Q: 没有后端也想看界面？**
A: `npm run dev` 后用普通浏览器打开 <http://localhost:1420> 即进入演示模式（内置拟真数据，仅内存不落盘）；Tauri 窗口内不受影响。

---

## 版本历史

详见 [CHANGELOG.md](CHANGELOG.md)。

- **v1.4.0**（2026-09-24）：**数据正确性修复 + 安全加固 + UI/商业功能完善** — 删除处方双重回扣库存修复、时区口径统一、更新包 SHA256 校验 + 下载源白名单 + 安装路径校验、未保存处方拦截、备份提醒、帮助/关于弹窗、浏览器演示模式、深色模式对比度修复、CI 工作流修复（详见 [CHANGELOG.md](CHANGELOG.md)）
- **v1.3.0**（2026-08-06）：性能调优 + 全局快捷键 + 主题切换 + 方剂模板扩充 + 数据导入导出统一入口
- **v1.2.0**（2026-08-02）：健壮性增强 + 错误 UI 完善
- **v1.1.0**（2026-07-28）：处方 PDF 导出功能 + GitHub Actions CI/Release 工作流
- **v1.0.0**（2026-07-28）：**里程碑版本** — 功能完成度达到 1.0 标准，定位为生产主推版本；Python 版同步进入维护模式。详见 [docs/ROADMAP.md](docs/ROADMAP.md)
- **v0.3.16**（2026-07-28）：新增用户操作手册（软著申请材料）
- **v0.3.15**（2026-07-25）：代码卫生改进（死代码清理 + 类型逃逸收窄 + 测试补强）
- **v0.3.14**（2026-07-25）：代码质量改进（brooks-lint 修复）
- **v0.3.13**（2026-07-25）：今日概览横幅 + 三页 CSV 导出
- **v0.3.12**（2026-07-25）：患者过敏史预警 + 默认剂量解析 + 查询错误重试 + staleTime 分级缓存
- **v0.3.11**（2026-07-25）：销售趋势可视化 + 库存状态高亮 + 处方库存预警 + 患者复诊复制
- **v0.3.10**（2026-07-25）：Dashboard 增强 + 药材详情 + 备份删除 + 库存导出
- **v0.3.9**（2026-07-25）：6 个处方 Bug 修复 + 侧边栏折叠 + 菜单分组
- **v0.3.8**（2026-07-23）：处方复制/再来一剂
- **v0.3.7**（2026-07-23）：跨批次处方删除回扣 Bug 修复 + 7 项其他改进
- **v0.3.6**（2026-07-23）：桌面图标重新设计
- **v0.3.5**（2026-07-23）：批次 + 效期管理 + FEFO 出库
- **v0.3.4**（2026-07-23）：药材库扩充至 400 味
- **v0.3.3**（2026-07-23）：桌面图标 + formatError + 出库预校验
- **v0.3.2**（2026-07-23）：无感自动更新
- **v0.3.1**（2026-07-22）：价格单位修复
- **v0.3.0**（2026-07-22）：库存变更历史 + 操作日志 + 后端日期筛选 + 事务原子化 + WAL 模式
- **v0.2.0**（2026-07-21）：319 味药材 + 32 张方剂模板 + 患者档案 + 批量导入 + 备份还原
- **v0.1.0**（2026-07-20）：初始版本

---

## License

[MIT License](../LICENSE) — Copyright (c) 2026 东方本草

本项目继承根仓库的 MIT 协议，允许商用、闭源衍生，仅需保留版权声明。
