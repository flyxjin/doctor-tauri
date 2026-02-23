import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QCheckBox,
                             QFrame, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from utils.version import CURRENT_VERSION, VersionManager
from utils.updater import UpdateInfo, UpdateManager, BackupManager


class UpdateDialog(QDialog):
    def __init__(self, parent=None, update_info: UpdateInfo = None, 
                 version_manager: VersionManager = None):
        super().__init__(parent)
        self.update_info = update_info
        self.version_manager = version_manager or VersionManager()
        self.update_manager = UpdateManager(self.version_manager)
        self._download_path = ""
        
        self.setWindowTitle('软件更新')
        self.setMinimumSize(480, 380)
        self.setModal(True)
        self.init_ui()
        
        if update_info:
            self._display_update_info()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        self.status_indicator = QFrame()
        self.status_indicator.setObjectName('status_indicator')
        self.status_indicator.setFixedSize(48, 48)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        self.title_label = QLabel("检查更新")
        self.title_label.setObjectName('dialog_title')
        
        self.version_label = QLabel(f"当前版本: v{CURRENT_VERSION}")
        self.version_label.setObjectName('dialog_subtitle')
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.version_label)
        
        header_layout.addWidget(self.status_indicator)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.content_frame = QFrame()
        self.content_frame.setObjectName('content_frame')
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setSpacing(8)
        
        self.new_version_label = QLabel()
        self.new_version_label.setObjectName('new_version_label')
        self.new_version_label.setVisible(False)
        
        self.size_label = QLabel()
        self.size_label.setObjectName('size_label')
        self.size_label.setVisible(False)
        
        self.changelog_group = QGroupBox("更新内容")
        self.changelog_group.setObjectName('changelog_group')
        changelog_layout = QVBoxLayout(self.changelog_group)
        
        self.changelog_text = QTextEdit()
        self.changelog_text.setReadOnly(True)
        self.changelog_text.setMaximumHeight(120)
        self.changelog_text.setObjectName('changelog_text')
        changelog_layout.addWidget(self.changelog_text)
        
        self.content_layout.addWidget(self.new_version_label)
        self.content_layout.addWidget(self.size_label)
        self.content_layout.addWidget(self.changelog_group)
        
        layout.addWidget(self.content_frame)
        
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setSpacing(8)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setObjectName('download_progress')
        
        self.progress_label = QLabel("准备下载...")
        self.progress_label.setObjectName('progress_label')
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        self.progress_frame.setVisible(False)
        layout.addWidget(self.progress_frame)
        
        self.skip_checkbox = QCheckBox("跳过此版本")
        self.skip_checkbox.setObjectName('skip_checkbox')
        layout.addWidget(self.skip_checkbox)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.later_btn = QPushButton("稍后提醒")
        self.later_btn.setObjectName('secondary_btn')
        self.later_btn.clicked.connect(self._on_later)
        
        self.action_btn = QPushButton("立即更新")
        self.action_btn.setObjectName('primary_btn')
        self.action_btn.clicked.connect(self._on_action)
        
        btn_layout.addWidget(self.later_btn)
        btn_layout.addWidget(self.action_btn)
        
        layout.addLayout(btn_layout)
        
        self._apply_styles()
    
    def _apply_styles(self):
        self.setStyleSheet('''
            QDialog {
                background-color: #ffffff;
            }
            QFrame#status_indicator {
                background-color: #1890ff;
                border-radius: 24px;
            }
            QFrame#content_frame {
                background-color: #fafafa;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 12px;
            }
            QLabel#dialog_title {
                font-size: 18px;
                font-weight: 500;
                color: #262626;
            }
            QLabel#dialog_subtitle {
                font-size: 13px;
                color: #8c8c8c;
            }
            QLabel#new_version_label {
                font-size: 15px;
                font-weight: 500;
                color: #1890ff;
            }
            QLabel#size_label {
                font-size: 13px;
                color: #595959;
            }
            QGroupBox#changelog_group {
                font-weight: 500;
                color: #262626;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox#changelog_group::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QTextEdit#changelog_text {
                background-color: #ffffff;
                border: none;
                font-size: 13px;
                color: #595959;
            }
            QProgressBar#download_progress {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: #f5f5f5;
            }
            QProgressBar#download_progress::chunk {
                background-color: #1890ff;
                border-radius: 3px;
            }
            QLabel#progress_label {
                font-size: 12px;
                color: #8c8c8c;
            }
            QCheckBox#skip_checkbox {
                font-size: 13px;
                color: #595959;
            }
            QPushButton#primary_btn {
                background-color: #1890ff;
                color: #ffffff;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 90px;
            }
            QPushButton#primary_btn:hover {
                background-color: #40a9ff;
            }
            QPushButton#primary_btn:disabled {
                background-color: #d9d9d9;
                color: #8c8c8c;
            }
            QPushButton#secondary_btn {
                background-color: #ffffff;
                color: #595959;
                border: 1px solid #d9d9d9;
                padding: 8px 24px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 90px;
            }
            QPushButton#secondary_btn:hover {
                border-color: #1890ff;
                color: #1890ff;
            }
        ''')
    
    def _display_update_info(self):
        if not self.update_info:
            return
        
        self.title_label.setText("发现新版本")
        self.status_indicator.setStyleSheet('''
            QFrame#status_indicator {
                background-color: #52c41a;
                border-radius: 24px;
            }
        ''')
        
        self.new_version_label.setText(f"最新版本: v{self.update_info.version}")
        self.new_version_label.setVisible(True)
        
        size = self.update_info.get_file_size_display()
        self.size_label.setText(f"文件大小: {size}")
        self.size_label.setVisible(True)
        
        changelog = self.update_info.body or "暂无更新说明"
        self.changelog_text.setPlainText(changelog)
        
        self.action_btn.setEnabled(True)
        self.later_btn.setText("稍后提醒")
    
    def show_no_update(self):
        self.title_label.setText("已是最新版本")
        self.status_indicator.setStyleSheet('''
            QFrame#status_indicator {
                background-color: #52c41a;
                border-radius: 24px;
            }
        ''')
        
        self.content_frame.setVisible(False)
        self.skip_checkbox.setVisible(False)
        
        self.action_btn.setText("确定")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.accept)
        
        self.later_btn.setVisible(False)
    
    def show_error(self, error_msg: str):
        self.title_label.setText("检查更新失败")
        self.status_indicator.setStyleSheet('''
            QFrame#status_indicator {
                background-color: #ff4d4f;
                border-radius: 24px;
            }
        ''')
        
        self.content_frame.setVisible(False)
        self.skip_checkbox.setVisible(False)
        
        self.action_btn.setText("确定")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.accept)
        
        self.later_btn.setVisible(False)
    
    def _on_later(self):
        if self.skip_checkbox.isChecked() and self.update_info:
            self.version_manager.skip_version(self.update_info.version)
        self.reject()
    
    def _on_action(self):
        if not self.update_info:
            return
        
        if self._download_path and os.path.exists(self._download_path):
            self._install_update()
            return
        
        self._start_download()
    
    def _start_download(self):
        self.action_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.skip_checkbox.setEnabled(False)
        self.progress_frame.setVisible(True)
        
        self.update_manager.download_update(
            self.update_info,
            self._on_download_progress,
            self._on_download_finished,
            self._on_download_error
        )
    
    def _on_download_progress(self, downloaded: int, total: int):
        if total > 0:
            percent = int(downloaded / total * 100)
            self.progress_bar.setValue(percent)
            
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.progress_label.setText(f"正在下载: {downloaded_mb:.1f}MB / {total_mb:.1f}MB")
    
    def _on_download_finished(self, path: str):
        self._download_path = path
        self.progress_label.setText("下载完成")
        self.action_btn.setEnabled(True)
        self.action_btn.setText("立即安装")
        
        self.version_manager.record_check_time()
    
    def _on_download_error(self, error: str):
        self.progress_label.setText(f"下载失败: {error}")
        self.action_btn.setEnabled(True)
        self.action_btn.setText("重试")
        self.later_btn.setEnabled(True)
    
    def _install_update(self):
        if not self._download_path or not os.path.exists(self._download_path):
            QMessageBox.warning(self, "错误", "更新文件不存在")
            return
        
        db_path = self._get_db_path()
        if db_path and os.path.exists(db_path):
            try:
                backup_manager = BackupManager()
                backup_path = backup_manager.create_backup(db_path)
                backup_manager.cleanup_old_backups(3)
            except:
                pass
        
        reply = QMessageBox.question(
            self, '确认安装',
            '更新程序将关闭当前程序并启动安装程序。\n确定要继续吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            import subprocess
            import sys
            
            try:
                if os.name == 'nt':
                    os.startfile(self._download_path)
                else:
                    subprocess.Popen([self._download_path])
                
                if self.parent():
                    self.parent().close()
                else:
                    sys.exit(0)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"启动安装程序失败: {e}")
    
    def _get_db_path(self) -> str:
        if self.parent() and hasattr(self.parent(), 'db'):
            db = self.parent().db
            if hasattr(db, 'db_path'):
                return db.db_path
        
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(exe_dir, 'medicine_system.db')
    
    def closeEvent(self, event):
        if self.update_manager._download_thread and self.update_manager._download_thread.isRunning():
            self.update_manager.cancel_download()
        event.accept()
