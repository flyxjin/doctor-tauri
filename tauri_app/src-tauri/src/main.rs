// 中药材销售管理系统 - Tauri 桌面端入口
// 在 release 模式下隐藏控制台窗口（Windows）
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    medicine_system_lib::run();
}
