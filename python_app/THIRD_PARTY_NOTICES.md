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

1. **允许用户替换 LGPL 库**：本应用以动态链接方式使用 PySide6 / Qt 库。自 v5.0.0 起，应用通过 [PyAppify](https://github.com/ok-oldking/pyappify) 启动器运行，启动器在用户机器上拉取独立 Python 3.12 环境并通过 `pip install PySide6` 安装 Qt 库到 `data/venv/` 目录，用户可执行以下任一方式替换：
   - 修改 `pyappify.yml` 中的 `requirements` 字段指定不同版本的 PySide6
   - 直接编辑 `data/venv/` 目录下的 PySide6 / Qt DLL 文件
   - 从源码运行 `python main.py` 即可使用用户自行安装的 Qt 版本

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

## 5. PyAppify — MIT License

- **用途**：应用打包 / 自动更新启动器（Rust 二进制，~3MB，不包含 Python 运行时）
- **协议**：MIT License
- **主页**：https://github.com/ok-oldking/pyappify

### 说明

PyAppify 启动器是独立的 Rust 程序，**不嵌入 Python 解释器或依赖库**。首次运行时，启动器从官方源下载独立 Python 3.12 与本应用 `requirements.txt` 声明的依赖到本地 `data/` 目录，应用代码与依赖均以源码 / wheel 形式存在，不构成静态或动态链接。PyAppify 自身遵循 MIT License，不传染本应用。

---

## 联系方式

如对第三方组件声明有疑问，请通过 Gitee Issue 联系：
https://gitee.com/flyxjin/doctor/issues
