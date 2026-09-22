// 库入口：注册插件、状态与 Tauri commands
mod commands;
mod compatibility;
mod db;
mod models;
mod updater;

use db::DbState;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // 解析用户数据目录并创建数据库文件 medicine_system.db
            let app_data_dir = app
                .path()
                .app_data_dir()
                .map_err(|e| format!("无法获取应用数据目录: {e}"))?;
            std::fs::create_dir_all(&app_data_dir).map_err(|e| format!("创建数据目录失败: {e}"))?;
            let db_path = app_data_dir.join("medicine_system.db");

            // 初始化数据库连接（单例，由 Tauri State 管理）
            let db_state = DbState::new(&db_path)?;
            // 执行所有编译期嵌入的迁移文件（幂等，由 schema_migrations 表追踪）
            db_state.run_migrations()?;

            app.manage(db_state);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // 药材管理
            commands::list_medicines,
            commands::get_medicine,
            commands::create_medicine,
            commands::update_medicine,
            commands::delete_medicine,
            // 库存管理
            commands::list_inventory,
            commands::update_stock,
            commands::adjust_stock,
            commands::list_inventory_history,
            commands::list_expiring_batches,
            // 处方管理
            commands::list_prescriptions,
            commands::create_prescription,
            commands::delete_prescription,
            // 客户管理
            commands::list_patients,
            commands::get_patient,
            commands::create_patient,
            commands::update_patient,
            commands::delete_patient,
            commands::get_patient_prescriptions,
            commands::get_patient_statistics,
            // 统计与看板
            commands::get_dashboard_data,
            commands::get_statistics,
            // 配伍禁忌
            commands::check_compatibility,
            // 批量导入 / 导出
            commands::batch_import_medicines,
            commands::export_medicines_csv,
            commands::download_import_template,
            commands::save_text_to_downloads,
            // 操作日志
            commands::list_operation_logs,
            // 打印处方
            commands::generate_prescription_html,
            // 数据备份与恢复
            commands::create_backup,
            commands::list_backups,
            commands::restore_backup,
            commands::delete_backup,
            // 自动更新
            updater::check_for_update,
            updater::download_update,
            updater::install_update,
            updater::check_and_download_silently,
        ])
        .run(tauri::generate_context!())
        .expect("运行 Tauri 应用时发生错误");
}
