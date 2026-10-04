; NSIS 安装器自定义钩子（tauri.conf.json → bundle.windows.nsis.installerHooks 引用）
;
; 背景：v1.11.0 及之前为 perMachine 全机安装（Program Files / 自定义盘符，登记 HKLM）。
; v1.12.0 起切换为 currentUser（按用户安装、免管理员），但 NSIS 会沿用注册表里的
; 旧安装目录（或用户手动选回旧目录），导致：
;   1. 旧程序仍在运行时文件被锁（"无法打开要写入的文件"）；
;   2. currentUser 的进程查杀只覆盖当前用户进程，杀不掉提升权限运行的旧实例；
;   3. 对旧目录（如 Program Files）可能没有写权限。
;
; 处理：currentUser 模式强制安装到当前用户目录（与业务数据所在 AppData 同侧），
; 不再写入旧目录。旧目录残留由应用启动时的迁移引导（打开系统卸载面板）清理。

!macro NSIS_HOOK_PREINSTALL
  ${If} $INSTDIR != "$LOCALAPPDATA\${PRODUCTNAME}"
    StrCpy $INSTDIR "$LOCALAPPDATA\${PRODUCTNAME}"
    SetOutPath "$INSTDIR"
  ${EndIf}
!macroend
