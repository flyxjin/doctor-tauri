// 库入口：注册插件、状态与 Tauri commands
mod backup;
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
        // 窗口位置/尺寸记忆：退出时保存，下次启动恢复
        .plugin(tauri_plugin_window_state::Builder::default().build())
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

            // 每日首次启动自动备份（当天无任何备份时静默创建；失败不阻塞启动）
            {
                let conn = db_state.lock()?;
                backup::auto_backup_if_needed(&app_data_dir, &conn);
            }

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
            commands::update_inventory_price,
            commands::batch_update_price,
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
            // 应用设置与我的方剂
            commands::get_app_settings,
            commands::set_app_setting,
            commands::list_my_templates,
            commands::save_my_template,
            commands::delete_my_template,
            // 统计与看板
            commands::get_dashboard_data,
            commands::get_statistics,
            commands::get_doctor_stats,
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
