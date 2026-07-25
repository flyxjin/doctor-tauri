# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.3.10] - 2026-07-25

### 新增

- **Dashboard 快捷操作入口** — 首页新增「开处方 / 新增药材 / 库存管理 / 批量导入」四个大尺寸按钮，提升常用操作直达效率
- **Dashboard 最近处方可跳转** — 最近处方表格支持双击行跳转到历史页并自动打开对应处方详情；表格标题栏新增「查看全部」入口
- **Dashboard 低库存「去入库」** — 低库存预警表格每行新增「去入库」按钮，一键跳转到库存管理页
- **药材详情 Drawer** — 药材管理页新增只读详情 Drawer（操作列「详情」按钮或双击表格行打开），展示完整药材信息（性味/归经/功效/主治/用量/禁忌等），避免必须打开编辑 Modal 才能查看
- **备份删除功能** — 后端新增 `delete_backup` 命令（含安全检查：禁止删除当前数据库、仅允许操作 backups 目录），前端 Settings 备份列表新增「删除」按钮，支持清理过期备份
- **库存导出 CSV** — 库存管理页新增「导出 CSV」按钮，导出当前筛选结果（含药材/分类/批次/效期/库存量/单价/批次价值等字段，带 BOM 兼容 Excel）

### 优化

- **Popconfirm 危险操作样式统一** — MedicineList、Patients、Settings（还原/删除备份）的确认对话框统一添加 `okButtonProps={{ danger: true }}`，红色按钮明确提示危险操作
- **Dashboard 表格标题徽章** — 低库存预警表格标题栏显示预警数量 Tag，一目了然
- **History 路由状态消费** — History 页支持接收 `location.state.focusId`，从 Dashboard 跳转后自动定位并打开处方详情，消费后清除 state 避免返回重复触发

### 测试

- 前端：35 个测试（不变），TypeScript 0 错误，ESLint 0 错误
- 后端：62 个测试（不变，新增 delete_backup 命令未单独写测试，因依赖文件系统与 State 不易单测）

---

## [0.3.9] - 2026-07-25

### 修复

- **处方页清空按钮不重置开方日期与 lastCreatedId** — 清空操作仅重置表单与药材列表，开方日期保留旧值、`lastCreatedId` 仍指向上一张已保存处方，可能导致用户误打印。改为同步重置 `createdDate` 为当前时间、`lastCreatedId` 为 null
- **处方页开方日期清空时静默保留旧值** — `DatePicker` 的 `onChange` 使用 `v && setCreatedDate(v)`，用户清空日期后状态不更新，仍提交旧时间。改为 `setCreatedDate(v ?? dayjs())`，清空时回退到当前时间
- **处方复制时未重置 lastCreatedId** — 从历史页复制处方到处方页后，`lastCreatedId` 仍指向原方，可能误导用户打印错处方。`processCopyData` 中显式调用 `setLastCreatedId(null)`
- **处方复制静默覆盖用户工作** — 从历史页复制到处方页时，若当前已有未保存内容（药材或患者姓名），直接覆盖造成数据丢失。新增 `modal.confirm` 确认对话框，用户可选「覆盖」或「取消」
- **处方复制后保存被库存预校验误判** — 复制处方后首次点保存时，`inventory` 可能尚未完成加载，`inventoryMap` 为空导致所有药材被误报库存不足。`handleSubmit` 中检测到 `inventory` 未加载时通过 `queryClient.fetchQuery` 预加载，并基于返回值构建临时 `invMap` 进行校验
- **清空按钮误操作风险** — 「清空」按钮无二次确认，误点会丢失全部输入。改为 `Popconfirm` 二次确认，并在无内容时禁用

### 优化

- **侧边栏支持折叠** — `MainLayout` 的 `Sider` 新增 `collapsible` 折叠能力，顶栏左侧新增折叠按钮（`MenuFoldOutlined`/`MenuUnfoldOutlined`），折叠态宽度 64px、展开 208px，节省横向空间
- **侧边栏菜单分组** — 9 项扁平菜单按业务重组为「首页概览 / 业务（开处方·客户管理·处方历史）/ 数据（药材管理·库存管理·销售统计·批量导入）/ 系统设置」四段，默认展开业务与数据分组，选中项所在分组自动展开
- **Statistics 快捷范围选中态** — 「近 7/30/90 天」按钮原先无选中态，用户无法识别当前范围。改为根据 `quickSelected` 状态切换 `type="primary"`，RangePicker 自定义选择后若匹配快捷范围则同步高亮，否则清除高亮
- **History 表格处方号列固定** — 表格横向滚动时处方号列随之滚走，对照困难。为「处方号」列添加 `fixed: 'left'`，与右侧固定的「操作」列形成两侧固定
- **History 删除确认增强** — `Popconfirm` 增加 `description`（"将回扣库存，此操作不可撤销"）与 `okButtonProps={{ danger: true }}`，明确告知用户删除影响

### 测试

- 前端：35 个测试（不变），TypeScript 0 错误，ESLint 0 错误
- 后端：61 个测试（不变，本次纯前端改动）

---

## [0.3.8] - 2026-07-23

### 新增

- **处方复制/再来一剂** — 处方历史页（History）列表行与详情 Drawer 均新增「复制到处方」按钮，点击后把处方头（患者姓名/年龄/性别/诊断/开方人）与药材明细（药名/数量/单位/单价）写入 `sessionStorage`，跳转到处方页自动预填，开方日期重置为当前时间。复诊高频场景一键带入原方，医生可调整剂量或换药后保存为新处方

### 设计要点

- **跨页面传输用 sessionStorage** — 避免 URL 序列化大量明细项，刷新页面不重复预填（读取后立即清除 key）
- **沿用原方价格** — 复诊常沿用原价，医生可在处方页手动调整单价，符合实际开方习惯
- **不复制 id/prescription_id/batch_id** — 新处方为新行，避免与原方数据混淆
- **导出 `PRESCRIPTION_COPY_KEY` 常量** — History 页导出 key 常量供 Prescription 页导入，避免魔法字符串

### 测试

- 前端：35 个测试（不变），TypeScript 0 错误，ESLint 0 错误
- 后端：61 个测试（不变，本次纯前端改动）

---

## [0.3.7] - 2026-07-23

### 修复

- **严重 Bug：跨批次处方删除回扣错误** — 0.3.5 引入的 FEFO 跨批次扣减存在数据一致性缺陷：`prescription_items.batch_id` 仅记录首个扣减批次，删除处方时整量回扣到该批次，导致后续批次库存永久丢失。新增 `009_prescription_item_batches.sql` 迁移，建立处方明细与批次扣减的关联表，`create_prescription` 写入每批次扣减明细，`delete_prescription` 按明细逐批次精确回扣，老数据（无明细记录）回退为整量回扣到「初始库存」
- **严重 Bug：处方页库存校验取错行** — `Prescription.tsx` 的 `inventoryMap` 直接以 `medicine_id` 为 key 存单行 `Inventory`，一药多批后只保留最后一条批次，导致库存校验与价格取值错误。改为按 `medicine_id` 聚合 `totalQty`，价格/单位取首批次
- **新批次 min_stock 丢失** — `update_stock` 新建批次行时 `min_stock` 硬编码为 0，导致同药材新批次的低库存预警失效。改为从该药材已有任意批次复制 `min_stock`
- **退库历史金额错误** — `delete_prescription` 写入 `inventory_history` 的 `price`/`total_amount` 使用处方明细均价，与原扣减批次价格不一致。改为使用关联表记录的原批次扣减价格
- **批量导入批次号冲突** — `batch_import_medicines` 同一批次时间戳内多行导入会生成相同 `batch_no`，违反联合唯一约束。改为在批次号后追加 `row_no` 区分
- **`distrib/install.bat` 语法错误** — 第 37 行注册卸载信息时 `DisplayVersion` 后缺失分号 `;`，导致 PowerShell 解析失败，卸载入口注册不完整
- **`Prescription.tsx` 非空断言** — `m.id!` 强制断言绕过类型检查，存在运行时风险。改用局部变量 `mid` 配合 early return 实现类型收窄

### 优化

- **处方提交前库存预校验** — `handleSubmit` 新增跨批次总库存检查，库存不足时列出每味药的「需求量 vs 库存量」并阻止提交，避免后端报错回滚
- **`update_stock` 死代码清理** — 移除 `remaining > 0.001` 的冗余校验（`select_batches_fefo` 内部已校验库存充足）
- **`templateService.ts` 类型安全** — 用 `TemplatesFile` 接口替代 `as any`，消除 ESLint `no-explicit-any` 警告

### 测试

- 后端：60 → 61 个测试（+1 个 `test_cross_batch_prescription_delete_restores_each_batch`：验证 B1(30)+B2(50) 处方扣 40 后删除，B1 恢复 30、B2 恢复 50，非整量回扣到首批次）
- `cargo test --lib` 全部通过
- 前端：35 个测试（不变），TypeScript 0 错误，ESLint 0 错误

---

## [0.3.6] - 2026-07-23

### 新增

- **桌面图标重新设计：「悬壶本草」药葫芦** — 用图形替代旧版「印章+本字」，解决 16/32px 小尺寸下文字模糊问题。深绿渐变圆角背景 + 中央白色药葫芦（中医药「悬壶济世」经典符号）+ 束腰处翠绿本草叶 + 顶部朱砂红葫芦口 + 底部金色弧线。4x 超采样 + LANCZOS 缩小抗锯齿，ICO 嵌入 7 个分辨率（16/24/32/48/64/128/256，38.2KB）
- **`generate_icon.py` 重写** — 简化葫芦几何（两个白色椭圆 + 束腰梯形同色重叠自然融合），删除根目录旧版研钵脚本

### 优化

- **图标对比度提升** — 深绿背景(#1E4530→#122A1E) + 白色葫芦主体(#FDFAF5) + 左侧高光模糊层，各尺寸下轮廓清晰可辨

---

## [0.3.5] - 2026-07-23

### 新增

- **批次 + 效期管理**：库存表从「一药一行」改为「一批次一行」，支持同药材多批次、生产日期与效期录入。新增 `008_batch_expiry.sql` 迁移，重建 inventory 表（移除 medicine_id UNIQUE 约束，新增 batch_no/production_date/expiry_date 字段 + 联合唯一索引），存量数据自动转为 batch_no='初始库存'、效期为 NULL
- **FEFO 近效期优先出库**：出库时自动按「近效期 → 无效期 → 入库时间」顺序跨批次扣减，新增 `select_batches_fefo` 辅助函数遍历累加直至满足需求量，库存不足时返回错误
- **效期预警查询**：新增 `list_expiring_batches` 后端命令，查询指定天数内到期且库存 > 0 的批次，按效期升序返回
- **库存页面效期预警横幅**：Inventory 页顶部展示近 30 天到期/已过期批次，红色标签标已过期、橙色标签标近效期，前 5 项预览
- **批次筛选模式**：库存表新增「近效期」筛选标签，与原有「全部/低库存/零库存」并列
- **入库批次录入**：入库 Modal 新增批次号、生产日期、效期三个输入项（出库时隐藏，显示 FEFO 提示）；批次号留空自动按时间戳生成，同批次号入库自动合并数量

### 优化

- **处方扣库存改为 FEFO 跨批次**：`create_prescription` 从单行 UPDATE 改为调用 `select_batches_fefo` 逐批次扣减，`prescription_items` 记录 `batch_id` 用于精确回扣
- **删除处方精确回扣**：`delete_prescription` 优先回扣到原 `batch_id`，批次不存在则回扣到该药材的「初始库存」或第一个批次
- **看板低库存统计聚合**：`get_dashboard_data` 的低库存判断从单行 `quantity <= min_stock` 改为按药材 `SUM(quantity) <= MIN(min_stock)` 聚合，避免一药多批时误报
- **批量导入新批次语义**：`batch_import_medicines` 已有药材不再覆盖库存，改为新建批次行（batch_no='导入批次-{时间戳}'），保留历史批次
- **库存列表按批次行返回**：`list_inventory` ORDER BY 改为 `medicine_id ASC, batch_no ASC`，前端表格新增批次号、效期列
- **库存统计按药材去重**：前端 Inventory 页「在库品种」「低库存」「零库存」统计改为按 medicine_id 聚合，不因多批次重复计数
- **出库预校验改为总库存**：前端出库前检查该药材跨批次总库存，而非单批次余量

### 测试

- 后端：52 → 60 个测试（+8 个批次专项测试：FEFO 顺序、无效期排后、库存不足报错、同批合并、新批新建、跨批扣减、效期预警查询、低库存聚合）
- 修复 `get_quantity` 测试辅助函数为 `SUM(quantity)` 聚合，适配一药多批
- `cargo test --lib` 全部通过
- 前端：35 个测试（不变），TypeScript 0 错误，ESLint 0 错误

---

## [0.3.4] - 2026-07-23

### 新增

- **药材库扩充至 400 味**：新增 `007_expand_herbs.sql` 迁移，在原 319 味（300 种子 + 19 补充）基础上补充 81 味常用中药材，覆盖清热药(15)、泻下药(1)、祛风湿药(5)、利水渗湿药(3)、温里药(2)、理气药(3)、消食药(2)、驱虫药(4)、止血药(3)、活血化瘀药(5)、化痰止咳平喘药(3)、安神药(3)、平肝息风药(3)、开窍药(2)、补虚药(5)、收涩药(5)、攻毒杀虫止痒药(6)、拔毒化腐生肌药(4)、其他常用(7) 共 19 个分类，数据来源《中药学》教材 + 《中国药典》
- **扩充药材库存初始化**：每味新增药材自动初始化库存 quantity=1000g、min_stock=100g、价格区间 0.05~80.00 元/g（与 `006_fix_price_unit.sql` 修复后元/g 基准一致）

### 测试

- 后端：52 个测试（不变，更新 `test_seed_data_inserted` 断言 319 → 400）
- `cargo test --lib` 全部通过

---

## [0.3.3] - 2026-07-23

### 新增

- **桌面图标重新设计**：「东方本草」篆刻印章风格 — 圆角方形深绿渐变背景 + 中央朱砂红印章（白色「本」字）+ 印章两侧装饰性叶片 + 底部金色弧线。生成脚本 `generate_icon.py` 直接用 Pillow 绘制位图，输出多分辨率 PNG（32/128/128@2x）、ICO（7 个分辨率嵌入，24.47KB）、SVG 矢量源
- **`formatError` 统一错误提示工具**：将 Rust 后端原始错误字符串映射为中文友好提示（库存不足、唯一约束、外键约束、网络异常等 6 种已知模式 + 未知错误兜底）
- **`Inventory` 出库预校验**：前端先检查库存余量，避免等后端拒绝；提示语带上当前库存与单位
- **`Inventory` Modal 标题响应式**：用 `Form.useWatch('is_in')` 替代 `getFieldValue`，操作类型切换时 Modal 标题实时更新

### 优化

- **React Query `placeholderData`**：全局配置 `(prev) => prev`，搜索关键字切换时保留上一次数据，消除表格闪烁加载态
- **`Settings` 还原后强制刷新**：`window.location.reload()` 替代 `invalidateQueries`，避免组件持有旧引用导致新旧数据混合状态
- **Vite `manualChunks` 新增 dayjs 分包**：`date-vendor` 独立分包，长期稳定无需随业务 chunk 变化失效缓存
- **antd 5.25+ API 对齐**：`destroyOnClose` → `destroyOnHidden`（MedicineList、Patients）
- **App.tsx theme 提升模块顶层**：补充文档注释，说明主题色对应业务语义
- **死代码清理**：删除前端从未调用的 `getMedicine` / `getPatient` 函数与 `DataVersion` interface

---

## [0.3.2] - 2026-07-23

### 新增

- **快速更新（无感更新）**：应用启动后延迟 1.5s 后台静默检查 Gitee Release，发现新版本则流式下载到 `%APPDATA%/com.medicine.system/downloads/`，下载完成后弹窗提示"立即更新"。用户确认后调用 NSIS 静默安装（`/S` 参数）+ 应用自动退出（`app_handle.exit(0)`），安装程序接管覆盖安装
- **`check_and_download_silently` 后端命令**：合并"检查 + 下载"为单一命令，内部完成版本比较，仅当 `remote > current` 时下载；下载失败仍返回 `has_update=true` 让前端可降级到 Settings 页手动重试
- **`install_update` 静默安装参数**：新增 `silent: Option<bool>` 参数，`true` 时传 `/S` 给 NSIS 安装程序并启动 500ms 定时器后调用 `app.exit(0)`
- **版本比较工具函数 + 6 个单元测试**：`is_newer_version` / `version_segments` 处理 `v` 前缀与非数字段
- **`SilentUpdateResult` 类型**：Rust + TypeScript 双端对齐

### 优化

- **updater.rs 重构**：抽取 `build_download_path` / `download_to_path` 公共函数，消除 `download_update` 与 `check_and_download_silently` 之间的代码重复；`download_to_path` 接受 `Option<&Channel>` 支持有进度/无进度两种模式
- **MainLayout 启动检查**：通过 `useEffect` + `setTimeout(1500)` 延迟触发，避免与首屏数据请求争抢网络；失败静默不打扰用户
- **Settings 页保留手动更新路径**：手动点击"启动安装程序"显式传 `silent=false`，仍走 NSIS 安装向导 UI

### 修复

- **网络异常不影响启动**：`check_and_download_silently` 在 Gitee API 请求失败时直接 reject，前端 `.catch()` 静默吞掉，不弹任何错误提示

### 测试

- 后端：46 → 52 个测试（+6 个版本比较单元测试）
- 前端：35 个测试（不变）
- TypeScript 严格模式 0 错误
- ESLint 0 错误

---

## [0.3.1] - 2026-07-22

### 修复

- **价格单位错误**：`005_redesign_prices.sql` 将 `inventory.price` 设为"元/100g"语义，但系统计算公式 `quantity × price` 按"元/g"计算，导致所有金额放大 100 倍。新增 `006_fix_price_unit.sql` 迁移，将 `inventory` / `prescription_items` / `inventory_history` / `prescriptions` 四张表的 `price` / `amount` / `total_amount` 字段统一除以 100 转为"元/g"，python_app 种子数据同步修正

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
