import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from core import BuiltinDataLoader, Database, PatientService, get_app_logger
from core.theme import AppColors, get_button_style, get_main_window_style
from utils.responsive_font import get_font_manager
from utils.shortcuts import ShortcutManager, get_shortcut_help_text
from utils.updater import UpdateManager
from utils.version import CURRENT_VERSION, VERSION_DATE, VersionManager
from views.batch_import_view import BatchImportView
from views.dashboard_view import DashboardView
from views.history_view import HistoryView
from views.inventory_view import InventoryView
from views.medicine_view import MedicineView
from views.patient_view import PatientView
from views.prescription_view import PrescriptionView
from views.statistics_view import StatisticsView
from widgets.page_header import PageHeader
from widgets.update_dialog import UpdateDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = get_app_logger()
        self.logger.info("应用程序启动")

        self.db = Database()

        data_loader = BuiltinDataLoader(self.db)
        data_loader.ensure_data_loaded()

        self.font_manager = get_font_manager()
        self.version_manager = VersionManager()
        self.update_manager = UpdateManager(self.version_manager)
        self.font_manager.font_changed.connect(self._on_font_changed)
        self._resize_timer = None
        self._last_window_state = None
        self.init_ui()
        self._setup_shortcuts()
        self._check_update_on_startup()

    def _setup_shortcuts(self):
        """初始化全局快捷键系统"""
        self._shortcut_manager = ShortcutManager(self)
        self._shortcut_manager.switch_view_requested.connect(self.switch_view)
        self._shortcut_manager.refresh_requested.connect(self._refresh_current_view)
        self._shortcut_manager.search_focus_requested.connect(self._focus_search)
        self._shortcut_manager.add_requested.connect(self._add_current)
        self._shortcut_manager.save_requested.connect(self._save_current)
        self._shortcut_manager.import_requested.connect(self.show_import_dialog)
        self._shortcut_manager.export_requested.connect(self._export_data)
        self._shortcut_manager.about_requested.connect(self._show_about)

    def _refresh_current_view(self):
        """刷新当前显示的页面"""
        view_name = self._shortcut_manager.get_current_view_name()
        if view_name == 'dashboard':
            self.dashboard_view.refresh_data()
        elif view_name == 'medicine':
            self.medicine_view.load_data()
        elif view_name == 'inventory':
            self.inventory_view.refresh_data()
        elif view_name == 'history':
            self.history_view.refresh_data()
        elif view_name == 'statistics':
            self.statistics_view.refresh_data()
        elif view_name == 'patient':
            self.patient_view.load_data()
        self.status_bar.showMessage(f'已刷新{self._current_view_title(view_name)}', 2000)

    def _focus_search(self):
        """聚焦当前页面的搜索框"""
        view_name = self._shortcut_manager.get_current_view_name()
        search_input = None
        if view_name == 'medicine':
            search_input = getattr(self.medicine_view, 'search_input', None)
        elif view_name == 'prescription':
            search_input = getattr(self.prescription_view, 'search_input', None)
        elif view_name == 'history':
            search_input = getattr(self.history_view, 'name_search', None)
        elif view_name == 'patient':
            search_input = getattr(self.patient_view, 'search_input', None)
        if search_input is not None:
            search_input.setFocus()
            search_input.selectAll()

    def _add_current(self):
        """当前页面的新增操作"""
        view_name = self._shortcut_manager.get_current_view_name()
        if view_name == 'medicine':
            self.medicine_view.add_medicine()
        elif view_name == 'prescription':
            self.prescription_view.save_prescription()
        elif view_name == 'patient':
            self.patient_view.add_patient()

    def _save_current(self):
        """保存操作（处方页面保存处方）"""
        view_name = self._shortcut_manager.get_current_view_name()
        if view_name == 'prescription':
            self.prescription_view.save_prescription()

    def _current_view_title(self, view_name: str) -> str:
        titles = {
            'dashboard': '首页概览', 'medicine': '药材管理',
            'prescription': '开处方', 'inventory': '库存管理',
            'history': '处方历史', 'statistics': '销售统计',
            'patient': '客户管理',
        }
        return titles.get(view_name, '')

    def init_ui(self):
        self.setWindowTitle('中药材销售管理系统')
        self.setGeometry(100, 100, 1400, 900)
        # 提高最小尺寸，避免内容密集的商务界面在小窗口下被裁剪
        self.setMinimumSize(1024, 720)

        self._create_menu_bar()
        self._create_status_bar()
        self._apply_responsive_styles()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_sidebar(main_layout)
        self._create_content_area(main_layout)

        self.nav_buttons[0].setChecked(True)
        self.stacked_widget.setCurrentIndex(0)

        self.font_manager.update_for_window_size(self.width())

    def _create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('文件')

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

        shortcut_action = QAction('快捷键说明', self)
        shortcut_action.setShortcut('F1')
        shortcut_action.triggered.connect(self._show_about)
        help_menu.addAction(shortcut_action)

        help_menu.addSeparator()

        about_action = QAction('关于', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')

    def _create_sidebar(self, main_layout):
        self.sidebar = QFrame()
        self.sidebar.setObjectName('sidebar')
        self._update_sidebar_width(1400)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(8, 18, 8, 18)
        sidebar_layout.setSpacing(8)

        brand_container = QWidget()
        brand_container.setObjectName('brand_container')
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(6, 16, 6, 20)
        brand_layout.setSpacing(4)

        self.brand_title = QLabel('中药材管理系统')
        self.brand_title.setObjectName('brand_title')
        self.brand_title.setAlignment(Qt.AlignCenter)
        self.brand_title.setMinimumHeight(28)
        self.brand_title.setWordWrap(True)

        self.brand_subtitle = QLabel('专业中医药信息平台')
        self.brand_subtitle.setObjectName('brand_subtitle')
        self.brand_subtitle.setAlignment(Qt.AlignCenter)
        self.brand_subtitle.setMinimumHeight(20)
        self.brand_subtitle.setWordWrap(True)

        brand_layout.addWidget(self.brand_title)
        brand_layout.addWidget(self.brand_subtitle)

        sidebar_layout.addWidget(brand_container)

        separator = QFrame()
        separator.setObjectName('sidebar_separator')
        separator.setFixedHeight(1)
        sidebar_layout.addWidget(separator)

        self.nav_buttons = []
        nav_items = [
            ('首页概览', 'dashboard'),
            ('药材管理', 'medicine'),
            ('开处方', 'prescription'),
            ('客户管理', 'patient'),
            ('库存管理', 'inventory'),
            ('处方历史', 'history'),
            ('销售统计', 'statistics')
        ]

        for text, name in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName('nav_btn')
            btn.clicked.connect(lambda checked, n=name: self.switch_view(n))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        self.import_btn = QPushButton('批量导入药材')
        self.import_btn.setObjectName('import_btn')
        self.import_btn.clicked.connect(self.show_import_dialog)
        sidebar_layout.addWidget(self.import_btn)

        self.version_label = QLabel(f'v{CURRENT_VERSION}')
        self.version_label.setObjectName('version_label')
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setMinimumHeight(24)
        sidebar_layout.addWidget(self.version_label)

        main_layout.addWidget(self.sidebar)

    def _create_content_area(self, main_layout):
        content_area = QFrame()
        content_area.setObjectName('content_area')
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        self.page_header = PageHeader('dashboard')
        content_layout.addWidget(self.page_header)

        self.stacked_widget = QStackedWidget()

        self.dashboard_view = DashboardView(self.db)
        self.medicine_view = MedicineView(self.db)
        self._patient_service = PatientService(self.db)
        self.prescription_view = PrescriptionView(self.db, patient_service=self._patient_service)
        self.patient_view = PatientView(self.db, patient_service=self._patient_service)
        self.inventory_view = InventoryView(self.db)
        self.history_view = HistoryView(self.db)
        self.statistics_view = StatisticsView(self.db)

        # 为各 view 设置最小宽度，避免小窗口下卡片/表格被挤压到无法阅读
        for view in (self.dashboard_view, self.medicine_view, self.prescription_view,
                     self.patient_view, self.inventory_view, self.history_view,
                     self.statistics_view):
            view.setMinimumWidth(760)

        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.medicine_view)
        self.stacked_widget.addWidget(self.prescription_view)
        self.stacked_widget.addWidget(self.patient_view)
        self.stacked_widget.addWidget(self.inventory_view)
        self.stacked_widget.addWidget(self.history_view)
        self.stacked_widget.addWidget(self.statistics_view)

        content_layout.addWidget(self.stacked_widget)

        main_layout.addWidget(content_area)

    def _apply_responsive_styles(self):
        base_size = self.font_manager.current_base_size
        new_style = get_main_window_style(base_size)
        # 只有样式表真的变化时才重新设置，避免重复触发重绘
        if self.styleSheet() != new_style:
            self.setStyleSheet(new_style)

    def _get_sidebar_width(self, window_width):
        if window_width < 1100:
            return 180
        elif window_width < 1300:
            return 200
        elif window_width < 1600:
            return 220
        else:
            return 260

    def _update_sidebar_width(self, window_width):
        width = self._get_sidebar_width(window_width)
        self.sidebar.setFixedWidth(width)

    def _on_font_changed(self, preset, base_size):
        self._apply_responsive_styles()
        self._update_sidebar_width(self.width())

        if hasattr(self.page_header, 'update_fonts'):
            self.page_header.update_fonts()

        if hasattr(self.dashboard_view, 'update_fonts'):
            self.dashboard_view.update_fonts()
        if hasattr(self.medicine_view, 'update_fonts'):
            self.medicine_view.update_fonts()
        if hasattr(self.inventory_view, 'update_fonts'):
            self.inventory_view.update_fonts()
        if hasattr(self.prescription_view, 'update_fonts'):
            self.prescription_view.update_fonts()
        if hasattr(self.patient_view, 'update_fonts'):
            self.patient_view.update_fonts()
        if hasattr(self.history_view, 'update_fonts'):
            self.history_view.update_fonts()
        if hasattr(self.statistics_view, 'update_fonts'):
            self.statistics_view.update_fonts()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self._resize_timer is not None:
            self.killTimer(self._resize_timer)

        self._resize_timer = self.startTimer(150)

    def changeEvent(self, event):
        super().changeEvent(event)

        if event.type() == event.Type.WindowStateChange:
            current_state = self.windowState()
            if current_state != self._last_window_state:
                self._last_window_state = current_state

                if current_state & Qt.WindowFullScreen or current_state & Qt.WindowMaximized:
                    self.font_manager.update_for_window_size(9999)
                else:
                    self.font_manager.update_for_window_size(self.width())
                self._apply_responsive_styles()
                QApplication.processEvents()

    def timerEvent(self, event):
        self.killTimer(self._resize_timer)
        self._resize_timer = None

        self.font_manager.update_for_window_size(self.width())

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
                dialog.exec()
        self.version_manager.record_check_time()

    def _on_update_error(self, error):
        pass

    def _on_update_found_manual(self, update_info):
        self.status_bar.clearMessage()
        if update_info:
            dialog = UpdateDialog(self, update_info, self.version_manager)
            dialog.exec()
        else:
            dialog = UpdateDialog(self, None, self.version_manager)
            dialog.show_no_update()
            dialog.exec()
        self.version_manager.record_check_time()

    def _on_update_error_manual(self, error):
        self.status_bar.clearMessage()
        dialog = UpdateDialog(self, None, self.version_manager)
        dialog.show_error(error)
        dialog.exec()

    def show_import_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('批量导入药材数据')
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)

        import_widget = BatchImportView(self.db, dialog)
        layout.addWidget(import_widget)

        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet(get_button_style(AppColors.INFO, padding='10px 30px'))
        close_btn.clicked.connect(dialog.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.exec()
        # 批量导入绕过 Service 层直接写数据库，需手动失效并重建缓存
        from core.cache import invalidate_medicine_cache
        invalidate_medicine_cache()
        if hasattr(self.medicine_view, '_init_cache'):
            self.medicine_view._init_cache()
        self.medicine_view.load_data()
        self.inventory_view.refresh_data()

    def _export_data(self):
        self.status_bar.showMessage('正在导出数据...')
        try:
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, '导出数据', 'medicines_export.csv', 'CSV文件 (*.csv)'
            )
            if file_path:
                self._do_export(file_path)
                self.status_bar.showMessage('导出完成')
        except Exception as e:
            QMessageBox.warning(self, '导出失败', str(e))
            self.status_bar.clearMessage()

    def _do_export(self, file_path):
        import csv
        medicines = self.db.fetchall("SELECT * FROM medicines")
        cols = ['name', 'alias', 'category', 'nature', 'taste', 'meridian',
                'efficacy', 'indications', 'usage', 'dosage', 'contraindication', 'notes']
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['名称', '别名', '分类', '药性', '药味', '归经', '功效', '主治', '用法', '用量', '禁忌', '备注'])
            for m in medicines:
                writer.writerow([m.get(c, '') for c in cols])

    def _backup_data(self):
        try:
            backup_path = self.db.backup()
            self.logger.info(f"数据备份完成: {backup_path}")
            QMessageBox.information(self, '备份完成', f'数据已备份到:\n{backup_path}')
        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            QMessageBox.warning(self, '备份失败', str(e))

    def _show_about(self):
        QMessageBox.about(self, '关于',
            f'<h3>中药材销售管理系统</h3>'
            f'<p>版本: {CURRENT_VERSION}</p>'
            f'<p>发布日期: {VERSION_DATE}</p>'
            f'<hr>'
            f'<p>一款专业的中药材信息管理系统</p>'
            f'<p>支持药材管理、处方开具、库存管理等功能</p>'
            f'<hr>'
            f'{get_shortcut_help_text()}'
        )

    def switch_view(self, view_name):
        view_map = {
            'dashboard': 0,
            'medicine': 1,
            'prescription': 2,
            'patient': 3,
            'inventory': 4,
            'history': 5,
            'statistics': 6
        }

        index = view_map.get(view_name, 0)
        self.stacked_widget.setCurrentIndex(index)

        self.page_header.set_page(view_name)

        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        if view_name == 'dashboard':
            self.dashboard_view.refresh_data()
        elif view_name == 'inventory':
            self.inventory_view.refresh_data()
        elif view_name == 'history':
            self.history_view.refresh_data()
        elif view_name == 'statistics':
            self.statistics_view.refresh_data()
        elif view_name == 'patient':
            self.patient_view.load_data()

        view_names = {
            'dashboard': '首页概览',
            'medicine': '药材管理',
            'prescription': '开处方',
            'patient': '客户管理',
            'inventory': '库存管理',
            'history': '处方历史',
            'statistics': '销售统计'
        }
        self.status_bar.showMessage(view_names.get(view_name, ''))

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, '退出确认',
            '确定要退出程序吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logger.info("应用程序关闭")
            self.db.close()
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)

    font_manager = get_font_manager()
    # 仅设置字体族，不设 pointSize，让样式表 px 字号完全接管
    font = QFont(font_manager.base_font_family)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
