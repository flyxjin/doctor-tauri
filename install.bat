@echo off
chcp 65001 >nul
title 中药材销售管理系统 - 安装程序

echo ============================================
echo   中药材销售管理系统 - 安装程序
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
set "APP_VERSION=0.3.4"
set "EXE_NAME=medicine-system.exe"

echo [1/4] 创建安装目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [2/4] 复制程序文件...
copy /Y "%~dp0%EXE_NAME%" "%INSTALL_DIR%\%EXE_NAME%" >nul

echo [3/4] 创建快捷方式...
REM 桌面快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\中药材销售管理系统.lnk'); $s.TargetPath = '%INSTALL_DIR%\%EXE_NAME%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = '中药材销售管理系统'; $s.Save()"

REM 开始菜单快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Programs') + '\中药材销售管理系统.lnk'); $s.TargetPath = '%INSTALL_DIR%\%EXE_NAME%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = '中药材销售管理系统'; $s.Save()"

echo [4/4] 创建卸载入口...
REM 注册到"添加/删除程序"
powershell -Command "$key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\中药材销售管理系统'; New-Item -Path $key -Force | Out-Null; Set-ItemProperty -Path $key -Name 'DisplayName' -Value '中药材销售管理系统'; Set-ItemProperty -Path $key -Name 'DisplayVersion' -Value '0.3.4'; Set-ItemProperty -Path $key -Name 'Publisher' -Value '东方本草'; Set-ItemProperty -Path $key -Name 'InstallLocation' -Value '%INSTALL_DIR%'; Set-ItemProperty -Path $key -Name 'DisplayIcon' -Value '%INSTALL_DIR%\%EXE_NAME%'; Set-ItemProperty -Path $key -Name 'UninstallString' -Value 'cmd /c rmdir /s /q \"%INSTALL_DIR%\" & del /q \"%USERPROFILE%\Desktop\中药材销售管理系统.lnk\"'"

echo.
echo ============================================
echo   安装完成！
echo ============================================
echo.
echo   安装路径: %INSTALL_DIR%
echo   桌面快捷方式已创建
echo   开始菜单快捷方式已创建
echo.
echo   数据存储: %%APPDATA%%\com.medicine.system\
echo.
echo   现在可以双击桌面图标启动程序。
echo.
pause
