# 架构总览（ARCHITECTURE）

> 面向维护者的代码地图。读完本文应能在 10 分钟内定位任何功能的实现位置。
> 配套阅读：[README](../README.md)（功能视角）、[软著申请指南](软著申请指南.md)。

## 1. 技术形态

桌面单机应用：**Tauri 2.x**（Rust 后端 + 系统 WebView 前端），数据存本地 SQLite，无服务端。

```
┌───────────── React 前端（WebView） ─────────────┐
│ pages/* ── useQuery/useMutation ── api/tauri.ts │
│                                          │ invoke │
└──────────────────────────────────────────┼────────┘
                                           ▼
┌──────────────── Rust 后端（src-tauri）────────────┐
│ lib.rs: 插件/State 注册 + 启动流程（迁移→自动备份）│
│ commands.rs: 39 个 #[tauri::command] IPC 接口     │
│ db.rs: SQLite 连接（Mutex 串行）+ 版本化迁移       │
│ backup.rs: 备份核心（手动命令与每日自动共用）       │
│ updater.rs: Gitee Release 检查/下载/校验/安装      │
│ compatibility.rs: 十八反十九畏规则（纯数据+匹配）   │
│ models.rs: 与前端 types/index.ts 一一对应的 DTO    │
└──────────────────────────────────────────────────┘
```

## 2. 目录职责速查

| 文件 | 职责 | 备注 |
|------|------|------|
| `src/api/tauri.ts` | **唯一** invoke 封装层，页面不得直接 import `@tauri-apps/api` | 命令名/参数 camelCase |
| `src/main.tsx` | QueryClient 全局配置 + 浏览器演示模式安装 | 演示模式见 §4.8 |
| `src/pages/*` | 9 个页面，antd 组件 + react-query | 单页 300~800 行 |
| `src/hooks/*` | useCrudMutations（CRUD 失效模板）/ useCsvExport / useCopyToPrescription | |
| `src/utils/csv.ts` | CSV 转义/解析（RFC4180 引号内换行）+ 公式注入防护 + Excel 行转换 | 前后端防护对齐 |
| `src/utils/inventory.ts` | 库存聚合与效期状态的**唯一口径**（aggregateInventory/expiryStatus） | |
| `src/mocks/tauriMock.ts` | 浏览器演示模式的内存数据库（拦截 invoke） | 仅 DEV 生效 |
| `src-tauri/src/lib.rs` | 插件/命令注册 + 启动流程（建库→迁移→每日自动备份） | |
| `src-tauri/src/commands.rs` | 全部 IPC 命令，按业务域分区（文件头有模块目录） | 待拆分，见 §6 |
| `src-tauri/src/db.rs` | 连接 PRAGMA 调优 + `MIGRATIONS` 数组 + schema_migrations 幂等迁移 | 新迁移在此数组追加 |
| `src-tauri/src/backup.rs` | 备份核心：checkpoint→复制→SHA256→清单；每日自动备份与保留策略 | 手动命令与启动共用 |
| `src-tauri/src/updater.rs` | 更新链路：Gitee API → 版本比较 → 下载（URL 白名单）→ SHA256 → 安装（路径校验） | |
| `src-tauri/migrations/*.sql` | 编译期 `include_str!` 嵌入，文件名升序执行 | 命名 `NNN_描述.sql` |

## 3. 关键机制（改动前必读）

### 3.1 批次与 FEFO 出库
- 库存以**批次**为最小单位（`inventory` 表，一药多批）；
- 出库/开方扣减统一走 `select_batches_fefo`：`ORDER BY 无效期最后 → expiry_date ASC → created_at ASC`，逐批扣完自动切下一批，总量不足时报缺口并**不做部分扣减**；
- 效期/生产日期入库时经 `validate_ymd` 严格校验 `YYYY-MM-DD`——字符串排序直接参与 FEFO，格式不校验会静默错乱。

### 3.2 处方扣减与删除回扣（最易出错的区域）
- 开方时：每个明细行按 FEFO 扣减，并把每批次的扣减量写入关联表 `prescription_item_batches`（pib）；
- 删除处方：`restore_prescription_stock` 统一入口——
  - **新数据**（有 pib 明细）：按明细精确回扣；pib 按（处方，药材）聚合覆盖同名多行，**必须按 medicine_id 去重只回扣一次**（历史 bug，有回归测试）；
  - **老数据**（009 迁移前无明细）：各行独立整量回扣到 fallback 批次（"初始库存"或第一批次）；
  - 所有批次均已删除时懒创建"退库恢复"批次接住回扣量（防静默丢失）。

### 3.3 时区约定（易踩坑）
- `prescriptions` / `inventory_history` / `operation_logs` 的 `created_at` 以 **UTC** 存储（`CURRENT_TIMESTAMP` 默认值）；
- 查询侧涉及"今天/日期范围"的必须转到本地口径：聚合用 `date(created_at,'localtime')`，范围过滤用半开区间 `created_at >= datetime(?,'utc') AND < datetime(?,'+1 day','utc')`（同时保住索引）；
- 例外：`patients` 表建表即用 `datetime('now','localtime')`（历史遗留），新查询勿混用两种口径。

### 3.4 金额与浮点
- 金额一律 `round_amount(quantity * price)` 服务端重算，不信任前端；
- FEFO 余量判定用 `STOCK_EPSILON = 1e-6` 容差，防浮点累加残值误报库存不足。

### 3.5 数据库迁移
- 新增迁移：写 `migrations/NNN_描述.sql` → 在 `db.rs` 的 `MIGRATIONS` 数组按序注册（`include_str!` 编译期嵌入）；
- 幂等：`schema_migrations` 记录已应用版本；恢复旧备份后会自动补跑迁移（`restore_backup` 内）。

### 3.6 备份体系
- 手动：`create_backup` 命令；自动：每日首次启动若当天无备份则静默创建 `medicine_system_auto_*`；
- 仅自动备份参与保留策略（14 份），手动备份永不清理；
- 每份备份附 SHA256 清单（`.json`），还原前校验。

### 3.7 自动更新链路（updater.rs）
`check_for_update`（Gitee API，解析 .exe 资产与 .sha256 侧车）→ `is_newer_version`（语义化分段补齐比较）→ `download_update`（**URL 白名单 gitee.com** + 大小校验 + SHA256 校验）→ `install_update`（**路径必须 canonicalize 在 downloads/ 内**）。三层校验是纵深防御：即使 renderer 被注入也无法借 IPC 拉取/执行任意程序。Release 侧由 `.github/workflows/release.yml` 产出 `.sha256` 侧车并可选签名。

### 3.8 浏览器演示模式
`main.tsx`：`import.meta.env.DEV && !('__TAURI_INTERNALS__' in window)` 时动态加载 `src/mocks/tauriMock.ts`，用内存数据库拦截全部 invoke。Tauri 窗口内永不生效；用于 UI 开发与演示。

### 3.9 前端缓存失效约定
- 全局**不设** `placeholderData`；仅三个搜索列表页（History/MedicineList/Patients）显式 `keepPreviousData`；
- mutation 后需显式失效关联缓存，注意 **`['prescriptions']` 前缀匹配不到 `['patient-prescriptions', …]`**（历史踩坑，现两处方 mutation 已补齐全量失效）；
- 库存聚合口径唯一来源是 `utils/inventory.ts` 的 `aggregateInventory`，勿在页面重写。

## 4. 测试地图

| 层 | 位置 | 数量 | 覆盖 |
|----|------|------|------|
| 后端 | `commands.rs` 内 `mod tests` | 76 | FEFO 顺序/跨批回扣/双重回扣回归/删除回退/导入规则/校验和/URL 白名单/日期校验/CSV 注入 |
| 后端 | `backup.rs` / `db.rs` / `updater.rs` | 3+若干 | 备份往返与保留策略 / 迁移幂等 / 版本比较与 SHA256 解析 |
| 前端 | `src/**/*.test.ts` | 79 | CSV 往返（引号内换行/注入防护）/ 剂量解析 / 过敏匹配 / 库存聚合 / 模板服务 |

运行：`npm test`（vitest）、`cargo test --lib`；门禁：CI 同时跑 `tsc` / `eslint` / `cargo clippy -D warnings` / `cargo fmt --check`。

## 5. 代码约定

- 后端错误信息一律中文返回前端；SQL 全参数化；Tauri 命令保持扁平参数（即 IPC 契约，不聚合结构体）；
- 前端组件颜色必须用 CSS 变量（`--text-color` 等），深色模式下硬编码 hex 会不可见；
- 版本号 SSOT 是 `package.json`，改后跑 `npm run version:sync`；
- 提交信息用中文 conventional 风格（feat/fix/chore/docs + 中文摘要）。

## 6. 待办重构：commands.rs 按域拆分（预案）

`commands.rs` 约 3,900 行为最大可维护性债务，已按域分区并在文件头维护目录。拆分预案（执行时编译器驱动即可）：

| 目标模块 | 内容（现 commands.rs 行号段） |
|----------|------------------------------|
| `commands/mod.rs` | 共享辅助：log_operation、validate_ymd、parse_f64_or、html_escape、compute_file_sha256、round_amount、map_*_row 行映射；`mod` 声明与 `pub use` 再导出（lib.rs 路径不变） |
| `commands/medicine.rs` | 药材 CRUD（L44-261）+ check_compatibility 薄封装 |
| `commands/inventory.rs` | 库存命令 + BatchDeduction + select_batches_fefo（L263-739） |
| `commands/prescription.rs` | 处方命令 + 批次回扣辅助族（L741-1230） |
| `commands/patient.rs` | 患者命令（L1232-1443） |
| `commands/stats.rs` | 看板与统计（L1445-1672） |
| `commands/import_export.rs` | 批量导入/导出/模板/保存下载（L1686-2067，含 sanitize_csv_formula） |
| `commands/logs.rs` | 操作日志查询（L2069-2137） |
| `commands/system.rs` | 备份四命令（compute_file_sha256 留 mod.rs） |
| `commands/tests.rs` | 现有 `mod tests` 原样迁移（`use super::*`），依赖 mod.rs 的 `pub(crate)` 再导出 |

执行要点：①纯搬移不改逻辑；②域内私有辅助改 `pub(crate)`；③`lib.rs` 因再导出无需改动；④每步 `cargo test --lib` 驱动。注意本仓库 Mimosa 钩子禁止经 Bash 写源码，需用 Write/Edit 工具搬运。

---

*最后更新：2026-09-27（对应 V1.4.0，后端 79 + 前端 79 测试）*
