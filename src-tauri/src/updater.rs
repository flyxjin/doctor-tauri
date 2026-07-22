// 自动更新：检查 Gitee Release、下载更新、启动安装程序
//
// 与原 Python 项目 utils/updater.py 对齐：
// - 调用 https://gitee.com/api/v5/repos/flyxjin/doctor/releases/latest
// - 解析 tag_name / name / body / assets
// - 流式下载到 %APPDATA%/com.medicine.system/downloads/

use crate::models::{DownloadProgress, UpdateInfo};
use futures_util::StreamExt;
use std::path::PathBuf;
use tauri::ipc::Channel;
use tauri::Manager;
use tokio::io::AsyncWriteExt;

const GITEE_RELEASES_URL: &str = "https://gitee.com/api/v5/repos/flyxjin/doctor/releases/latest";

/// 检查 Gitee 最新 Release，解析 tag_name / name / body / assets
#[tauri::command]
pub async fn check_for_update() -> Result<UpdateInfo, String> {
    let client = reqwest::Client::builder()
        .user_agent("medicine-system-updater/1.0")
        .timeout(std::time::Duration::from_secs(15))
        .build()
        .map_err(|e| format!("创建 HTTP 客户端失败: {e}"))?;

    let resp = client
        .get(GITEE_RELEASES_URL)
        .header("Accept", "application/json")
        .send()
        .await
        .map_err(|e| format!("请求 Gitee API 失败: {e}"))?;

    if !resp.status().is_success() {
        return Err(format!(
            "Gitee API 返回错误状态码: {}",
            resp.status().as_u16()
        ));
    }

    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析 Release 数据失败: {e}"))?;

    let tag = body["tag_name"]
        .as_str()
        .unwrap_or("0.0.0")
        .trim_start_matches('v')
        .to_string();
    let release_name = body["name"].as_str().unwrap_or("").to_string();
    let changelog = body["body"].as_str().unwrap_or("").to_string();

    // 在 assets 中找 .exe（排除 update 类的辅助文件）
    let mut download_url = String::new();
    let mut file_size: u64 = 0;
    if let Some(assets) = body["assets"].as_array() {
        for asset in assets {
            let name = asset["name"].as_str().unwrap_or("");
            let lower = name.to_lowercase();
            if lower.ends_with(".exe") && !lower.contains("update") {
                download_url = asset["browser_download_url"]
                    .as_str()
                    .unwrap_or("")
                    .to_string();
                file_size = asset["size"].as_u64().unwrap_or(0);
                break;
            }
        }
    }

    Ok(UpdateInfo {
        version: tag,
        release_name,
        changelog,
        download_url,
        file_size,
    })
}

/// 下载更新到下载目录，通过 Channel 推送进度
///
/// 返回下载完成的本地路径
#[tauri::command]
pub async fn download_update(
    url: String,
    on_progress: Channel<DownloadProgress>,
    app_handle: tauri::AppHandle,
) -> Result<String, String> {
    if url.trim().is_empty() {
        return Err("下载地址为空".to_string());
    }

    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("无法获取应用数据目录: {e}"))?;
    let download_dir = app_data_dir.join("downloads");
    std::fs::create_dir_all(&download_dir)
        .map_err(|e| format!("创建下载目录失败: {e}"))?;

    let filename = url
        .rsplit('/')
        .next()
        .filter(|s| !s.is_empty())
        .unwrap_or("medicine_system_update.exe")
        .to_string();
    // 过滤 Windows 非法字符
    let safe_filename = filename
        .chars()
        .map(|c| match c {
            '<' | '>' | ':' | '"' | '/' | '\\' | '|' | '?' | '*' => '_',
            _ => c,
        })
        .collect::<String>();
    let save_path: PathBuf = download_dir.join(&safe_filename);

    // 大文件下载不能用总超时（否则下不完），仅限制连接阶段超时
    let client = reqwest::Client::builder()
        .user_agent("medicine-system-updater/1.0")
        .connect_timeout(std::time::Duration::from_secs(30))
        .build()
        .map_err(|e| format!("创建 HTTP 客户端失败: {e}"))?;

    let response = client
        .get(&url)
        .send()
        .await
        .map_err(|e| format!("发起下载请求失败: {e}"))?;

    if !response.status().is_success() {
        return Err(format!(
            "下载失败，HTTP 状态码: {}",
            response.status().as_u16()
        ));
    }

    let total = response.content_length().unwrap_or(0);

    let mut file = tokio::fs::File::create(&save_path)
        .await
        .map_err(|e| format!("创建本地文件失败: {e}"))?;

    let mut stream = response.bytes_stream();
    let mut downloaded: u64 = 0;

    while let Some(chunk) = stream.next().await {
        let chunk = chunk.map_err(|e| format!("读取数据块失败: {e}"))?;
        file.write_all(&chunk)
            .await
            .map_err(|e| format!("写入数据失败: {e}"))?;
        downloaded += chunk.len() as u64;
        let _ = on_progress.send(DownloadProgress {
            downloaded,
            total: if total == 0 { downloaded } else { total },
        });
    }

    file.flush()
        .await
        .map_err(|e| format!("刷新文件失败: {e}"))?;

    Ok(save_path.to_string_lossy().to_string())
}

/// 启动下载好的 .exe 安装程序
///
/// 使用 detached spawn，启动后立即返回；当前应用不会自动退出，
/// 用户可在安装程序接管后手动关闭应用
#[tauri::command]
pub fn install_update(exe_path: String) -> Result<(), String> {
    if exe_path.trim().is_empty() {
        return Err("安装程序路径为空".to_string());
    }
    let path = PathBuf::from(&exe_path);
    if !path.exists() {
        return Err(format!("安装程序文件不存在: {exe_path}"));
    }
    std::process::Command::new(&path)
        .spawn()
        .map_err(|e| format!("启动安装程序失败: {e}"))?;
    Ok(())
}
