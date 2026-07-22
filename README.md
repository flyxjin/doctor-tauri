# 中药材销售管理系统（Tauri 2.x 重写版）

基于原 PySide6 项目（`d:\learn\trae\python_app`）重写的桌面端中药材销售管理系统，采用 Tauri 2.x + React + TypeScript 技术栈，数据库与原项目 SQLite schema 完全兼容，可共享数据。

## 技术栈

- **后端**：Rust + Tauri 2.x + rusqlite（SQLite，bundled）
- **前端**：React 18 + TypeScript（严格模式）
- **UI**：Ant Design 5.x（中文 locale）
- **状态**：TanStack Query（服务端状态）
- **路由**：React Router DOM v6
- **构建**：Vite

## 功能模块

1. **首页概览** - 统计卡片 + 低库存预警 + 最近处方
2. **药材管理** - 药材 CRUD，搜索、分类筛选
3. **开处方** - 药材检索 + 处方编辑 + 十八反十九畏配伍禁忌预警
4. **库存管理** - 库存列表 + 入库/出库
5. **处方历史** - 处方查询与详情
6. **销售统计** - 时间范围统计 + 热销 TOP10 + 趋势

## 数据库

- 文件位置：用户数据目录下的 `medicine_system.db`（通过 `app_data_dir()` 解析）
- 表结构：`medicines`、`inventory`、`prescriptions`、`prescription_items`、`inventory_history`、`operation_logs`、`data_version`
- 迁移脚本：`src-tauri/migrations/001_init.sql`
- 与原 Python 项目 schema 完全一致，可直接共享同一数据库文件

## 配伍禁忌

完整保留中医十八反、十九畏配伍禁忌规则（`src-tauri/src/compatibility.rs`），匹配采用"包含"策略以兼容炮制前后缀（如"生甘草"匹配"甘草"）。

## 运行方式

```bash
# 安装前端依赖
npm install

# 开发模式（同时启动 Vite 与 Tauri）
npm run tauri:dev

# 生产构建
npm run tauri:build
```

> 首次构建需下载 Rust 依赖，可能较慢；`rusqlite` 使用 `bundled` feature 会自动编译 SQLite，无需系统安装。

## 目录结构

```
tauri_app/
├── src/                    # React 前端
│   ├── api/                # Tauri invoke 封装
│   ├── components/         # 通用组件
│   ├── layouts/            # 布局
│   ├── pages/              # 页面
│   ├── styles/             # 全局样式
│   └── types/              # 类型定义
├── src-tauri/              # Rust 后端
│   ├── migrations/         # SQL 迁移
│   └── src/
│       ├── commands.rs     # Tauri commands
│       ├── compatibility.rs# 配伍禁忌
│       ├── db.rs           # 数据库连接管理
│       ├── models.rs       # 数据模型
│       └── lib.rs          # 注册 commands
└── package.json
```
