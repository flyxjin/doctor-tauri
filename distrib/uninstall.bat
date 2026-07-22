@echo off
chcp 65001 >nul
title 中药材销售管理系统 - 卸载程序

echo ============================================
echo   中药材销售管理系统 - 卸载程序
echo ============================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 需要管理员权限，正在请求...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set "INSTALL_DIR=%ProgramFiles%\中药材销售管理系统"

echo [1/3] 关闭运行中的程序...
taskkill /F /IM medicine-system.exe >nul 2>&1

echo [2/3] 删除程序文件...
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

echo [3/3] 删除快捷方式...
del /q "%USERPROFILE%\Desktop\中药材销售管理系统.lnk" >nul 2>&1
del /q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\中药材销售管理系统.lnk" >nul 2>&1

REM 删除注册表卸载入口
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\中药材销售管理系统" /f >nul 2>&1

echo.
echo ============================================
echo   卸载完成！
echo ============================================
echo.
echo   程序文件已删除。
echo   用户数据保留在: %%APPDATA%%\com.medicine.system\
echo   如需彻底清除，请手动删除该目录。
echo.
pause
