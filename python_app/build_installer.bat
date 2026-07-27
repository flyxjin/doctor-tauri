@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 中药材销售管理系统（Python 版）- NSIS 安装包构建

echo ============================================
echo   中药材销售管理系统（Python 版）
echo   NSIS 安装包构建脚本
echo ============================================
echo.

REM 切换到本脚本所在目录（python_app/）
cd /d "%~dp0"

REM --------------------------------------------
REM [1/5] 检测 NSIS 编译器 makensis
REM --------------------------------------------
set "MAKENSIS="
where makensis >nul 2>&1
if %errorlevel% equ 0 (
    set "MAKENSIS=makensis"
    goto :found_nsis
)

REM 常见安装位置回退（按 C/D 盘、x86/x64 顺序探测）
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "MAKENSIS=C:\Program Files (x86)\NSIS\makensis.exe"
    goto :found_nsis
)
if exist "C:\Program Files\NSIS\makensis.exe" (
    set "MAKENSIS=C:\Program Files\NSIS\makensis.exe"
    goto :found_nsis
)
if exist "D:\Program\NSIS\makensis.exe" (
    set "MAKENSIS=D:\Program\NSIS\makensis.exe"
    goto :found_nsis
)
if exist "D:\Program Files\NSIS\makensis.exe" (
    set "MAKENSIS=D:\Program Files\NSIS\makensis.exe"
    goto :found_nsis
)

echo [错误] 未找到 NSIS 编译器 makensis
echo.
echo 请从以下地址下载并安装 NSIS：
echo   https://nsis.sourceforge.io/Download
echo 安装时勾选「Add NSIS to system PATH」选项，
echo 或将 makensis.exe 所在目录加入系统 PATH。
echo.
goto :error_exit

:found_nsis
echo [1/5] NSIS 编译器: !MAKENSIS!
set "MAKENSIS_ESC=!MAKENSIS!"

REM --------------------------------------------
REM [2/5] 检查 pyappify.exe 启动器
REM --------------------------------------------
set "PYAPPIFY_EXE=build\pyappify.exe"
if not exist "%PYAPPIFY_EXE%" (
    echo [错误] 未找到 PyAppify 启动器: %PYAPPIFY_EXE%
    echo.
    echo 请从 PyAppify Releases 下载 pyappify.exe：
    echo   https://github.com/ok-oldking/pyappify/releases
    echo 下载后放置到: %CD%\build\pyappify.exe
    echo.
    echo 提示：也可在 python_app\ 下手动创建 build\ 目录后放入。
    echo.
    goto :error_exit
)

REM --------------------------------------------
REM [3/5] 从 utils\version.py 读取版本号
REM --------------------------------------------
set "APP_VERSION="
for /f "tokens=2 delims==" %%a in ('findstr /b /c:"CURRENT_VERSION" utils\version.py') do (
    set "raw=%%a"
    REM 去除前后空格与引号
    set "raw=!raw: =!"
    set "raw=!raw:"=!"
    set "APP_VERSION=!raw!"
)
if "!APP_VERSION!"=="" (
    echo [错误] 无法从 utils\version.py 读取 CURRENT_VERSION
    goto :error_exit
)
echo [2/5] 应用版本号: !APP_VERSION!
echo [3/5] PyAppify 启动器: %PYAPPIFY_EXE%

REM --------------------------------------------
REM [4/5] 准备输出目录
REM --------------------------------------------
if not exist dist mkdir dist
echo [4/5] 输出目录: %CD%\dist

REM --------------------------------------------
REM [5/5] 调用 makensis 编译
REM --------------------------------------------
echo [5/5] 开始编译 NSIS 安装包...
echo.
REM /D 定义值不含空格时不应加引号，否则引号会成为值的一部分导致 File 指令路径错误
"!MAKENSIS_ESC!" /DAPP_VERSION=!APP_VERSION! /DPYAPPIFY_EXE=%PYAPPIFY_EXE% installer.nsi
if %errorlevel% neq 0 (
    echo.
    echo [错误] NSIS 编译失败，请查看上方输出
    goto :error_exit
)

REM --------------------------------------------
REM 构建完成
REM --------------------------------------------
set "OUTPUT=dist\中药材销售管理系统_python_!APP_VERSION!_x64-setup.exe"
echo.
echo ============================================
echo   构建成功！
echo ============================================
echo.
echo   安装包: %OUTPUT%
echo   体积:
if exist "%OUTPUT%" (
    for %%f in ("%OUTPUT%") do echo     %%~zf 字节
)
echo.
echo   静默安装: "%OUTPUT%" /S
echo   静默卸载: "%%LOCALAPPDATA%%\Programs\中药材销售管理系统\uninstall.exe" /S
echo.
goto :ok_exit

:error_exit
echo.
echo ============================================
echo   构建失败
echo ============================================
exit /b 1

:ok_exit
exit /b 0
