@echo off
chcp 65001 >nul
echo ========================================
echo   中药材销售管理系统 - Windows 7 打包脚本
echo ========================================
echo.

REM 检查Python版本
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python
    echo 请从 https://www.python.org/downloads/release/python-3810/ 下载Python 3.8.10
    pause
    exit /b 1
)

REM 检查Python版本是否为3.8.x
python --version 2>&1 | findstr "3.8" >nul
if errorlevel 1 (
    echo 警告: 推荐使用Python 3.8.10以获得最佳Windows 7兼容性
    echo 当前Python版本:
    python --version
    echo.
    choice /C YN /M "是否继续打包?"
    if errorlevel 2 exit /b 1
)

echo [1/6] 清理旧的打包文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo [2/6] 安装Windows 7兼容依赖...
pip install -r requirements_win7.txt -q

echo [3/6] 创建版本信息文件...
if not exist "version_info.txt" (
    echo 版本信息文件不存在，跳过...
)

echo [4/6] 打包应用程序...
pyinstaller --clean --noconfirm "medicine_system_win7.spec"

if errorlevel 1 (
    echo.
    echo 错误: 打包失败！
    pause
    exit /b 1
)

echo [5/6] 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo start "" "dist\中药材销售管理系统_Win7\中药材销售管理系统_Win7.exe"
) > 启动系统_Win7.bat

echo [6/6] 创建发布说明...
(
echo ========================================
echo   中药材销售管理系统 Windows 7版
echo ========================================
echo.
echo 版本: 2.3.0-Win7
echo 发布日期: %date%
echo.
echo 系统要求:
echo - Windows 7 SP1 或更高版本
echo - 建议安装KB3063858更新 ^(TLS 1.2支持^)
echo.
echo 安装说明:
echo 1. 解压到任意目录
echo 2. 运行 启动系统_Win7.bat 或直接运行exe文件
echo.
echo 注意事项:
echo - 首次运行会在%%APPDATA%%\MedicineSystem创建数据目录
echo - 如遇网络问题，请确保系统已安装TLS 1.2支持
echo.
) > dist\发布说明.txt

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo   输出目录: %cd%\dist\中药材销售管理系统_Win7\
echo   启动脚本: 启动系统_Win7.bat
echo   发布说明: dist\发布说明.txt
echo.
echo ========================================
echo.
pause
