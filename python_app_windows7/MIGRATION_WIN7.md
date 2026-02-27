# Windows 7 迁移文档

## 项目概述

本文档记录了将中药材销售管理系统从当前版本迁移到Windows 7兼容版本的所有变更。

- **原版本目录**: `python_app/`
- **Windows 7版本目录**: `python_app_windows7/`
- **迁移日期**: 2026-02-27
- **目标平台**: Windows 7 SP1 (32位/64位)

---

## 一、依赖库变更

### 1.1 Python版本

| 项目 | 原版本 | Windows 7版本 | 说明 |
|------|--------|---------------|------|
| Python | 3.9+ | **3.8.10** | Python 3.8.10是最后一个官方支持Windows 7的版本 |

### 1.2 第三方库变更

| 依赖库 | 原版本 | Windows 7版本 | 变更原因 |
|--------|--------|---------------|----------|
| PyQt5 | 5.15.10 | **5.15.2** | 5.15.2是最后一个完全支持Windows 7的版本 |
| PyQt5-Qt5 | 5.15.2 | 5.15.2 | 无变更，已兼容 |
| PyQt5-sip | 12.13.0 | **12.12.0** | 与PyQt5 5.15.2更好兼容 |
| reportlab | 4.0.7 | **4.0.4** | 稳定性考虑 |
| Pillow | 10.1.0 | **9.5.0** | Pillow 10.x对Windows 7支持有限 |
| pyinstaller | 6.3.0 | **5.13.2** | PyInstaller 6.x存在Windows 7兼容问题 |

### 1.3 新增文件

```
python_app_windows7/
├── requirements_win7.txt      # Windows 7专用依赖文件
├── medicine_system_win7.spec  # PyInstaller打包配置
├── version_info.txt           # Windows版本信息
├── build_win7.bat             # 打包构建脚本
├── system_check.bat           # 系统兼容性检测工具
└── core/
    └── win7_compat.py         # Windows 7兼容性适配模块 (新增)
```

---

## 二、代码变更详情（2026-02-27 更新）

### 2.0 新增模块: `utils/excel_template.py`

**功能**: Excel模板生成器和数据验证器

**主要功能**:
- 生成标准化的Excel导入模板 (`ExcelTemplateGenerator`)
- 数据验证功能 (`DataValidator`)
- 支持必填字段验证
- 支持数据类型验证（数值、文本）
- 支持药性字段验证（寒/热/温/凉/平）

### 2.1 修改文件: `views/batch_import_view.py`

**变更内容**:

1. **增强数据验证**
   - 导入 `ExcelTemplateGenerator` 和 `DataValidator`
   - 导入前进行数据验证
   - 显示验证错误信息

2. **改进模板下载**
   - 支持Excel和CSV两种格式
   - Excel模板包含字段说明sheet
   - 必填字段用红色表头标识

3. **改进错误提示**
   - 验证错误显示在日志区域
   - 提供继续导入有效数据的选项

### 2.2 修改文件: `views/history_view.py`

**变更内容**: 修复删除按钮布局对齐问题

1. **表格行高设置**
   ```python
   self.list_table.verticalHeader().setDefaultSectionSize(40)
   ```

2. **列宽固定设置**
   ```python
   self.list_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
   self.list_table.setColumnWidth(6, 80)
   ```

3. **删除按钮样式优化**
   - 添加 `min-width: 50px`
   - 添加悬停和按下状态样式
   - 添加鼠标指针样式

### 2.3 修改文件: `views/prescription_view.py`

**变更内容**: 修复删除按钮布局对齐问题

1. **表格行高设置**
   ```python
   self.prescription_table.verticalHeader().setDefaultSectionSize(40)
   ```

2. **列宽固定设置**
   ```python
   self.prescription_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
   self.prescription_table.setColumnWidth(4, 70)
   ```

3. **单元格文本对齐**
   ```python
   item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
   ```

### 2.4 更新依赖: `requirements_win7.txt`

**新增依赖**:
```
openpyxl==3.0.10  # Excel文件支持
```

### 2.5 更新打包配置: `medicine_system_win7.spec`

**新增隐藏导入**:
```python
'openpyxl',
'openpyxl.styles',
'openpyxl.utils',
'utils.excel_template',
```

### 2.1 新增模块: `core/win7_compat.py`

**功能**: Windows 7兼容性适配器

**主要功能**:
- 系统版本检测 (`is_windows7()`)
- DPI感知设置 (`setup_dpi_awareness()`)
- 高DPI缩放设置 (`setup_high_dpi_scaling()`)
- TLS 1.2支持 (`setup_tls_support()`, `create_ssl_context()`)
- 应用数据目录管理 (`get_app_data_dir()`)
- 系统要求检测 (`check_system_requirements()`)

**代码片段**:
```python
class Windows7Compat:
    @classmethod
    def initialize(cls) -> bool:
        cls.setup_dpi_awareness()
        cls.setup_high_dpi_scaling()
        cls.setup_tls_support()
        return cls.is_windows7()
```

### 2.2 修改文件: `main.py`

**变更内容**:

1. **导入Windows 7兼容模块**
   ```python
   from core.win7_compat import Windows7Compat, initialize_win7_compat
   
   is_win7 = initialize_win7_compat()
   if is_win7:
       print("[Windows 7 兼容模式] 已启用")
   ```

2. **版本号标识**
   ```python
   WIN7_VERSION_SUFFIX = "-Win7"
   CURRENT_VERSION_WIN7 = CURRENT_VERSION + WIN7_VERSION_SUFFIX
   ```

3. **窗口标题变更**
   ```python
   self.setWindowTitle('中药材销售管理系统 (Windows 7版)')
   ```

4. **日志记录增强**
   ```python
   self.logger.info("应用程序启动 (Windows 7 兼容版)")
   if Windows7Compat.is_windows7():
       self.logger.info("检测到 Windows 7 系统，已启用兼容模式")
   ```

### 2.3 修改文件: `utils/updater.py`

**变更内容**:

1. **新增SSL上下文创建函数**
   ```python
   def create_win7_ssl_context() -> ssl.SSLContext:
       """创建Windows 7兼容的SSL上下文"""
       ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
       ctx.minimum_version = ssl.TLSVersion.TLSv1_2
       ctx.check_hostname = False
       ctx.verify_mode = ssl.CERT_NONE
       return ctx
   ```

2. **网络请求超时调整**
   - Windows 7下网络请求超时从10秒增加到15-20秒
   - 下载超时从30秒增加到60秒

3. **User-Agent添加**
   ```python
   request.add_header('User-Agent', 'MedicineSystem-Updater/1.0')
   ```

### 2.4 修改文件: `core/__init__.py`

**变更内容**:
- 新增导出Windows 7兼容模块
  ```python
  from .win7_compat import Windows7Compat, initialize_win7_compat, get_win7_compat
  ```

---

## 三、打包配置变更

### 3.1 PyInstaller Spec文件

**文件**: `medicine_system_win7.spec`

**关键配置**:
```python
exe = EXE(
    ...
    name='中药材销售管理系统_Win7',
    console=False,
    uac_admin=False,  # 不需要管理员权限
    version='version_info.txt',
)
```

### 3.2 版本信息文件

**文件**: `version_info.txt`

**内容**:
- 产品名称: 中药材销售管理系统
- 文件描述: 中药材销售管理系统 - Windows 7兼容版
- 版本号: 2.3.0.0
- 特殊构建: Windows 7 Compatible Version

---

## 四、构建与部署

### 4.1 构建步骤

1. **环境准备**
   ```bash
   # 安装Python 3.8.10
   # 下载地址: https://www.python.org/downloads/release/python-3810/
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements_win7.txt
   ```

3. **执行打包**
   ```bash
   # 方式1: 使用批处理脚本
   build_win7.bat
   
   # 方式2: 直接使用PyInstaller
   pyinstaller --clean --noconfirm medicine_system_win7.spec
   ```

### 4.2 输出目录结构

```
dist/
└── 中药材销售管理系统_Win7/
    ├── 中药材销售管理系统_Win7.exe
    ├── medicines_data_300.py
    ├── medicine_system.db
    └── [其他依赖文件]
```

---

## 五、系统要求

### 5.1 最低要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 7 SP1 |
| 处理器 | 1 GHz 或更快 |
| 内存 | 512 MB RAM |
| 硬盘 | 100 MB 可用空间 |
| 显示器 | 800 x 600 分辨率 |

### 5.2 推荐配置

| 项目 | 推荐 |
|------|------|
| 操作系统 | Windows 7 SP1 (64位) |
| 处理器 | 2 GHz 双核 |
| 内存 | 2 GB RAM |
| 硬盘 | 500 MB 可用空间 |
| 显示器 | 1366 x 768 分辨率 |

### 5.3 可选更新

- **KB3063858**: TLS 1.2支持更新
- **KB3154518**: TLS 1.2注册表配置

---

## 六、已知问题与解决方案

### 6.1 网络连接问题

**问题**: Windows 7默认不支持TLS 1.2，可能导致更新检查失败

**解决方案**:
1. 安装KB3063858更新
2. 代码中已禁用SSL证书验证
3. 增加了网络请求超时时间

### 6.2 高DPI显示问题

**问题**: Windows 7对高DPI支持有限

**解决方案**:
1. 添加DPI感知设置
2. 使用Qt的高DPI缩放属性

### 6.3 数据目录权限

**问题**: 打包后程序可能无写入权限

**解决方案**:
- 数据存储在 `%APPDATA%\MedicineSystem` 目录
- 该目录所有用户都有写入权限

---

## 七、测试清单

### 7.1 功能测试

- [ ] 应用程序启动
- [ ] 药材管理功能
- [ ] 处方开具功能
- [ ] 库存管理功能
- [ ] 处方历史查询
- [ ] 批量导入功能
- [ ] 数据导出功能
- [ ] 数据备份功能
- [ ] 更新检查功能

### 7.2 兼容性测试

- [ ] Windows 7 SP1 32位
- [ ] Windows 7 SP1 64位
- [ ] Windows 10 (向后兼容)
- [ ] 不同DPI设置
- [ ] 不同屏幕分辨率

### 7.3 性能测试

- [ ] 启动时间 (< 5秒)
- [ ] 内存占用 (< 200MB)
- [ ] 数据库操作响应时间

---

## 八、变更文件清单

| 文件路径 | 变更类型 | 说明 |
|----------|----------|------|
| `requirements_win7.txt` | 新增 | Windows 7专用依赖 |
| `core/win7_compat.py` | 新增 | 兼容性适配模块 |
| `main.py` | 修改 | 添加兼容代码 |
| `utils/updater.py` | 修改 | TLS兼容处理 |
| `utils/excel_template.py` | 新增 | Excel模板生成器和数据验证器 |
| `views/batch_import_view.py` | 修改 | 增强数据验证和模板下载 |
| `views/history_view.py` | 修改 | 修复删除按钮布局对齐 |
| `views/prescription_view.py` | 修改 | 修复删除按钮布局对齐 |
| `core/__init__.py` | 修改 | 导出新模块 |
| `medicine_system_win7.spec` | 修改 | 打包配置（添加openpyxl） |
| `version_info.txt` | 新增 | 版本信息 |
| `build_win7.bat` | 新增 | 构建脚本 |
| `system_check.bat` | 新增 | 系统检测工具 |
| `MIGRATION_WIN7.md` | 新增 | 本文档 |

---

## 九、回滚方案

如需回滚到原版本:

1. 使用 `python_app/` 目录中的原版本代码
2. 使用 `requirements.txt` 安装原依赖
3. 数据库文件兼容，无需迁移

---

## 十、联系与支持

如有问题，请检查:
1. 系统是否满足最低要求
2. 是否安装了必要的Windows更新
3. 运行 `system_check.bat` 进行诊断

---

*文档版本: 1.0*
*最后更新: 2026-02-27*
