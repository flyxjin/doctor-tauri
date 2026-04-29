# 中药材销售管理系统 (Python桌面版)

## 系统简介

本系统是一款基于Python + PyQt5开发的原生桌面应用程序，面向药店医生使用的中药材销售管理系统。无需浏览器，双击即可运行。

## 功能模块

1. **中药材管理** - 药材信息的录入、查询、编辑、删除
2. **开具处方** - 患者信息录入、药材选择、自动计算金额
3. **库存管理** - 入库、出库、库存预警、库存历史
4. **处方历史** - 历史处方查询、详情查看、删除

## 系统要求

### 标准版本（推荐）

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 8.1 / 10 / 11 |
| **处理器** | 1 GHz 或更快 |
| **内存** | 512 MB RAM |
| **硬盘** | 100 MB 可用空间 |
| **运行时** | 无需安装（已打包为 exe） |

### Windows 7 兼容版本

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 7 SP1 或更高 |
| **处理器** | 1 GHz 或更快 |
| **内存** | 512 MB RAM |
| **硬盘** | 100 MB 可用空间 |
| **备注** | 需要使用 Python 3.9.x 重新打包 |

> ⚠️ **注意**：Windows 7 已于 2020 年停止微软官方支持，建议升级到 Windows 10/11

## 安装步骤

### 方法一：直接运行打包版本（推荐）

1. 双击 `中药材销售管理系统.exe` 即可运行
2. 无需安装 Python 或其他依赖

### 方法二：从源码运行（需要Python环境）

1. **安装Python**
   - 下载地址: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"
   - 推荐版本：Python 3.9+（Windows 8.1/10/11）

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行系统**
   - 双击 `启动系统.bat` 文件
   - 或在命令行运行: `python main.py`

### 方法三：自行打包

**标准版本（Windows 8.1/10/11）：**
```bash
pip install -r requirements.txt
pyinstaller --clean 中药材销售管理系统.spec
```

**Windows 7 兼容版本：**
```bash
# 需要使用 Python 3.9.x
pip install -r requirements_win7.txt
pyinstaller --clean 中药材销售管理系统_Win7.spec
```

详细说明请参考 [WIN7_BUILD_GUIDE.md](WIN7_BUILD_GUIDE.md)

## 项目结构

```
python_app/
├── main.py                          # 主程序入口
├── database.py                      # 数据库模型
├── medicines_data_300.py            # 内置300味中药材数据
├── requirements.txt                 # 标准依赖列表
├── requirements_win7.txt            # Windows 7 兼容依赖
├── 中药材销售管理系统.spec           # 标准打包配置
├── 中药材销售管理系统_Win7.spec      # Windows 7 打包配置
├── build.bat                        # 标准打包脚本
├── build_win7.bat                   # Windows 7 打包脚本
├── 启动系统.bat                     # 启动脚本
├── WIN7_BUILD_GUIDE.md              # Windows 7 打包指南
├── core/                            # 核心模块
│   ├── database.py                  # 数据库连接
│   ├── models.py                    # 数据模型
│   ├── services.py                  # 业务服务
│   ├── cache.py                     # 缓存机制
│   ├── exceptions.py                # 异常处理
│   └── ...
├── views/                           # 视图模块
│   ├── medicine_view.py             # 中药材管理
│   ├── prescription_view.py         # 处方开具
│   ├── inventory_view.py            # 库存管理
│   └── history_view.py              # 处方历史
├── widgets/                         # 自定义控件
│   ├── page_header.py               # 页面标题栏
│   └── update_dialog.py             # 更新对话框
└── utils/                           # 工具模块
    ├── version.py                   # 版本管理
    ├── updater.py                   # 自动更新
    └── responsive_font.py           # 响应式字体
```

## 数据存储

- 数据库文件: `%APPDATA%\MedicineSystem\medicine_system.db` (SQLite)
- 日志文件: `%APPDATA%\MedicineSystem\logs\`
- 自动创建于用户 AppData 目录
- 支持数据备份和恢复

## 技术栈

- **前端框架**: PyQt5 5.15.x
- **数据库**: SQLite3
- **打包工具**: PyInstaller 5.x / 6.x
- **开发语言**: Python 3.9+

## 常见问题

### 1. 运行时提示缺少模块

```bash
pip install 模块名
```

### 2. 打包后运行闪退

- 检查是否缺少依赖
- 尝试在命令行运行查看错误信息

### 3. 数据库文件丢失

- 系统会自动创建新的数据库文件
- 内置300味中药材数据

### 4. Windows 7 无法运行

- 确认已安装 SP1
- 使用 Windows 7 兼容版本打包
- 参考 [WIN7_BUILD_GUIDE.md](WIN7_BUILD_GUIDE.md)

## 版本信息

- 当前版本: 2.4.2
- 开发语言: Python 3.9+
- 界面框架: PyQt5

## 更新日志

### v2.4.2 (2026-02-25)
- 修复处方开具模块闪退问题
- 修复数据库字典格式适配问题
- 增强库存检查逻辑
- 添加处方药材删除功能
- 完善异常处理和日志记录

### v2.4.1 (2026-02-24)
- 修复measure装饰器使用错误
- 修复数据库返回字典格式适配

### v2.4.0 (2026-02-24)
- 全面代码优化
- 新增配置管理模块
- 添加单元测试

### v2.3.0 (2026-02-24)
- 重大性能优化，查询速度提升37-110倍
- 新增内存缓存机制
- 重构代码架构
