@echo off
chcp 65001 >nul
echo ========================================
echo   中药材销售管理系统 - 打包脚本 v2.0
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo [1/4] 清理旧的打包文件...
if exist "build" rmdir /s /q "build"
if exist "dist\中药材销售管理系统.exe" del /q "dist\中药材销售管理系统.exe"

echo [2/4] 安装/更新依赖...
pip install -r requirements.txt -q

echo [3/4] 打包应用程序...
pyinstaller --clean --noconfirm "中药材销售管理系统.spec"

echo [4/4] 创建启动脚本...
echo @echo off > dist\启动系统.bat
echo chcp 65001 ^>nul >> dist\启动系统.bat
echo start "" "中药材销售管理系统.exe" >> dist\启动系统.bat

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo   输出目录: %cd%\dist\
echo   主程序: 中药材销售管理系统.exe
echo   启动脚本: 启动系统.bat
echo.
echo   文件大小:
for %%I in ("dist\中药材销售管理系统.exe") do echo   %%~zI 字节 (约 %%~nxI)
echo.
echo ========================================
echo.
pause