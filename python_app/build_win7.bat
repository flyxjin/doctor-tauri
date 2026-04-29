@echo off
chcp 65001 >nul
echo ============================================
echo   中药材销售管理系统 - Windows 7 兼容版本打包
echo ============================================
echo.
echo 注意：此脚本需要在 Python 3.9.x 环境下运行
echo 当前 Python 版本：
python --version
echo.
echo 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements_win7.txt
)
echo.
echo 开始打包...
pyinstaller --clean 中药材销售管理系统_Win7.spec
echo.
if exist "dist\中药材销售管理系统_Win7.exe" (
    echo ============================================
    echo   打包成功！
    echo   输出文件: dist\中药材销售管理系统_Win7.exe
    echo ============================================
) else (
    echo 打包失败，请检查错误信息
)
pause
