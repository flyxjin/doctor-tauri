// 自动更新：检查 Gitee Release、下载更新、启动安装程序
//
// 仓库拆分后指向 Tauri 版主仓库 flyxjin/doctor-tauri：
// - 调用 https://gitee.com/api/v5/repos/flyxjin/doctor-tauri/releases/latest
// - 解析 tag_name / name / body / assets
// - 流式下载到 %APPDATA%/com.medicine.system/downloads/
//
// v0.3.2 增强：
// - install_update 支持 silent 参数（NSIS /S 静默安装）+ 自动退出应用
// - 新增 check_and_download_silently：启动时后台静默检查并下载更新
//
// v1.2.0 增强：
// - 下载完整性校验：下载完成后断言 downloaded == file_size（API 返回值），不一致则删除文件并报错
// - 并发保护：AtomicBool 防止多个下载任务写同一文件导致损坏
// - 单 chunk 读超时：60 秒无数据则中断，避免网络卡死导致永久挂起

use crate::models::{DownloadProgress, SilentUpdateResult, UpdateInfo};
use futures_util::StreamExt;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use tauri::ipc::Channel;
use tauri::Manager;
use tokio::io::AsyncWriteExt;

const GITEE_RELEASES_URL: &str =
    "https://gitee.com/api/v5/repos/flyxjin/doctor-tauri/releases/latest";

/// 下载并发保护：同一时刻只允许一个下载任务
/// 防止 check_and_download_silently 与用户手动 download_update 同时写同一文件
static DOWNLOADING: AtomicBool = AtomicBool::new(false);

/// 单 chunk 读取最大超时（秒）。超时则中断下载，避免网络卡死导致永久挂起。
const READ_TIMEOUT_SECS: u64 = 60;

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

    // 在 assets 中找 .exe（排除 update 类的辅助文件），并查找配套的 .sha256 校验文件
    let mut download_url = String::new();
    let mut file_size: u64 = 0;
    let mut exe_name = String::new();
    let mut checksum = String::new();
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
                exe_name = name.to_string();
                break;
            }
        }
        // 命名约定：<安装包文件名>.sha256（由 Release 工作流生成）
        if let Some(sha_url) = find_sha256_asset(assets, &exe_name) {
            match fetch_sha256_content(&client, &sha_url).await {
                Some(sum) => checksum = sum,
                None => eprintln!("[updater] 校验文件存在但解析失败，本次仅做大小校验"),
            }
        }
    }

    Ok(UpdateInfo {
        version: tag,
        release_name,
        changelog,
        download_url,
        file_size,
        checksum,
    })
}

/// 从 Release assets 里找与安装包配套的 `.sha256` 校验文件的下载地址
fn find_sha256_asset(assets: &[serde_json::Value], exe_name: &str) -> Option<String> {
    if exe_name.is_empty() {
        return None;
    }
    let expect = format!("{}.sha256", exe_name.to_lowercase());
    assets.iter().find_map(|a| {
        let name = a["name"].as_str()?;
        let url = a["browser_download_url"].as_str()?;
        (name.to_lowercase() == expect).then(|| url.to_string())
    })
}

/// 下载并解析 `.sha256` 校验文件（sha256sum 格式："hex  filename" 或裸 hex）
async fn fetch_sha256_content(client: &reqwest::Client, url: &str) -> Option<String> {
    let resp = client.get(url).send().await.ok()?;
    if !resp.status().is_success() {
        return None;
    }
    let text = resp.text().await.ok()?;
    parse_sha256_content(&text)
}

/// 解析 sha256sum 文本，返回十六进制摘要；格式非法返回 None
fn parse_sha256_content(text: &str) -> Option<String> {
    let token = text.split_whitespace().next()?.trim().to_lowercase();
    let valid = token.len() == 64 && token.chars().all(|c| c.is_ascii_hexdigit());
    valid.then_some(token)
}

/// 下载更新到下载目录，通过 Channel 推送进度
///
/// `file_size` 由前端从 `check_for_update` 返回的 `UpdateInfo.file_size` 传入，
/// 用于下载完成后完整性校验。`checksum` 为 Release 附带的 SHA256（可为空，
/// 为空时仅做大小校验）。避免后端再次调用 Gitee API 重复请求。
///
/// 返回下载完成的本地路径
#[tauri::command]
pub async fn download_update(
    url: String,
    file_size: u64,
    checksum: String,
    on_progress: Channel<DownloadProgress>,
    app_handle: tauri::AppHandle,
) -> Result<String, String> {
    if url.trim().is_empty() {
        return Err("下载地址为空".to_string());
    }
    // 纵深防御：限制下载源为发布渠道 host，封死 IPC 拉取任意 URL 的链路
    validate_download_url(&url)?;

    // 并发保护：若已有下载任务在进行，直接返回错误
    if DOWNLOADING.swap(true, Ordering::SeqCst) {
        return Err("已有下载任务在进行中，请等待完成后再试".to_string());
    }

    // 使用 RAII 守卫确保无论成功或失败都重置 DOWNLOADING 标志
    struct DownloadGuard;
    impl Drop for DownloadGuard {
        fn drop(&mut self) {
            DOWNLOADING.store(false, Ordering::SeqCst);
        }
    }
    let _guard = DownloadGuard;

    let save_path = build_download_path(&url, &app_handle)?;
    download_to_path(&url, &save_path, Some(&on_progress), file_size, &checksum).await?;
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
    // 纵深防御：仅允许执行应用下载目录内的 .exe，防止被注入的 renderer 借此执行任意程序
    validate_install_path(&path, &app_handle)?;

    let do_silent = silent.unwrap_or(false);
    let mut cmd = std::process::Command::new(&path);
    if do_silent {
        // NSIS 静默安装参数：/S（大小写敏感，必须大写）
        cmd.arg("/S");
    }
    cmd.spawn().map_err(|e| format!("启动安装程序失败: {e}"))?;

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

    // 4. 并发保护：若已有下载任务在进行，仅返回更新信息，不重复下载
    if DOWNLOADING.swap(true, Ordering::SeqCst) {
        eprintln!("[updater] 已有下载任务在进行，跳过静默下载");
        return Ok(SilentUpdateResult {
            has_update: true,
            info,
            downloaded_path: String::new(),
        });
    }

    struct DownloadGuard;
    impl Drop for DownloadGuard {
        fn drop(&mut self) {
            DOWNLOADING.store(false, Ordering::SeqCst);
        }
    }
    let _guard = DownloadGuard;

    // 5. 静默下载到 downloads/ 目录（不推送进度）
    // 同样校验下载源（URL 来自 Gitee API 响应，API 异常时不应拉取任意地址）
    if let Err(e) = validate_download_url(&info.download_url) {
        eprintln!("[updater] 静默下载 URL 校验失败: {e}");
        return Ok(SilentUpdateResult {
            has_update: true,
            info,
            downloaded_path: String::new(),
        });
    }
    let save_path = build_download_path(&info.download_url, &app_handle)?;
    let expected_size = info.file_size;
    let expected_checksum = info.checksum.clone();
    match download_to_path(
        &info.download_url,
        &save_path,
        None,
        expected_size,
        &expected_checksum,
    )
    .await
    {
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

/// 更新包下载源的 host 白名单（当前仅 Gitee Release）
///
/// 纵深防御：renderer 进程若被注入（XSS/供应链），可通过 IPC 拉取任意 URL。
/// 白名单将下载源限制在发布渠道，封死"下载任意 exe 再执行"的 RCE 链路。
const DOWNLOAD_HOST_WHITELIST: [&str; 1] = ["gitee.com"];

/// 校验下载 URL：必须为 https 且 host 在白名单内
fn validate_download_url(url: &str) -> Result<(), String> {
    let rest = url
        .strip_prefix("https://")
        .ok_or_else(|| "下载地址必须为 https 协议".to_string())?;
    // Gitee Release 资产 URL 不含 user@host 形式的用户信息，
    // 直接拒绝以排除 userinfo 与 host 混淆类绕过
    if rest.contains('@') {
        return Err("下载地址不应包含用户信息".to_string());
    }
    let host = rest
        .split(['/', '?', '#'])
        .next()
        .filter(|s| !s.is_empty())
        .ok_or_else(|| "下载地址缺少主机名".to_string())?;
    let host = host.split(':').next().unwrap_or(host);
    let host = host.to_ascii_lowercase();
    let allowed = DOWNLOAD_HOST_WHITELIST
        .iter()
        .any(|h| host == *h || host.ends_with(&format!(".{h}")));
    if !allowed {
        return Err(format!("下载地址主机不在允许列表内: {host}"));
    }
    Ok(())
}

/// 校验安装程序路径：必须位于应用数据目录 downloads/ 下且为 .exe 文件
///
/// 防止 IPC 调用者以 install_update 为跳板执行任意路径的程序
fn validate_install_path(exe_path: &Path, app_handle: &tauri::AppHandle) -> Result<(), String> {
    let extension_ok = exe_path
        .extension()
        .and_then(|e| e.to_str())
        .map(|e| e.eq_ignore_ascii_case("exe"))
        .unwrap_or(false);
    if !extension_ok {
        return Err("安装程序必须是 .exe 文件".to_string());
    }
    let download_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("无法获取应用数据目录: {e}"))?
        .join("downloads");
    let canonical_path = exe_path
        .canonicalize()
        .map_err(|_| format!("安装程序路径无效: {}", exe_path.display()))?;
    let canonical_dir = download_dir
        .canonicalize()
        .map_err(|e| format!("下载目录无效: {e}"))?;
    if !canonical_path.starts_with(&canonical_dir) {
        return Err("安装程序必须位于应用下载目录内".to_string());
    }
    Ok(())
}

/// 根据 URL 推导下载文件本地保存路径
fn build_download_path(url: &str, app_handle: &tauri::AppHandle) -> Result<PathBuf, String> {
    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("无法获取应用数据目录: {e}"))?;
    let download_dir = app_data_dir.join("downloads");
    std::fs::create_dir_all(&download_dir).map_err(|e| format!("创建下载目录失败: {e}"))?;

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
///
/// v1.2.0 增强：
/// - `expected_size` 用于下载完成后完整性校验（>0 时断言 downloaded == expected_size）
/// - 单 chunk 读取超时（READ_TIMEOUT_SECS 秒），避免网络卡死导致永久挂起
///
/// v1.3.x 增强：
/// - `expected_sha256` 非空时做哈希校验（防 Release 资产被替换），不一致删除文件并报错
async fn download_to_path(
    url: &str,
    save_path: &PathBuf,
    on_progress: Option<&Channel<DownloadProgress>>,
    expected_size: u64,
    expected_sha256: &str,
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

    loop {
        let timeout_result = tokio::time::timeout(
            std::time::Duration::from_secs(READ_TIMEOUT_SECS),
            stream.next(),
        )
        .await;

        let chunk_result = match timeout_result {
            Ok(Some(result)) => result,
            Ok(None) => break, // 流结束
            Err(_) => {
                return Err(format!(
                    "读取数据块超时（{READ_TIMEOUT_SECS} 秒无数据），已下载 {downloaded} 字节"
                ));
            }
        };

        let chunk = chunk_result.map_err(|e| format!("读取数据块失败: {e}"))?;
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

    // 完整性校验：若 API 返回了文件大小，断言下载字节数一致
    // 防止服务端提前断连导致下载截断，安装损坏的安装包
    if expected_size > 0 && downloaded != expected_size {
        // 删除不完整的下载文件
        let _ = tokio::fs::remove_file(save_path).await;
        return Err(format!(
            "下载完整性校验失败：期望 {expected_size} 字节，实际下载 {downloaded} 字节（文件可能被截断）"
        ));
    }

    // SHA256 校验：防安装包在发布渠道被替换或传输损坏（校验失败已删除文件）
    if !expected_sha256.trim().is_empty() {
        verify_file_checksum(save_path, expected_sha256)?;
    }

    Ok(())
}

/// 校验下载文件的 SHA256 与期望值一致；不一致删除文件并返回错误
fn verify_file_checksum(path: &Path, expected: &str) -> Result<(), String> {
    let actual = crate::commands::compute_file_sha256(&path.to_path_buf())?;
    if !actual.eq_ignore_ascii_case(expected.trim()) {
        let _ = std::fs::remove_file(path);
        return Err(format!(
            "更新包 SHA256 校验失败：期望 {expected}，实际 {actual}（文件已删除，请重新下载）"
        ));
    }
    Ok(())
}

/// 语义化版本比较：返回 `remote > current` 时为 true
///
/// 按 `.` 分段，逐段比较数字大小；非数字段按 0 处理。
/// 补齐到相同长度后比较，确保 `1.0` == `1.0.0`（语义化版本规范）。
/// 例：`is_newer_version("0.3.2", "0.3.1") == true`
fn is_newer_version(remote: &str, current: &str) -> bool {
    let r = version_segments(remote);
    let c = version_segments(current);
    // 补齐到相同长度，避免 [1,0] < [1,0,0] 的字典序问题
    let max_len = r.len().max(c.len());
    pad_segments(&r, max_len) > pad_segments(&c, max_len)
}

/// 将版本字符串解析为可比较的数字段向量
fn version_segments(v: &str) -> Vec<u64> {
    v.trim_start_matches('v')
        .split('.')
        .map(|s| s.parse::<u64>().unwrap_or(0))
        .collect()
}

/// 将版本段补齐到指定长度，不足部分用 0 填充
fn pad_segments(v: &[u64], len: usize) -> Vec<u64> {
    let mut result = v.to_vec();
    result.resize(len, 0);
    result
}

// ==================== 旧版（perMachine 管理员安装）迁移 ====================
//
// 背景：v1.11.0 及之前采用 perMachine 安装（HKLM 注册、需管理员），每次静默
// 更新都会触发 UAC 提权弹窗。v1.12.0 起切换为 currentUser（按用户安装、免提权）。
// 存量用户迁移：新版安装器找不到旧 HKLM 记录，会装入用户目录形成双份安装，
// 旧桌面/开始菜单图标仍指向旧版（版本永远落后、反复提示更新），因此需要
// 一次性检测 + 引导清理。
//
// 清理方式：不代为执行旧卸载程序（避免从注册表数据派生命令执行），而是
// 通过系统壳打开 Windows「安装的应用」面板，由用户走标准卸载流程。

/// 旧版（管理员/全机安装）残留信息
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct LegacyInstall {
    pub install_location: String,
    pub display_version: String,
    /// 当前运行的 exe 是否位于旧安装目录内（true = 尚未迁移到新版安装方式）
    pub running_from_legacy: bool,
}

/// 检测旧版（perMachine/HKLM 管理员安装）残留。
/// 只认定 HKLM 机器级登记为旧版；HKCU 登记是新版（currentUser）自身。
#[tauri::command]
pub fn detect_legacy_install(
    app_handle: tauri::AppHandle,
) -> Result<Option<LegacyInstall>, String> {
    #[cfg(windows)]
    {
        let product = app_handle.config().product_name.clone().unwrap_or_default();
        Ok(detect_legacy_install_win(&product))
    }
    #[cfg(not(windows))]
    {
        let _ = &app_handle;
        Ok(None)
    }
}

/// 打开 Windows「安装的应用」系统面板，引导用户卸载旧版本残留
#[tauri::command]
pub fn open_uninstall_panel(app_handle: tauri::AppHandle) -> Result<(), String> {
    use tauri_plugin_opener::OpenerExt;
    app_handle
        .opener()
        .open_url("ms-settings:appsfeatures", None::<&str>)
        .map_err(|e| format!("打开系统应用面板失败: {e}"))
}

#[cfg(windows)]
fn detect_legacy_install_win(product: &str) -> Option<LegacyInstall> {
    use winreg::enums::{HKEY_LOCAL_MACHINE, KEY_READ};
    use winreg::RegKey;

    if product.trim().is_empty() {
        return None;
    }
    let sub = format!(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{product}");
    // HKLM（perMachine 旧版登记处）优先；HKCU 是新版（currentUser）自身
    let Ok(hk) = RegKey::predef(HKEY_LOCAL_MACHINE).open_subkey_with_flags(&sub, KEY_READ) else {
        return None;
    };
    // 有 UninstallString 才认定为有效安装登记
    let uninstall_hint: String = hk.get_value("UninstallString").unwrap_or_default();
    if uninstall_hint.trim().is_empty() {
        return None;
    }
    let install_location: String = hk.get_value("InstallLocation").unwrap_or_default();
    let display_version: String = hk.get_value("DisplayVersion").unwrap_or_default();
    // 当前 exe 是否在旧安装目录内（大小写不敏感，容忍尾部路径分隔符差异）
    let loc_norm = install_location
        .trim_end_matches(['\\', '/'])
        .to_lowercase();
    let running_from_legacy = std::env::current_exe()
        .ok()
        .map(|p| {
            let exe = p.to_string_lossy().to_lowercase();
            !loc_norm.is_empty() && exe.starts_with(&loc_norm)
        })
        .unwrap_or(false);
    Some(LegacyInstall {
        install_location,
        display_version,
        running_from_legacy,
    })
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

    #[test]
    fn test_is_newer_version_different_segment_lengths() {
        // 1.0 与 1.0.0 语义相等，不应触发更新
        assert!(!is_newer_version("1.0.0", "1.0"));
        assert!(!is_newer_version("1.0", "1.0.0"));
        // 1.0.1 > 1.0
        assert!(is_newer_version("1.0.1", "1.0"));
        // 1.1 > 1.0.9
        assert!(is_newer_version("1.1", "1.0.9"));
    }

    #[test]
    fn test_validate_download_url() {
        // 合法：Gitee Release 资产
        assert!(validate_download_url(
            "https://gitee.com/owner/repo/releases/download/v1.3.0/app_1.3.0_x64-setup.exe"
        )
        .is_ok());
        // 合法：子域名（.gitee.com 结尾）
        assert!(validate_download_url("https://cdn.gitee.com/owner/repo/app.exe").is_ok());
        // 合法：大写 host + 端口
        assert!(validate_download_url("https://GITEE.COM:443/a/b.exe").is_ok());

        // 非法：http 明文
        assert!(validate_download_url("http://gitee.com/a.exe").is_err());
        // 非法：ftp
        assert!(validate_download_url("ftp://gitee.com/a.exe").is_err());
        // 非法：仿冒域名（gitee.com.evil.io 以 gitee.com 开头但不是其子域名）
        assert!(validate_download_url("https://gitee.com.evil.io/a.exe").is_err());
        assert!(validate_download_url("https://notgitee.com/a.exe").is_err());
        // 非法：其他 host
        assert!(validate_download_url("https://evil.com/a.exe").is_err());
        // 非法：user@host 形式的用户信息（含 gitee.com@evil.com 反向绕过）
        assert!(validate_download_url("https://evil.com@gitee.com/a.exe").is_err());
        assert!(validate_download_url("https://gitee.com@evil.com/a.exe").is_err());
        // 非法：空 host
        assert!(validate_download_url("https:///a.exe").is_err());
    }

    #[test]
    fn test_parse_sha256_content() {
        // sha256sum 标准格式："hex  filename"
        let hex = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678abcdef0123456789012345ab";
        assert_eq!(
            parse_sha256_content(&format!("{hex}  app_1.3.1_x64-setup.exe")),
            Some(hex.to_string())
        );
        // 裸 hex
        assert_eq!(parse_sha256_content(hex), Some(hex.to_string()));
        // 大写转小写
        assert_eq!(
            parse_sha256_content(&hex.to_uppercase()),
            Some(hex.to_string())
        );
        // 长度不对 / 非十六进制 / 空文本
        assert_eq!(parse_sha256_content("abc123"), None);
        assert_eq!(parse_sha256_content(&"z".repeat(64)), None);
        assert_eq!(parse_sha256_content(""), None);
    }

    #[test]
    fn test_find_sha256_asset() {
        let assets: Vec<serde_json::Value> = serde_json::json!([
            {"name": "medicine-system_1.3.1_x64-setup.exe", "browser_download_url": "https://gitee.com/a.exe"},
            {"name": "medicine-system_1.3.1_x64-setup.exe.sha256", "browser_download_url": "https://gitee.com/a.exe.sha256"},
            {"name": "README.md", "browser_download_url": "https://gitee.com/readme"}
        ])
        .as_array()
        .unwrap()
        .clone();
        assert_eq!(
            find_sha256_asset(&assets, "medicine-system_1.3.1_x64-setup.exe").as_deref(),
            Some("https://gitee.com/a.exe.sha256")
        );
        // 大小写不敏感匹配
        assert_eq!(
            find_sha256_asset(&assets, "Medicine-System_1.3.1_x64-Setup.EXE").as_deref(),
            Some("https://gitee.com/a.exe.sha256")
        );
        // 无配套校验文件
        assert_eq!(find_sha256_asset(&assets, "other.exe"), None);
        assert_eq!(find_sha256_asset(&assets, ""), None);
    }
}
