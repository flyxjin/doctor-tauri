@echo off
chcp 65001 >nul
echo ========================================
echo   中药材销售管理系统 - 打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo 正在安装依赖...
pip install -r requirements.txt

echo.
echo 正在打包应用程序...
pyinstaller --onefile --windowed --name "中药材销售管理系统" --icon=icon.ico main.py

echo.
echo ========================================
echo   打包完成！
echo   可执行文件位于: dist\中药材销售管理系统.exe
echo ========================================
echo.
pause
