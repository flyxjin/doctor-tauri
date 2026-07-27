; =========================================================================
; 中药材销售管理系统（Python 版）NSIS 安装脚本
; =========================================================================
; 对应 Gitee Issue: IK4DWR
;
; 分发内容：
;   - pyappify.exe（~3MB，重命名为「中药材销售管理系统.exe」）
;   - pyappify.yml（PyAppify 启动器配置，指向本仓库）
;   - assets/icon.ico（快捷方式 + 控制面板图标）
;
; 安装模式：currentUser（无需管理员权限，与 PyAppify 用户态运行时一致）
; 安装目录：%LOCALAPPDATA%\Programs\中药材销售管理系统
; 静默安装：NSIS 原生 /S 参数
; 卸载：注册到 HKCU Uninstall 键，控制面板可见
;
; 编译：makensis installer.nsi
;   可通过 /D 指定版本与源文件路径覆盖默认值：
;   makensis /DAPP_VERSION=5.1.0 /DPYAPPIFY_EXE=build\pyappify.exe installer.nsi
; =========================================================================

Unicode true
ManifestDPIAware true

; --- 版本号：优先用命令行 /DAPP_VERSION 传入，否则从 utils/version.py 读取 ---
; 路径相对 makensis 调用时的工作目录（build_installer.bat 会 cd 到 python_app/）
!ifndef APP_VERSION
  !searchparse /file "utils\version.py" `CURRENT_VERSION = "` APP_VERSION `"`
!endif
!ifndef APP_VERSION
  !error "APP_VERSION 未能从 utils/version.py 解析，请检查 CURRENT_VERSION 定义"
!endif

; --- 源文件路径：默认相对 build/ 目录，可由 build_installer.bat 通过 /D 覆盖 ---
!ifndef PYAPPIFY_EXE
  !define PYAPPIFY_EXE "build\pyappify.exe"
!endif
!ifndef PYAPPIFY_YML
  !define PYAPPIFY_YML "pyappify.yml"
!endif
!ifndef APP_ICON
  !define APP_ICON "assets\icon.ico"
!endif

; --- 应用元信息 ---
!define PRODUCT_NAME "中药材销售管理系统"
!define PRODUCT_PUBLISHER "东方本草"
!define PRODUCT_URL "https://gitee.com/flyxjin/doctor"
!define PRODUCT_EXE "中药材销售管理系统.exe"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

; --- 输出文件名：加 _python 后缀以与 Tauri 版区分 ---
!define OUT_FILE "dist\中药材销售管理系统_python_${APP_VERSION}_x64-setup.exe"

; =========================================================================
; 编译器配置
; =========================================================================
Name "${PRODUCT_NAME}"
BrandingText "${PRODUCT_PUBLISHER}"
OutFile "${OUT_FILE}"
InstallDir "$LOCALAPPDATA\Programs\${PRODUCT_NAME}"
RequestExecutionLevel user
SetCompressor /SOLID lzma
ShowInstDetails show
ShowUnInstDetails show

; 安装目录记忆：若已安装，复用上次的目录
InstallDirRegKey HKCU "${UNINST_KEY}" "InstallLocation"

; 文件版本信息（Windows 文件属性对话框）
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} 安装程序（Python 版）"
VIAddVersionKey "LegalCopyright" "© 2026 ${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"

; =========================================================================
; MUI2 现代界面
; =========================================================================
!include "MUI2.nsh"
!include "FileFunc.nsh"

; 安装程序图标
!define MUI_ICON "${APP_ICON}"
!define MUI_UNICON "${APP_ICON}"

; 界面语言：简体中文
!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES
!insertmacro MUI_LANGUAGE "SimpChinese"

; --- 安装页面 ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; --- 卸载页面 ---
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; =========================================================================
; 安装逻辑
; =========================================================================
Section "Install" SecInstall
  SectionIn RO
  SetOutPath "$INSTDIR"

  ; 若旧版 exe 仍在运行，提示关闭（避免 File 覆盖失败）
  Call CloseAppIfRunning

  ; 主程序：将 pyappify.exe 重命名为产品名
  File /oname="${PRODUCT_EXE}" "${PYAPPIFY_EXE}"

  ; 启动器配置（必须与 exe 同目录）
  File /oname="pyappify.yml" "${PYAPPIFY_YML}"

  ; 图标资源（快捷方式与控制面板 DisplayIcon 使用）
  File /oname="icon.ico" "${APP_ICON}"

  ; 写入卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; --- 控制面板「程序和功能」注册项（HKCU，currentUser 模式）---
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "${UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKCU "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\icon.ico"
  WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKCU "${UNINST_KEY}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
  WriteRegStr HKCU "${UNINST_KEY}" "URLInfoAbout" "${PRODUCT_URL}"
  WriteRegStr HKCU "${UNINST_KEY}" "URLUpdateInfo" "${PRODUCT_URL}"
  WriteRegStr HKCU "${UNINST_KEY}" "HelpLink" "${PRODUCT_URL}"
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoRepair" 1

  ; 估算安装体积（KB），写入 EstimatedSize
  ${GetSize} "$INSTDIR" "/S=0K /G=0" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKCU "${UNINST_KEY}" "EstimatedSize" "$0"

  ; --- 快捷方式 ---
  ; 静默安装时 MUI_PAGE_FINISH 不显示，需主动创建桌面快捷方式
  CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_EXE}" "" "$INSTDIR\icon.ico" 0
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_EXE}" "" "$INSTDIR\icon.ico" 0
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\卸载.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\icon.ico" 0

  ; 静默安装时自动关闭安装详情页
  ${If} ${Silent}
    SetAutoClose true
  ${EndIf}
SectionEnd

; =========================================================================
; 卸载逻辑
; =========================================================================
Section "Uninstall"
  ; 若程序仍在运行，尝试关闭
  Call un.CloseAppIfRunning

  ; 删除主程序与配置
  Delete "$INSTDIR\${PRODUCT_EXE}"
  Delete "$INSTDIR\pyappify.yml"
  Delete "$INSTDIR\icon.ico"
  Delete "$INSTDIR\uninstall.exe"

  ; 删除快捷方式
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\卸载.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"

  ; 清理注册项
  DeleteRegKey HKCU "${UNINST_KEY}"

  ; 尝试删除安装目录（仅当为空时）
  RMDir "$INSTDIR"

  ${If} ${Silent}
    SetAutoClose true
  ${EndIf}
SectionEnd

; =========================================================================
; 辅助函数：检测并关闭正在运行的主程序
; =========================================================================
Function CloseAppIfRunning
  ; 通过窗口标题检测主程序是否运行
  FindWindow $0 "" "${PRODUCT_NAME}"
  ${If} $0 <> 0
    ${IfNot} ${Silent}
      MessageBox MB_OKCANCEL|MB_ICONQUESTION \
        "${PRODUCT_NAME} 正在运行，需要关闭后才能继续安装。$\r$\n$\r$\n点击「确定」自动关闭并继续，或点击「取消」退出。" \
        IDOK close_it
        Abort
    ${Else}
      Goto close_it
    ${EndIf}
    close_it:
      ; 发送关闭消息，等待最多 3 秒
      SendMessage $0 ${WM_CLOSE} 0 0 /TIMEOUT=3000
  ${EndIf}
FunctionEnd

Function un.CloseAppIfRunning
  FindWindow $0 "" "${PRODUCT_NAME}"
  ${If} $0 <> 0
    ${IfNot} ${Silent}
      MessageBox MB_OKCANCEL|MB_ICONQUESTION \
        "${PRODUCT_NAME} 正在运行，需要关闭后才能卸载。$\r$\n$\r$\n点击「确定」自动关闭并继续，或点击「取消」退出。" \
        IDOK close_it
        Abort
    ${Else}
      Goto close_it
    ${EndIf}
    close_it:
      SendMessage $0 ${WM_CLOSE} 0 0 /TIMEOUT=3000
  ${EndIf}
FunctionEnd
