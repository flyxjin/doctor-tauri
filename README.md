# 中药材销售管理系统 (Python桌面版)

## 系统简介

本系统是一款基于Python + PyQt5开发的原生桌面应用程序，面向药店医生使用的中药材销售管理系统。无需浏览器，双击即可运行。

## 功能模块

1. **中药材管理** - 药材信息的录入、查询、编辑、删除
2. **开具处方** - 患者信息录入、药材选择、自动计算金额
3. **库存管理** - 入库、出库、库存预警、库存历史
4. **处方历史** - 历史处方查询、详情查看、删除

## 系统要求

- Windows 7 及以上版本
- Python 3.8 或更高版本

## 安装步骤

### 方法一：直接运行（需要Python环境）

1. **安装Python**
   - 下载地址: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行系统**
   - 双击 `启动系统.bat` 文件
   - 或在命令行运行: `python main.py`

### 方法二：打包为exe（无需Python环境）

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **打包应用**
   - 双击 `build.bat` 文件
   - 或运行: `pyinstaller --onefile --windowed --name "中药材销售管理系统" main.py`

3. **运行打包后的应用**
   - 打包完成后，可执行文件位于 `dist\中药材销售管理系统.exe`
   - 双击即可运行，无需安装Python

## 项目结构

```
python_app/
├── main.py              # 主程序入口
├── database.py          # 数据库模型
├── requirements.txt     # 依赖列表
├── build.bat           # 打包脚本
├── 启动系统.bat         # 启动脚本
└── views/              # 视图模块
    ├── __init__.py
    ├── medicine_view.py     # 中药材管理
    ├── prescription_view.py # 处方开具
    ├── inventory_view.py    # 库存管理
    └── history_view.py      # 处方历史
```

## 数据存储

- 数据库文件: `medicine_system.db` (SQLite)
- 自动创建于程序运行目录
- 支持数据备份和恢复

## 技术栈

- **前端框架**: PyQt5
- **数据库**: SQLite3
- **打包工具**: PyInstaller

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
- 预置10种常见中药材数据

## 版本信息

- 版本: 1.0.0
- 开发语言: Python 3.8+
- 界面框架: PyQt5
