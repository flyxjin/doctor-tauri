# Windows 7 兼容版本打包指南

## 概述

由于当前开发环境使用 Python 3.14.2 和 PyInstaller 6.x，这些版本不支持 Windows 7。本指南说明如何创建 Windows 7 兼容版本。

## 系统要求对比

| 组件 | 标准版本 | Windows 7 兼容版本 |
|------|----------|-------------------|
| Python | 3.14+ | 3.9.x |
| PyInstaller | 6.x | 5.13.2 |
| PyQt5 | 5.15.10 | 5.15.10 |
| Pillow | 10.1.0 | 9.5.0 |
| 操作系统 | Win8.1/10/11 | Win7 SP1+ |

## 打包步骤

### 方法一：使用独立 Python 3.9 环境（推荐）

1. **下载 Python 3.9.x**
   - 访问 https://www.python.org/downloads/release/python-3913/
   - 下载 Windows installer (64-bit)
   - 安装时勾选 "Add Python to PATH"

2. **创建虚拟环境**
   ```bash
   # 使用 Python 3.9 创建虚拟环境
   py -3.9 -m venv venv_win7
   
   # 激活虚拟环境
   venv_win7\Scripts\activate
   
   # 安装依赖
   pip install -r requirements_win7.txt
   ```

3. **执行打包**
   ```bash
   # 激活虚拟环境后运行
   build_win7.bat
   ```
   或手动执行：
   ```bash
   pyinstaller --clean 中药材销售管理系统_Win7.spec
   ```

4. **输出文件**
   - 位置：`dist\中药材销售管理系统_Win7.exe`

### 方法二：使用 conda 环境

1. **创建 Python 3.9 环境**
   ```bash
   conda create -n win7build python=3.9
   conda activate win7build
   ```

2. **安装依赖并打包**
   ```bash
   pip install -r requirements_win7.txt
   pyinstaller --clean 中药材销售管理系统_Win7.spec
   ```

## 文件说明

| 文件 | 说明 |
|------|------|
| `requirements_win7.txt` | Windows 7 兼容版本的依赖列表 |
| `中药材销售管理系统_Win7.spec` | Windows 7 兼容版本的 PyInstaller 配置 |
| `build_win7.bat` | Windows 7 版本打包脚本 |

## 注意事项

1. **Python 版本必须为 3.9.x**
   - Python 3.10+ 不支持 Windows 7
   - Python 3.8 也可以，但建议使用 3.9.x（最后一个官方支持 Win7 的版本）

2. **PyInstaller 版本必须为 5.x**
   - PyInstaller 6.x 需要 Windows 8.1+
   - 推荐使用 5.13.2

3. **Pillow 版本**
   - Pillow 10.x 可能存在兼容性问题
   - 建议使用 9.5.0

4. **Windows 7 系统要求**
   - 必须安装 SP1（Service Pack 1）
   - 建议安装所有 Windows 更新

## 验证打包结果

打包完成后，建议在 Windows 7 系统上进行测试：

1. 复制 `dist\中药材销售管理系统_Win7.exe` 到 Windows 7 电脑
2. 双击运行，检查是否正常启动
3. 测试主要功能：药材管理、处方开具、库存管理

## 常见问题

### Q: 打包时提示 Python 版本不对
A: 确保使用 Python 3.9.x，可以运行 `python --version` 检查

### Q: 打包后 exe 在 Win7 上无法运行
A: 
- 确认 Windows 7 已安装 SP1
- 检查是否使用了正确的 PyInstaller 5.x 版本
- 尝试以管理员身份运行

### Q: 缺少某些模块
A: 检查 spec 文件中的 hiddenimports 列表是否完整

## 技术背景

- Python 3.10+ 停止支持 Windows 7 的原因：使用了 Windows 8+ 才有的 API
- PyInstaller 6.x 同样使用了新版 Windows API
- Windows 7 于 2020 年 1 月结束微软官方支持
