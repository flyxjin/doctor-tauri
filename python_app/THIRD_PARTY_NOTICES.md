# 第三方组件声明 (Third Party Notices)

本项目（中药材销售管理系统 · Python 版）使用以下第三方开源组件。本声明用于满足各组件协议的合规要求。

---

## 1. PySide6 — LGPL v3

- **用途**：GUI 框架（Qt 6 for Python）
- **版权**：The Qt Company Ltd
- **协议**：GNU Lesser General Public License v3.0 (LGPL v3)
- **主页**：https://www.qt.io/qt-for-python

### LGPL v3 合规说明

根据 LGPL v3 协议要求，本项目作为「使用」（非衍生）LGPL 库的应用程序，声明如下：

1. **允许用户替换 LGPL 库**：本应用以动态链接方式使用 PySide6 / Qt 库。打包后的 exe（PyInstaller `--onefile` 模式）将 Qt 库嵌入归档，用户可通过以下方式替换：
   - 安装 Python 3.9+ 与 PySide6（`pip install PySide6`），从源码运行 `python main.py` 即可使用用户自行安装的 Qt 版本
   - 或使用 PyInstaller `--onedir` 模式重新打包，替换 `dist/` 目录下的 Qt DLL 文件

2. **允许逆向调试**：用户有权对本应用中 PySide6 / Qt 部分进行逆向工程与调试

3. **LGPL 协议文本**：完整协议见 https://www.gnu.org/licenses/lgpl-3.0.html

4. **源码获取**：PySide6 源码获取地址：https://code.qt.io/cgit/pyside/pyside-setup.git/

---

## 2. SQLAlchemy — MIT License

- **用途**：ORM 框架
- **协议**：MIT License
- **主页**：https://www.sqlalchemy.org/

---

## 3. Pydantic — MIT License

- **用途**：数据模型验证与序列化
- **协议**：MIT License
- **主页**：https://docs.pydantic.dev/

---

## 4. openpyxl — MIT License

- **用途**：Excel 读写
- **协议**：MIT License
- **主页**：https://openpyxl.readthedocs.io/

---

## 5. PyInstaller — GPL License（带例外条款）

- **用途**：打包工具（仅开发期使用，不包含在运行时）
- **协议**：GPL v2（带 Bootloader 例外条款）
- **主页**：https://pyinstaller.org/

### GPL 例外说明

PyInstaller 的 GPL 协议仅约束 PyInstaller 自身及其 Bootloader，**不传染被打包的应用程序**。本应用使用 PyInstaller 打包后，应用本身仍遵循 MIT License。

详见：https://pyinstaller.org/en/stable/license.html

---

## 联系方式

如对第三方组件声明有疑问，请通过 Gitee Issue 联系：
https://gitee.com/flyxjin/doctor/issues
