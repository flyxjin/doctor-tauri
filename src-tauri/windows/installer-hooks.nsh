; NSIS 安装器自定义钩子（tauri.conf.json → bundle.windows.nsis.installerHooks 引用）
;
; 背景：v1.11.0 及之前为 perMachine 全机安装（登记 HKLM）。v1.12.0 起 currentUser
; 按用户安装（免管理员）。若用户选择/沿用了旧版登记的安装目录：
;   1. 旧程序仍在运行时文件被锁（currentUser 进程查杀杀不掉提升运行的旧实例）；
;   2. 对旧目录（如 Program Files 类）可能无写权限。
;
; 处理（v1.12.2，条件重定向）：仅当选中目录正是 HKLM 登记的旧目录时，
; 重定向到当前用户目录；用户自定义的其他目录完全尊重其选择——
; 该目录会写入 HKCU，静默更新时自动沿用。

!macro NSIS_HOOK_PREINSTALL
  ; 读取旧版（perMachine）在 HKLM 登记的安装目录
  ReadRegStr $R9 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCTNAME}" "InstallLocation"
  StrCmp $R9 "" done_legacy_redirect

  ; 规范化比较：去掉两侧尾部反斜杠（StrCmp 大小写不敏感）
  StrCpy $R8 "$INSTDIR"
  StrCpy $R6 $R8 1 -1
  StrCmp $R6 "\" 0 +2
    StrCpy $R8 $R8 -1
  StrCpy $R7 "$R9"
  StrCpy $R6 $R7 1 -1
  StrCmp $R6 "\" 0 +2
    StrCpy $R7 $R7 -1

  ; 未选中旧目录 → 尊重用户选择
  StrCmp $R8 $R7 0 done_legacy_redirect

  ; 命中旧目录 → 重定向到当前用户目录（与业务数据同侧），避免锁冲突与权限问题
  StrCpy $INSTDIR "$LOCALAPPDATA\${PRODUCTNAME}"
  SetOutPath "$INSTDIR"

  done_legacy_redirect:
!macroend
