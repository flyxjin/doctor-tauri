# 中药材销售管理系统

> 面向中医诊所 / 中药房的桌面端开方与销售管理软件。内置 300+ 味药材库、32 张经典方剂模板、十八反十九畏配伍禁忌实时预警。

本项目同时提供 **两套独立实现**，功能等价但技术栈完全不同，开发者可按需选择：

| 方案 | 路径 | 技术栈 | 体积 | 推荐场景 |
|------|------|--------|------|---------|
| **方案 A · Python 版** | [`python_app/`](python_app) | Python + PySide6 + SQLAlchemy | ~50 MB | 快速开发、学习 Qt、单文件分发 |
| **方案 B · Tauri 版** ⭐ | [`tauri_app/`](tauri_app) | Rust + React 18 + TypeScript | ~3 MB | **生产首选**、极致体积、现代 UI、自动更新 |

两套方案共享同一产品需求与功能矩阵，数据库结构对齐，**数据可互通**（备份 / 还原）。

---

## 功能矩阵

| 功能 | 方案 A (Python) | 方案 B (Tauri) |
|------|:---:|:---:|
| 首页概览仪表盘 | ✅ | ✅ |
| 药材管理（300+ 味内置） | ✅ | ✅ |
| 智能开方 + 配伍禁忌预警 | ✅ | ✅ |
| 32 张经典方剂模板 | ✅ | ✅ |
| 库存管理 + 变更历史 | ✅ | ✅ |
| 处方历史 + 日期筛选 | ✅ | ✅ |
| 销售统计（5 种时间范围） | ✅ | ✅ |
| 患者档案 + 历史处方 | ✅ | ✅ |
| 批量导入（CSV） | ✅ | ✅ |
| 数据备份与还原 | ✅ | ✅ |
| Gitee 自动更新 | ✅ | ✅ |
| 操作日志查询 | ✅ | ✅ |
| NSIS 安装包 | ❌（便携 exe） | ✅ |
| 代码签名 | ❌ | ⚠️（需购买证书） |

---

## 方案 B · Tauri 版（生产首选）⭐

### 为什么推荐 Tauri 版？

- **体积小 16 倍**：NSIS 安装包 3 MB vs Python 打包后 ~50 MB
- **启动秒开**：Rust 原生编译，无 Python 解释器冷启动开销
- **现代 Web UI**：React + Ant Design 5，组件丰富、样式灵活
- **内存占用低**：WebView2 渲染，无 Qt 运行时
- **安全加固**：CSP 策略、SQL 全参数化、路径遍历防护、金额服务端重算、CRUD 全事务原子化
- **自动更新**：内置 Gitee Releases 检测 + 流式下载 + 一键安装

### 快速开始

**环境要求**：Node.js ≥ 18、Rust ≥ 1.70（推荐 `stable-msvc` 工具链）、Windows 10/11 x64（需 WebView2 Runtime，Win11 自带）

```powershell
cd tauri_app
npm install
npm run tauri:dev      # 开发模式，热更新
npm run tauri:build    # 生产构建
```

**产物位置**：
- NSIS 安装包：`tauri_app/src-tauri/target/release/bundle/nsis/中药材销售管理系统_0.3.0_x64-setup.exe`（约 3 MB）
- 便携 EXE：`tauri_app/src-tauri/target/release/medicine-system.exe`（约 7 MB）

> NSIS 采用 `perMachine` 模式，安装到 `Program Files`，简体中文向导，运行时自动请求 UAC 提权。

### 技术架构

```
┌─────────────────────────────────────────────────┐
│              React 18 + TypeScript              │
│   (Ant Design 5 + TanStack Query 5 + Vite 5)    │
└────────────────────┬────────────────────────────┘
                     │ invoke() IPC
┌────────────────────▼────────────────────────────┐
│           Rust 后端 (31 个 Tauri 命令)            │
│  ┌──────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │commands  │ │compatibility │ │   updater    │ │
│  │  .rs     │ │    .rs       │ │    .rs       │ │
│  └────┬─────┘ └──────────────┘ └──────────────┘ │
│       │                                        │
│  ┌────▼────────────────────────────────────┐   │
│  │  rusqlite (SQLite, WAL 模式, 7 张表)     │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

详见 [`tauri_app/README.md`](tauri_app/README.md)。

---

## 方案 A · Python 版

### 适用场景

- 已有 Python 环境，想快速二次开发
- 学习 PyQt/PySide6 桌面开发
- 需要单文件 exe 分发（无安装过程）
- 不在意体积（50 MB 可接受）

### 快速开始

**环境要求**：Python 3.9+、Windows 8.1/10/11

```powershell
cd python_app
pip install -r requirements.txt
python main.py               # 运行
pyinstaller --clean 中药材销售管理系统.spec   # 打包
```

**产物位置**：`python_app/dist/中药材销售管理系统.exe`

### 技术架构

```
┌─────────────────────────────────────────────────┐
│            PySide6 6.6+ (Qt 官方维护)             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  views/ (视图层, 继承 BaseDataView)               │
│  └── 调用 Service 层                              │
├─────────────────────────────────────────────────┤
│  core/services.py    → 业务逻辑 + 缓存同步        │
│  core/repositories/  → Repository (SQLAlchemy 2) │
│  core/cache.py       → LRU 缓存 + 读写穿透        │
│  core/compatibility  → 十八反十九畏配伍禁忌       │
├─────────────────────────────────────────────────┤
│  SQLite3 (线程安全单例 + schema 自动迁移)         │
└─────────────────────────────────────────────────┘
```

详见 [`python_app/README.md`](python_app/README.md)。

---

## 两套方案如何选择？

### 我是使用者（诊所医生 / 药房 staff）

**直接下载方案 B 的 NSIS 安装包**：
1. 前往 [Gitee Releases](https://gitee.com/flyxjin/doctor/releases) 下载最新 `中药材销售管理系统_x.x.x_x64-setup.exe`
2. 双击安装（需 Windows 10/11）
3. 桌面快捷方式启动即可

> 老电脑（Windows 8.1）或不想安装？用方案 A 的便携 exe，双击即用。

### 我是开发者，想学习 / 二次开发

| 你的情况 | 推荐方案 | 理由 |
|---------|---------|------|
| 只会 C / 想学系统级编程 | **方案 B** | Rust 内存安全 + 所有权模型，从 C 过渡平滑 |
| 已会 Python / 想快速出活 | **方案 A** | Python 生态熟、迭代快、调试简单 |
| 想学现代前端 (React/TS) | **方案 B** | 完整 React + Ant Design + TanStack Query 实战 |
| 想学桌面 GUI 框架 | **方案 A** | Qt (PySide6) 是跨平台 GUI 工业标准 |
| 追求最小体积 / 最佳性能 | **方案 B** | 3 MB vs 50 MB，启动秒开 |

### 两套方案的技术栈对比

| 维度 | 方案 A (Python) | 方案 B (Tauri) |
|------|-----------------|----------------|
| 后端语言 | Python 3.9+ | Rust 1.70+ |
| 前端 / UI | PySide6 (Qt 6) | React 18 + Ant Design 5 |
| 类型系统 | 动态类型 + typing | TypeScript 严格模式 + Rust 类型系统 |
| 数据库 | SQLite3 + SQLAlchemy 2.0 ORM | rusqlite (bundled SQLite) |
| 状态管理 | 内存 LRU 缓存 | TanStack Query 5 |
| 打包工具 | PyInstaller 6.x | Tauri 2.x bundler + NSIS |
| 测试框架 | pytest + pytest-qt | Vitest + cargo test |
| 代码质量 | ruff + mypy | ESLint + tsc |
| 安装包体积 | ~50 MB（便携 exe） | ~3 MB（NSIS 安装包） |
| CI/CD | GitHub Actions | 本地构建 + Gitee Releases |

---

## 项目结构

```
doctor/
├── python_app/              # 方案 A：Python + PySide6 版本
│   ├── main.py              # 主程序入口
│   ├── core/                # 业务层（Service / Repository / Cache / Validators）
│   ├── views/               # 视图层（7 个页面）
│   ├── widgets/             # 自定义控件
│   ├── utils/               # 工具模块（版本管理 / 自动更新 / 响应式字体）
│   ├── tests/               # 单元测试（pytest）
│   ├── requirements.txt     # 运行依赖
│   ├── pyproject.toml       # ruff + mypy 配置
│   └── 中药材销售管理系统.spec  # PyInstaller 打包配置
│
├── tauri_app/               # 方案 B：Tauri + React 版本（生产首选）
│   ├── src/                 # React 前端
│   │   ├── pages/           # 9 个页面
│   │   ├── api/tauri.ts     # Tauri invoke 封装（31 个命令）
│   │   ├── hooks/           # 通用 CRUD mutation Hook
│   │   ├── components/      # 通用组件
│   │   ├── services/        # 方剂模板服务
│   │   ├── types/           # TypeScript 类型定义
│   │   └── utils/           # CSV / 格式化 / 打印工具
│   ├── src-tauri/           # Rust 后端
│   │   ├── src/             # commands / db / models / compatibility / updater
│   │   ├── migrations/      # SQL 迁移脚本（5 个）
│   │   └── tauri.conf.json  # Tauri 配置
│   ├── distrib/             # 便携版分发目录
│   ├── CHANGELOG.md         # 更新日志
│   └── README.md            # 详细文档
│
├── README.md                # 本文件
├── LICENSE                  # Apache 2.0
└── .gitee/                  # Gitee Issue / PR 模板
```

---

## 核心功能详解

### 1. 智能开方 + 配伍禁忌预警

完整保留中医 **十八反**（31 对）+ **十九畏**（10 对）配伍禁忌规则：

- **十八反·甘草反甘遂/大戟/海藻/芫花**（4 对）
- **十八反·乌头（川乌/草乌/附子）反贝母/瓜蒌/半夏/白蔹/白及**（20 对）
- **十八反·藜芦反人参/沙参/丹参/玄参/苦参/细辛/芍药**（7 对）
- **十九畏**（10 对，如硫黄畏朴硝、巴豆畏牵牛、人参畏五灵脂等）

匹配采用「包含」策略：`"生甘草"` 匹配 `"甘草"`，兼容炮制前后缀。添加冲突药材时实时弹窗预警，保存处方前最终确认。

### 2. 32 张经典方剂模板

一键导入四君子汤、六味地黄丸、桂枝汤、逍遥散等 32 张经典方，自动匹配药材库并填充剂量。

### 3. 库存事务原子化

开方扣库存、删除处方回扣库存、入库 / 出库均包裹在数据库事务中，中途失败自动回滚，确保库存与处方数据一致。

### 4. 数据安全

- **SQL 全参数化**：杜绝 SQL 注入
- **路径遍历防护**：导出文件名校验禁止 `/`、`\`、`..`、`\0`
- **金额服务端重算**：不信任前端传入的 total_amount，服务端 `sum(items.amount)`
- **CSP 策略**：限制脚本 / 样式 / 连接源（方案 B）
- **数据备份**：MD5 校验 + 一键还原

---

## 开发指南

### 运行测试

```powershell
# 方案 A (Python)
cd python_app
pip install -r requirements-dev.txt
pytest                    # 90 个单元测试
ruff check .              # lint
mypy core/                # 类型检查

# 方案 B (Tauri)
cd tauri_app
npx vitest run            # 35 个前端测试
cargo test --manifest-path src-tauri/Cargo.toml   # 46 个后端测试
npx tsc --noEmit          # 类型检查
npx eslint src            # lint
```

### 数据库位置

| 方案 | 路径 |
|------|------|
| 方案 A | `%APPDATA%\MedicineSystem\medicine_system.db` |
| 方案 B | `%APPDATA%\com.medicine.system\medicine_system.db` |

> 两套方案的数据库 schema 对齐，可互相备份还原。删除数据库文件后重启应用会自动重建表结构与种子数据。

---

## 常见问题

<details>
<summary><b>方案 B 启动白屏？</b></summary>

检查 WebView2 Runtime 是否安装（Win11 自带，Win10 需手动安装）；确认 `npm install` 已执行。
</details>

<details>
<summary><b>方案 A 双击 exe 闪退？</b></summary>

在命令行运行 `中药材销售管理系统.exe` 查看错误输出。常见原因：旧数据库 schema 不兼容（v3.3.2+ 已自动迁移）、数据库文件损坏（备份后删除重启）。
</details>

<details>
<summary><b>方案 B 安装时弹出 SmartScreen 警告？</b></summary>

因未购买代码签名证书，Windows SmartScreen 会提示「未知发布者」。点击「更多信息」→「仍要运行」即可。正式商用建议购买 OV/EV 代码签名证书。
</details>

<details>
<summary><b>数据库文件在哪？如何重置？</b></summary>

见上方「数据库位置」表。删除对应 `.db` 文件后重启应用，会自动重建表结构与种子数据。
</details>

<details>
<summary><b>两套方案的数据能互通吗？</b></summary>

能。两套方案的数据库 schema 对齐，可在方案 A 的 Settings 页备份 `.db`，在方案 B 的 Settings 页还原（反之亦然）。注意备份前先关闭另一个方案，避免数据库锁。
</details>

<details>
<summary><b>自动更新失败？</b></summary>

检查网络、确认 Gitee Release 已发布且包含 `.exe` 安装包，或手动下载覆盖安装。
</details>

---

## 版本历史

### 方案 B (Tauri)

- **v0.3.0**（2026-07-22）：库存变更历史、操作日志查询、batch_import N+1 优化、6 个 CRUD 事务原子化、WAL 模式、路径遍历防护
- **v0.2.0**（2026-07-21）：319 味药材、32 张方剂模板、真实市场价、自定义图标
- **v0.1.0**（2026-07-20）：初始版本

详见 [`tauri_app/CHANGELOG.md`](tauri_app/CHANGELOG.md)。

### 方案 A (Python)

- **v4.2.0**（2026-07-22）：UI 风格升级、N+1 查询修复、4 个数据库索引补充、测试覆盖 90 个
- **v4.0.0**（2026-07-04）：PyQt5 → PySide6、SQLAlchemy 2.0 ORM、Repository 分层架构
- **v3.3.0**（2026-06-21）：首页仪表盘、销售统计、配伍禁忌预警

详见 [`python_app/utils/version.py`](python_app/utils/version.py)。

---

## License

[MIT License](LICENSE) — Copyright (c) 2026 东方本草

两套方案统一使用 MIT 协议，允许商用、闭源衍生，仅需保留版权声明。

> 方案 A (python_app) 使用 PySide6 (LGPL v3)，已按 LGPL 合规要求提供 [第三方组件声明](python_app/THIRD_PARTY_NOTICES.md)，包含 Qt 库替换方式与源码获取地址。

---

## 致谢

- [Tauri](https://tauri.app/) — Rust 桌面应用框架
- [React](https://react.dev/) + [Ant Design](https://ant.design/) — 前端 UI
- [PySide6](https://www.qt.io/) — Qt for Python
- [SQLAlchemy](https://www.sqlalchemy.org/) — Python ORM
- [TanStack Query](https://tanstack.com/query) — React 数据获取
- [Vite](https://vitejs.dev/) — 前端构建工具
