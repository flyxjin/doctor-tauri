# -*- coding: utf-8 -*-
"""
中药材销售管理系统 - Windows 7兼容版本
主入口文件（已优化重构）

模块化结构:
- widgets/sidebar.py: 侧边栏组件
- widgets/import_dialog.py: 导入对话框
- utils/modern_design.py: 现代设计系统
- views/: 各视图模块

现代UI设计系统风格
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QEvent
from PyQt5.QtGui import QFont, QFontDatabase

from core import Database, BuiltinDataLoader, get_app_logger
from views.medicine_view import MedicineView
from views.prescription_view import PrescriptionView
from views.inventory_view import InventoryView
from views.history_view import HistoryView
from views.dashboard_view import DashboardView
from views.prescription_template_view import PrescriptionTemplateView
from views.patient_view import PatientView
from views.print_template_view import PrintTemplateView
from widgets.page_header import PageHeader
from widgets.update_dialog import UpdateDialog
from widgets.import_dialog import ImportDialog
from widgets.sidebar import SidebarWidget
from utils.responsive_font import get_font_manager
from utils.version import CURRENT_VERSION, VERSION_DATE, VersionManager
from utils.updater import UpdateManager, UpdateInfo
from utils.style import UIStyles

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.logger = get_app_logger()
        self.logger.info("应用程序启动")

        self.db = Database()
        BuiltinDataLoader(self.db).ensure_data_loaded()

        self.font_manager = get_font_manager()
        self.version_manager = VersionManager()
        self.update_manager = UpdateManager(self.version_manager)
        self.font_manager.font_changed.connect(self._on_font_changed)
        self._resize_timer = None
        self._last_window_state = self.windowState()

        self.init_ui()
        self._check_update_on_startup()

    def init_ui(self):
        self.setWindowTitle('中药材销售管理系统')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        self._create_menu_bar()
        self._create_status_bar()

        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {UIStyles.COLORS['bg_main']};")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_sidebar(main_layout)
        self._create_content_area(main_layout)
        self._apply_styles()

        self.sidebar.set_current_nav('dashboard')
        self.stacked_widget.setCurrentIndex(0)
        self.font_manager.update_for_window_size(self.width())

    def _create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(UIStyles.get_main_stylesheet())

        file_menu = menubar.addMenu('文件')
        
        from PyQt5.QtWidgets import QAction
        export_action = QAction('导出数据', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tool_menu = menubar.addMenu('工具')
        import_action = QAction('批量导入药材', self)
        import_action.triggered.connect(self.show_import_dialog)
        tool_menu.addAction(import_action)
        tool_menu.addSeparator()
        
        backup_action = QAction('数据备份', self)
        backup_action.triggered.connect(self._backup_data)
        tool_menu.addAction(backup_action)

        help_menu = menubar.addMenu('帮助')
        update_action = QAction('检查更新', self)
        update_action.triggered.connect(self._check_update_manual)
        help_menu.addAction(update_action)
        help_menu.addSeparator()
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        from PyQt5.QtWidgets import QStatusBar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(UIStyles.get_main_stylesheet())
        self.status_bar.showMessage('就绪')

    def _create_sidebar(self, main_layout):
        self.sidebar = SidebarWidget(version_text=f'v{CURRENT_VERSION}')
        self.sidebar.nav_clicked.connect(self.switch_view)
        self.sidebar.set_fixed_width(220)
        main_layout.addWidget(self.sidebar)

    def _create_content_area(self, main_layout):
        content_area = QFrame()
        content_area.setObjectName('content_area')
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        self.page_header = PageHeader('dashboard')
        content_layout.addWidget(self.page_header)

        self.stacked_widget = QStackedWidget()

        self.dashboard_view = DashboardView(self.db)
        self.medicine_view = MedicineView(self.db)
        self.prescription_view = PrescriptionView(self.db)
        self.inventory_view = InventoryView(self.db)
        self.history_view = HistoryView(self.db)
        self.template_view = PrescriptionTemplateView(self.db)
        self.patient_view = PatientView(self.db)
        self.print_view = PrintTemplateView(self.db)

        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.medicine_view)
        self.stacked_widget.addWidget(self.prescription_view)
        self.stacked_widget.addWidget(self.inventory_view)
        self.stacked_widget.addWidget(self.history_view)
        self.stacked_widget.addWidget(self.template_view)
        self.stacked_widget.addWidget(self.patient_view)
        self.stacked_widget.addWidget(self.print_view)

        self.stacked_widget.currentChanged.connect(self._on_view_changed)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_area)

    def _apply_styles(self):
        self.setStyleSheet(UIStyles.get_main_stylesheet())
        
    def _on_view_changed(self, index):
        view_names = ['dashboard', 'medicine', 'prescription', 'inventory', 
                     'history', 'template', 'patient', 'print']
        if index < len(view_names):
            self.page_header.update_title(view_names[index])

    def _on_font_changed(self, preset, base_size):
        self._apply_styles()
        for view in [self.medicine_view, self.inventory_view, self.prescription_view, 
                     self.history_view, self.dashboard_view, self.template_view,
                     self.patient_view, self.print_view]:
            if hasattr(view, 'update_fonts'):
                view.update_fonts()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._resize_timer is not None:
            self.killTimer(self._resize_timer)
        self._resize_timer = self.startTimer(150)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            current_state = self.windowState()
            if current_state != self._last_window_state:
                self._last_window_state = current_state
                if current_state & Qt.WindowFullScreen or current_state & Qt.WindowMaximized:
                    self.font_manager.update_for_window_size(9999)
                    self._apply_styles()

    def timerEvent(self, event):
        self.killTimer(self._resize_timer)
        self._resize_timer = None
        new_width = self.width()
        old_base_size = self.font_manager.current_base_size
        self.font_manager.update_for_window_size(new_width)
        if self.font_manager.current_base_size != old_base_size:
            self._apply_styles()
        if hasattr(self.sidebar, 'update_for_window_size'):
            self.sidebar.update_for_window_size(new_width)

    def _check_update_on_startup(self):
        if self.version_manager.should_check_update():
            QTimer.singleShot(2000, self._check_update_silent)

    def _check_update_silent(self):
        self.update_manager.check_update(
            self._on_update_found,
            self._on_update_error
        )

    def _check_update_manual(self):
        self.status_bar.showMessage('正在检查更新...')
        self.update_manager.check_update(
            self._on_update_found_manual,
            self._on_update_error_manual
        )

    def _on_update_found(self, update_info):
        if update_info:
            if not self.version_manager.is_version_skipped(update_info.version):
                dialog = UpdateDialog(self, update_info, self.version_manager)
                dialog.exec_()
        self.version_manager.record_check_time()

    def _on_update_error(self, error):
        pass

    def _on_update_found_manual(self, update_info):
        self.status_bar.clearMessage()
        if update_info:
            dialog = UpdateDialog(self, update_info, self.version_manager)
            dialog.exec_()
        else:
            dialog = UpdateDialog(self, None, self.version_manager)
            dialog.show_no_update()
            dialog.exec_()
        self.version_manager.record_check_time()

    def _on_update_error_manual(self, error):
        self.status_bar.clearMessage()
        dialog = UpdateDialog(self, None, self.version_manager)
        dialog.show_error(error)
        dialog.exec_()

    def show_import_dialog(self):
        dialog = ImportDialog(self, self.db)
        dialog.exec_()
        self.medicine_view.load_data()
        self.inventory_view.refresh_data()
        self.dashboard_view.load_statistics()

    def switch_view(self, name):
        view_map = {
            'dashboard': 0,
            'medicine': 1,
            'prescription': 2,
            'inventory': 3,
            'history': 4,
            'template': 5,
            'patient': 6,
            'print': 7
        }
        index = view_map.get(name, 0)
        self.stacked_widget.setCurrentIndex(index)
        self.page_header.set_page(name)
        self.sidebar.set_current_nav(name)

        if name == 'inventory':
            self.inventory_view.refresh_data()
        elif name == 'history':
            self.history_view.refresh_data()
        elif name == 'dashboard':
            self.dashboard_view.load_statistics()
        elif name == 'template':
            self.template_view.load_data()
        elif name == 'patient':
            self.patient_view.load_data()

        view_names = {
            'dashboard': '数据统计',
            'medicine': '药材管理',
            'prescription': '开处方',
            'inventory': '库存管理',
            'history': '处方历史',
            'template': '处方模板',
            'patient': '患者管理',
            'print': '打印设置'
        }
        self.status_bar.showMessage(view_names.get(name, ''))

    def _export_data(self):
        self.status_bar.showMessage('正在导出数据...')
        try:
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(self, '导出数据', 'medicines_export.csv', 'CSV文件 (*.csv)')
            if file_path:
                self._do_export(file_path)
                self.status_bar.showMessage('导出完成')
        except Exception as e:
            QMessageBox.warning(self, '导出失败', str(e))
            self.status_bar.clearMessage()

    def _do_export(self, file_path):
        import csv
        medicines = self.db.fetchall("SELECT * FROM medicines")
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['名称', '别名', '分类', '药性', '药味', '归经', '功效', '主治', '用法', '用量', '禁忌', '备注'])
            for m in medicines:
                writer.writerow(m[1:])

    def _backup_data(self):
        try:
            backup_path = self.db.backup()
            self.logger.info(f"数据备份完成: {backup_path}")
            QMessageBox.information(self, '备份完成', f'数据已备份到:\n{backup_path}')
        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            QMessageBox.warning(self, '备份失败', str(e))

    def _show_about(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle('关于')
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        title_label = QLabel('中药材销售管理系统')
        title_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #1890ff;')
        title_label.setAlignment(Qt.AlignCenter)
        
        version_label = QLabel(f'版本: {CURRENT_VERSION}')
        version_label.setStyleSheet('font-size: 14px;')
        version_label.setAlignment(Qt.AlignCenter)
        
        date_label = QLabel(f'发布日期: {VERSION_DATE}')
        date_label.setStyleSheet('font-size: 12px; color: #666;')
        date_label.setAlignment(Qt.AlignCenter)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet('background-color: #e0e0e0;')
        
        desc_label = QLabel(
            '一款专业的中药材信息管理系统\n\n'
            '主要功能:\n'
            '• 药材信息管理\n'
            '• 处方开具与管理\n'
            '• 库存监控与调配\n'
            '• 患者信息管理\n'
            '• 数据统计与分析'
        )
        desc_label.setStyleSheet('font-size: 13px; line-height: 1.6;')
        desc_label.setAlignment(Qt.AlignCenter)
        
        copyright_label = QLabel('© 2026 TCM System')
        copyright_label.setStyleSheet('font-size: 11px; color: #999;')
        copyright_label.setAlignment(Qt.AlignCenter)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(date_label)
        layout.addWidget(separator)
        layout.addWidget(desc_label)
        layout.addWidget(copyright_label)
        layout.addWidget(button_box)
        
        dialog.exec_()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出确认', '确定要退出程序吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logger.info("应用程序关闭")
            self.db.close()
            event.accept()
        else:
            event.ignore()


def main():
    # 全局异常处理 - 捕获未处理的异常防止闪退
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        import traceback
        logger = get_app_logger()
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"未捕获的异常:\n{error_msg}")
        
        # 显示错误对话框
        try:
            from PyQt5.QtWidgets import QMessageBox
            app = QApplication.instance()
            if app:
                msg_box = QMessageBox()
                msg_box.setWindowTitle('程序错误')
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setText('程序发生了一个错误')
                msg_box.setDetailedText(error_msg)
                msg_box.exec_()
        except:
            pass
    
    sys.excepthook = global_exception_handler

    # 设置 Qt 异常处理
    def qt_exception_handler(message):
        logger = get_app_logger()
        logger.error(f"Qt 异常: {message}")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 安装 Qt 消息处理器
    from PyQt5.QtCore import qInstallMessageHandler
    def qt_message_handler(msg_type, context, message):
        logger = get_app_logger()
        level = {0: 'INFO', 1: 'WARNING', 2: 'CRITICAL', 3: 'FATAL'}
        logger.error(f"Qt Message [{level.get(msg_type, 'UNKNOWN')}]: {message}")
    qInstallMessageHandler(qt_message_handler)

    font_manager = get_font_manager()
    font_name = "Segoe UI"
    font_db = QFontDatabase()
    font_families = font_db.families()
    if font_name not in font_families:
        font_name = "Microsoft YaHei"
        if font_name not in font_families:
            font_name = "SimSun"

    font = QFont(font_name, font_manager.current_base_size)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
