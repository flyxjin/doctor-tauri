# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.3.0] - 2026-07-22

### 新增

- **库存变更历史查询**：后端 `list_inventory_history` 命令支持按药材、类型、日期范围筛选；前端 Inventory 页新增「历史」按钮 + Drawer（720px）展示变更明细，类型颜色标识（入库=绿、出库=橙、退库=蓝）
- **操作日志查询**：后端 `list_operation_logs` 命令支持按操作类型、目标类型、日期范围筛选；前端 Settings 页新增「操作日志」卡片（最近 100 条），按类型筛选（CREATE / UPDATE / DELETE / STOCK / IMPORT）
- **处方后端日期筛选**：`list_prescriptions` 签名增加 `start_date` / `end_date` 参数，前端 History 页改用后端 SQL `date(created_at) BETWEEN` 过滤，消除前端全量加载后过滤的性能问题
- **6 个后端单元测试**：库存历史筛选（2）、操作日志筛选（2）、batch_import HashMap 预查模式（2）

### 修复

- **处方 created_at 丢失**：`create_prescription` 的 INSERT 增加条件性 created_at 字段，用户选择的开方日期不再被后端静默丢弃
- **时区不一致**：`update_patient` 的 `datetime('now','localtime')` 改为 `CURRENT_TIMESTAMP`，与其它表时间戳一致
- **路径遍历漏洞**：`save_text_to_downloads` 的 filename 校验禁止 `/`、`\`、`..`、`\0`，防止写入任意路径
- **删除药材破坏处方审计**：`delete_medicine` 先 `COUNT(*) FROM prescription_items WHERE medicine_id=?`，被引用时拒绝删除并提示
- **前端金额篡改**：`create_prescription` 的 `total_amount` 由服务端 `items.iter().map(|i| i.amount).sum()` 重新计算，不信任前端传入

### 优化

- **SQLite 性能**：启用 WAL 模式 + `synchronous=NORMAL` + `busy_timeout=5000` + `cache_size=-8000` + `foreign_keys=ON` 五项 PRAGMA
- **batch_import N+1 消除**：循环前 `SELECT id, name FROM medicines WHERE name IN (...)` 一次性预查所有已存在药材到 HashMap，循环内 O(1) 查找替代 per-record SQL 查询；新建药材后更新 HashMap，同批次重复名称走 UPDATE
- **CRUD 事务原子化**：`create_medicine` / `update_medicine` / `delete_medicine` / `create_patient` / `update_patient` / `delete_patient` 的数据操作 + `log_operation` 包裹在 `unchecked_transaction()` 中，防止中途失败导致数据与审计日志不一致

### 测试

- 后端：40 → 46 个测试（+6）
- 前端：35 个测试（不变）
- TypeScript 严格模式 0 错误
- ESLint 0 错误

---

## [0.2.0] - 2026-07-21

### 新增

- **319 味中药材内置库**：含别名、分类、药性、归经、功效、主治、用法、用量、禁忌、备注
- **32 张经典方剂模板**：四君子汤、六味地黄丸、桂枝汤、逍遥散等，一键导入自动匹配药材
- **真实市场参考价**：基于实际市场调研的价格数据
- **自定义应用图标**：中药材主题 SVG 图标，多分辨率（32/128/256px）
- **患者档案管理**：患者 CRUD + 历史处方关联 + 消费统计
- **批量导入**：CSV 解析 + 预览 + UPSERT + 实时进度
- **数据备份与还原**：MD5 校验 + 备份列表 + 一键还原
- **Gitee 自动更新**：检查更新 + 流式下载 + 进度条 + 启动安装

### 优化

- **前端分包**：antd-vendor / react-vendor / query-vendor / icons-vendor 四 chunk 分离，@ant-design/icons 独立为 16KB chunk
- **路由懒加载**：9 个页面均使用 `React.lazy` + `Suspense`

---

## [0.1.0] - 2026-07-20

### 首次发布

- 基础架构：Tauri 2.x + React 18 + TypeScript + Rust + SQLite
- 药材管理 CRUD
- 开处方 + 十八反十九畏配伍禁忌预警
- 库存管理 + 入库 / 出库
- 处方历史 + 打印
- 销售统计（5 种时间范围 + TOP10 + 趋势）
- 首页看板
