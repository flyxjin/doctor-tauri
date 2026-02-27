@echo off
chcp 65001 >nul
echo ========================================
echo   系统兼容性检测工具
echo   Windows 7 版本
echo ========================================
echo.

set ISSUES=0

echo [检测操作系统]
ver | findstr /i "6\.1\." >nul
if not errorlevel 1 (
    echo ✓ 检测到 Windows 7 系统
    echo.
    
    REM 检查Service Pack
    wmic os get ServicePackMajorVersion 2>nul | findstr "1" >nul
    if not errorlevel 1 (
        echo ✓ 已安装 Service Pack 1
    ) else (
        echo ✗ 未检测到 Service Pack 1
        echo   建议安装 Windows 7 SP1 以获得更好兼容性
        set /a ISSUES+=1
    )
) else (
    ver | findstr /i "10\." >nul
    if not errorlevel 1 (
        echo ✓ 检测到 Windows 10 系统
    ) else (
        echo ! 当前系统非 Windows 7 或 Windows 10
        echo   当前版本:
        ver
    )
)
echo.

echo [检测 Python]
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未检测到 Python
    echo   请从 https://www.python.org/downloads/release/python-3810/ 下载安装
    set /a ISSUES+=1
) else (
    python --version 2>&1 | findstr "3.8" >nul
    if not errorlevel 1 (
        echo ✓ Python 3.8.x 已安装
        python --version
    ) else (
        echo ! Python 版本非 3.8.x
        echo   当前版本:
        python --version
        echo   推荐使用 Python 3.8.10 以获得最佳 Windows 7 兼容性
    )
)
echo.

echo [检测依赖库]
python -c "import PyQt5; print('PyQt5:', PyQt5.QtCore.PYQT_VERSION_STR)" 2>nul
if errorlevel 1 (
    echo ✗ PyQt5 未安装
    set /a ISSUES+=1
)

python -c "import reportlab; print('reportlab:', reportlab.Version)" 2>nul
if errorlevel 1 (
    echo ✗ reportlab 未安装
    set /a ISSUES+=1
)

python -c "import PIL; print('Pillow:', PIL.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ Pillow 未安装
    set /a ISSUES+=1
)

python -c "import PyInstaller; print('PyInstaller:', PyInstaller.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ PyInstaller 未安装
    set /a ISSUES+=1
)
echo.

echo [检测 TLS 支持]
python -c "import ssl; print('SSL版本:', ssl.OPENSSL_VERSION)" 2>nul
if errorlevel 1 (
    echo ✗ SSL 模块异常
    set /a ISSUES+=1
)
echo.

echo ========================================
if %ISSUES%==0 (
    echo   系统兼容性检测通过！
) else (
    echo   发现 %ISSUES% 个问题需要解决
)
echo ========================================
echo.
pause
