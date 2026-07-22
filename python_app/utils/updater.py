import hashlib
import json
import os
import shutil
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from PySide6.QtCore import QThread, Signal

from utils.version import GITEE_RELEASES_URL, Version, VersionManager


class UpdateInfo:
    def __init__(self, data: Dict[str, Any]):
        self.version = data.get('tag_name', '0.0.0').replace('v', '')
        self.title = data.get('name', '')
        self.body = data.get('body', '')
        self.published_at = data.get('published_at', '')
        self.assets = data.get('assets', [])
        self.html_url = data.get('html_url', '')
        self.draft = data.get('draft', False)
        self.prerelease = data.get('prerelease', False)

    def get_download_url(self) -> Optional[str]:
        for asset in self.assets:
            name = asset.get('name', '').lower()
            if name.endswith('.exe') and 'update' not in name:
                return asset.get('browser_download_url')
        return None

    def get_file_size(self) -> int:
        for asset in self.assets:
            name = asset.get('name', '').lower()
            if name.endswith('.exe') and 'update' not in name:
                return asset.get('size', 0)
        return 0

    def get_file_size_display(self) -> str:
        size = self.get_file_size()
        if size <= 0:
            return "未知"
        elif size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class CheckUpdateThread(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, version_manager: VersionManager):
        super().__init__()
        self.version_manager = version_manager

    def run(self):
        try:
            update_info = self._check_gitee()
            self.finished.emit(update_info)
        except Exception as e:
            self.error.emit(str(e))

    def _check_gitee(self) -> Optional[UpdateInfo]:
        ctx = ssl.create_default_context()

        request = urllib.request.Request(
            GITEE_RELEASES_URL,
            headers={'Accept': 'application/json'}
        )

        with urllib.request.urlopen(request, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))

        if not data:
            return None

        release = UpdateInfo(data)

        if release.draft or release.prerelease:
            return None

        current = self.version_manager.get_current_version()
        latest = Version(release.version)

        if latest > current:
            return release

        return None


class DownloadThread(QThread):
    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url: str, save_path: str, expected_size: int = 0):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.expected_size = expected_size
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            temp_path = self.save_path + '.downloading'
            downloaded = 0

            if os.path.exists(temp_path):
                downloaded = os.path.getsize(temp_path)

            ctx = ssl.create_default_context()

            request = urllib.request.Request(self.url)
            if downloaded > 0:
                request.add_header('Range', f'bytes={downloaded}-')

            with urllib.request.urlopen(request, timeout=30, context=ctx) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                if downloaded > 0 and response.status == 206:
                    total_size += downloaded
                elif total_size == 0:
                    total_size = self.expected_size

                mode = 'ab' if downloaded > 0 else 'wb'
                with open(temp_path, mode) as f:
                    while True:
                        if self._is_cancelled:
                            return

                        chunk = response.read(8192)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            self.progress.emit(downloaded, total_size)

            if not self._is_cancelled:
                if os.path.exists(self.save_path):
                    os.remove(self.save_path)
                shutil.move(temp_path, self.save_path)
                self.finished.emit(self.save_path)

        except Exception as e:
            self.error.emit(str(e))


class BackupManager:
    def __init__(self, backup_dir: str = None):
        if backup_dir is None:
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            backup_dir = os.path.join(app_data, 'MedicineSystem', 'backups')

        self.backup_dir = backup_dir
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self, db_path: str, config_path: str = None) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_subdir = os.path.join(self.backup_dir, f'backup_{timestamp}')
        os.makedirs(backup_subdir)

        if os.path.exists(db_path):
            db_backup = os.path.join(backup_subdir, os.path.basename(db_path))
            shutil.copy2(db_path, db_backup)

        if config_path and os.path.exists(config_path):
            config_backup = os.path.join(backup_subdir, os.path.basename(config_path))
            shutil.copy2(config_path, config_backup)

        manifest = {
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'files': []
        }

        for f in os.listdir(backup_subdir):
            filepath = os.path.join(backup_subdir, f)
            manifest['files'].append({
                'name': f,
                'size': os.path.getsize(filepath),
                'checksum': self._calc_md5(filepath)
            })

        manifest_path = os.path.join(backup_subdir, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        return backup_subdir

    def restore_backup(self, backup_path: str, db_path: str, config_path: str = None) -> bool:
        try:
            manifest_path = os.path.join(backup_path, 'manifest.json')
            if not os.path.exists(manifest_path):
                return False

            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            for file_info in manifest.get('files', []):
                src = os.path.join(backup_path, file_info['name'])
                if not os.path.exists(src):
                    continue

                if file_info['name'].endswith('.db'):
                    shutil.copy2(src, db_path)
                elif config_path and file_info['name'].endswith('.json'):
                    shutil.copy2(src, config_path)

            return True
        except Exception:
            return False

    def list_backups(self) -> list:
        backups = []
        if not os.path.exists(self.backup_dir):
            return backups

        for name in os.listdir(self.backup_dir):
            path = os.path.join(self.backup_dir, name)
            if os.path.isdir(path) and name.startswith('backup_'):
                manifest_path = os.path.join(path, 'manifest.json')
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        backups.append({
                            'path': path,
                            'timestamp': manifest.get('timestamp', ''),
                            'created_at': manifest.get('created_at', ''),
                            'file_count': len(manifest.get('files', []))
                        })
                    except Exception:
                        pass

        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

    def cleanup_old_backups(self, keep_count: int = 5):
        backups = self.list_backups()
        for backup in backups[keep_count:]:
            try:
                shutil.rmtree(backup['path'])
            except Exception:
                pass

    def _calc_md5(self, filepath: str) -> str:
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


class UpdateManager:
    def __init__(self, version_manager: VersionManager = None):
        self.version_manager = version_manager or VersionManager()
        self.backup_manager = BackupManager()
        self._check_thread = None
        self._download_thread = None

    def check_update(self, callback: Callable, error_callback: Callable):
        self._check_thread = CheckUpdateThread(self.version_manager)
        self._check_thread.finished.connect(callback)
        self._check_thread.error.connect(error_callback)
        self._check_thread.start()

    def download_update(self, update_info: UpdateInfo,
                       progress_callback: Callable,
                       finished_callback: Callable,
                       error_callback: Callable) -> str:
        url = update_info.get_download_url()
        if not url:
            error_callback("无法获取下载地址")
            return ""

        download_dir = self.version_manager.get_download_dir()
        filename = f"medicine_system_{update_info.version}.exe"
        save_path = os.path.join(download_dir, filename)

        self._download_thread = DownloadThread(
            url, save_path, update_info.get_file_size()
        )
        self._download_thread.progress.connect(progress_callback)
        self._download_thread.finished.connect(finished_callback)
        self._download_thread.error.connect(error_callback)
        self._download_thread.start()

        return save_path

    def cancel_download(self):
        if self._download_thread and self._download_thread.isRunning():
            self._download_thread.cancel()
            self._download_thread.wait()

    def create_pre_update_backup(self, db_path: str) -> str:
        return self.backup_manager.create_backup(db_path)
