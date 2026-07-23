// 自动更新：检查 Gitee Release、下载更新、启动安装程序
//
// 与原 Python 项目 utils/updater.py 对齐：
// - 调用 https://gitee.com/api/v5/repos/flyxjin/doctor/releases/latest
// - 解析 tag_name / name / body / assets
// - 流式下载到 %APPDATA%/com.medicine.system/downloads/
//
// v0.3.2 增强：
// - install_update 支持 silent 参数（NSIS /S 静默安装）+ 自动退出应用
// - 新增 check_and_download_silently：启动时后台静默检查并下载更新

use crate::models::{DownloadProgress, SilentUpdateResult, UpdateInfo};
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

    let save_path = build_download_path(&url, &app_handle)?;
    download_to_path(&url, &save_path, Some(&on_progress)).await?;
    Ok(save_path.to_string_lossy().to_string())
}

/// 启动下载好的 .exe 安装程序
///
/// - `silent=true`：传 `/S` 给 NSIS 安装程序（静默安装），并在启动安装程序后立即退出当前应用，
///   实现"无感更新"。安装程序（perMachine）会触发 UAC 提权，用户同意后静默覆盖安装。
/// - `silent=false`：保留原有行为，启动安装向导，应用不自动退出，用户手动关闭
#[tauri::command]
pub fn install_update(
    exe_path: String,
    silent: Option<bool>,
    app_handle: tauri::AppHandle,
) -> Result<(), String> {
    if exe_path.trim().is_empty() {
        return Err("安装程序路径为空".to_string());
    }
    let path = PathBuf::from(&exe_path);
    if !path.exists() {
        return Err(format!("安装程序文件不存在: {exe_path}"));
    }

    let do_silent = silent.unwrap_or(false);
    let mut cmd = std::process::Command::new(&path);
    if do_silent {
        // NSIS 静默安装参数：/S（大小写敏感，必须大写）
        cmd.arg("/S");
    }
    cmd.spawn()
        .map_err(|e| format!("启动安装程序失败: {e}"))?;

    if do_silent {
        // 静默模式下，立即退出当前应用，让安装程序接管覆盖安装。
        // Tauri exit(0) 会触发 cleanup 钩子，但不会阻塞。
        // 给安装程序一个短暂的启动窗口（避免文件锁竞争），然后退出。
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(500));
            app_handle.exit(0);
        });
    }
    Ok(())
}

/// 启动时后台静默检查 + 下载
///
/// 流程：
/// 1. 调用 Gitee API 获取最新 Release
/// 2. 与 `current_version` 比较（语义化版本字符串比较）
/// 3. 若有新版本且存在 .exe 资源，则静默流式下载到 downloads/ 目录
/// 4. 返回 `SilentUpdateResult { has_update, info, downloaded_path }`
///
/// 前端在应用启动时调用此命令，若 `has_update=true` 且 `downloaded_path` 非空，
/// 则弹窗提示用户"新版本已下载，是否立即重启更新？"，用户确认后调用
/// `install_update(path, true)` 触发静默安装 + 应用退出。
///
/// 任何步骤失败（网络错误、写盘失败等）均返回 `has_update=false`，
/// 不影响应用启动，前端可降级到 Settings 页手动检查。
#[tauri::command]
pub async fn check_and_download_silently(
    current_version: String,
    app_handle: tauri::AppHandle,
) -> Result<SilentUpdateResult, String> {
    // 1. 检查更新
    let info = check_for_update().await?;

    // 2. 比较版本：若最新版本不高于当前版本，则无需更新
    if !is_newer_version(&info.version, &current_version) {
        return Ok(SilentUpdateResult {
            has_update: false,
            info,
            downloaded_path: String::new(),
        });
    }

    // 3. 若无 .exe 下载地址，仅返回更新信息（前端可引导用户手动下载）
    if info.download_url.trim().is_empty() {
        return Ok(SilentUpdateResult {
            has_update: true,
            info,
            downloaded_path: String::new(),
        });
    }

    // 4. 静默下载到 downloads/ 目录（不推送进度）
    let save_path = build_download_path(&info.download_url, &app_handle)?;
    match download_to_path(&info.download_url, &save_path, None).await {
        Ok(_) => Ok(SilentUpdateResult {
            has_update: true,
            info,
            downloaded_path: save_path.to_string_lossy().to_string(),
        }),
        Err(e) => {
            // 下载失败：仍返回 has_update=true，让前端可引导用户到 Settings 页重试
            // 不使用 log crate（项目未引入），直接 eprintln 输出到 stderr 便于排查
            eprintln!("[updater] 静默下载失败，前端可降级到手动下载: {e}");
            Ok(SilentUpdateResult {
                has_update: true,
                info,
                downloaded_path: String::new(),
            })
        }
    }
}

// ==================== 内部辅助函数 ====================

/// 根据 URL 推导下载文件本地保存路径
fn build_download_path(url: &str, app_handle: &tauri::AppHandle) -> Result<PathBuf, String> {
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
    Ok(download_dir.join(&safe_filename))
}

/// 流式下载到指定路径；`on_progress` 为 None 时静默下载（无进度回调）
async fn download_to_path(
    url: &str,
    save_path: &PathBuf,
    on_progress: Option<&Channel<DownloadProgress>>,
) -> Result<(), String> {
    // 大文件下载不能用总超时（否则下不完），仅限制连接阶段超时
    let client = reqwest::Client::builder()
        .user_agent("medicine-system-updater/1.0")
        .connect_timeout(std::time::Duration::from_secs(30))
        .build()
        .map_err(|e| format!("创建 HTTP 客户端失败: {e}"))?;

    let response = client
        .get(url)
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

    let mut file = tokio::fs::File::create(save_path)
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
        if let Some(ch) = on_progress {
            let _ = ch.send(DownloadProgress {
                downloaded,
                total: if total == 0 { downloaded } else { total },
            });
        }
    }

    file.flush()
        .await
        .map_err(|e| format!("刷新文件失败: {e}"))?;

    Ok(())
}

/// 语义化版本比较：返回 `remote > current` 时为 true
///
/// 简化实现：按 `.` 分段，逐段比较数字大小；非数字段按字符串字典序比较。
/// 例：`is_newer_version("0.3.2", "0.3.1") == true`
fn is_newer_version(remote: &str, current: &str) -> bool {
    version_segments(remote) > version_segments(current)
}

/// 将版本字符串解析为可比较的元组向量
fn version_segments(v: &str) -> Vec<u64> {
    v.trim_start_matches('v')
        .split('.')
        .map(|s| s.parse::<u64>().unwrap_or(0))
        .collect()
}

// ==================== 单元测试 ====================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_newer_version_basic() {
        assert!(is_newer_version("0.3.2", "0.3.1"));
        assert!(is_newer_version("0.4.0", "0.3.9"));
        assert!(is_newer_version("1.0.0", "0.9.9"));
    }

    #[test]
    fn test_is_newer_version_equal() {
        assert!(!is_newer_version("0.3.1", "0.3.1"));
    }

    #[test]
    fn test_is_newer_version_older() {
        assert!(!is_newer_version("0.3.0", "0.3.1"));
        assert!(!is_newer_version("0.2.9", "0.3.0"));
    }

    #[test]
    fn test_is_newer_version_with_v_prefix() {
        assert!(is_newer_version("v0.3.2", "0.3.1"));
        assert!(is_newer_version("0.3.2", "v0.3.1"));
    }

    #[test]
    fn test_version_segments_parses_correctly() {
        assert_eq!(version_segments("0.3.2"), vec![0, 3, 2]);
        assert_eq!(version_segments("v1.2.3"), vec![1, 2, 3]);
        assert_eq!(version_segments("0.3"), vec![0, 3]);
    }

    #[test]
    fn test_version_segments_handles_invalid_segments() {
        // 非数字段解析为 0
        assert_eq!(version_segments("0.3.x"), vec![0, 3, 0]);
        assert_eq!(version_segments("a.b.c"), vec![0, 0, 0]);
    }
}
