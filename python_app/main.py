import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox, 
                              QProgressBar, QDialog, QStatusBar, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon

from core import Database, BuiltinDataLoader, get_app_logger
from core.theme import get_main_window_style
from views.medicine_view import MedicineView
from views.prescription_view import PrescriptionView
from views.inventory_view import InventoryView
from views.history_view import HistoryView
from views.batch_import_view import BatchImportView
from widgets.page_header import PageHeader
from widgets.update_dialog import UpdateDialog
from utils.responsive_font import get_font_manager
from utils.version import CURRENT_VERSION, VERSION_DATE, VersionManager
from utils.updater import UpdateManager, UpdateInfo


class ImportThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str, int, int)

    def __init__(self, db):
        super().__init__()
        self.db = db

    def run(self):
        try:
            from medicines_data_300 import medicines_300
            
            total = len(medicines_300)
            added = 0
            updated = 0
            
            for i, medicine in enumerate(medicines_300):
                try:
                    existing = self.db.fetchone(
                        "SELECT id FROM medicines WHERE name = ?", 
                        (medicine['name'],)
                    )
                    
                    if existing:
                        self.db.execute('''
                            UPDATE medicines 
                            SET alias=?, category=?, nature=?, taste=?, meridian=?,
                                efficacy=?, indications=?, usage=?, dosage=?, 
                                contraindication=?, notes=?
                            WHERE id=?
                        ''', (
                            medicine.get('alias', ''),
                            medicine.get('category', ''),
                            medicine.get('nature', ''),
                            medicine.get('taste', ''),
                            medicine.get('meridian', ''),
                            medicine.get('efficacy', ''),
                            medicine.get('indications', ''),
                            medicine.get('usage', ''),
                            medicine.get('dosage', ''),
                            medicine.get('contraindication', ''),
                            medicine.get('notes', ''),
                            existing[0]
                        ))
                        
                        self.db.execute('''
                            UPDATE inventory 
                            SET quantity=?, unit=?, price=?, min_stock=?, notes=?
                            WHERE medicine_id=?
                        ''', (
                            medicine.get('quantity', 0),
                            medicine.get('unit', 'g'),
                            medicine.get('price', 0),
                            medicine.get('min_stock', 10),
                            medicine.get('notes', ''),
                            existing[0]
                        ))
                        updated += 1
                    else:
                        self.db.execute('''
                            INSERT INTO medicines 
                            (name, alias, category, nature, taste, meridian, 
                             efficacy, indications, usage, dosage, contraindication, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            medicine['name'],
                            medicine.get('alias', ''),
                            medicine.get('category', ''),
                            medicine.get('nature', ''),
                            medicine.get('taste', ''),
                            medicine.get('meridian', ''),
                            medicine.get('efficacy', ''),
                            medicine.get('indications', ''),
                            medicine.get('usage', ''),
                            medicine.get('dosage', ''),
                            medicine.get('contraindication', ''),
                            medicine.get('notes', '')
                        ))
                        
                        med_id = self.db.fetchone(
                            "SELECT id FROM medicines WHERE name = ?", 
                            (medicine['name'],)
                        )[0]
                        
                        self.db.execute('''
                            INSERT INTO inventory 
                            (medicine_id, quantity, unit, price, min_stock, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            med_id,
                            medicine.get('quantity', 0),
                            medicine.get('unit', 'g'),
                            medicine.get('price', 0),
                            medicine.get('min_stock', 10),
                            medicine.get('notes', '')
                        ))
                        added += 1
                    
                    self.progress.emit(int((i + 1) / total * 100))
                    
                except Exception as e:
                    print(f"导入 {medicine['name']} 时出错: {e}")
                    continue
            
            self.finished.emit(True, f"导入完成！新增 {added} 味，更新 {updated} 味", added, updated)
            
        except Exception as e:
            self.finished.emit(False, f"导入失败: {str(e)}", 0, 0)


class ImportDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.font_manager = get_font_manager()
        self.setWindowTitle('批量导入药材')
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        info_label = QLabel('将导入常用中药材数据到系统中')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('color: #606266; padding: 15px;')
        info_label.setFont(self.font_manager.get_font('body'))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        self.status_label = QLabel('点击"开始"执行导入')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(self.font_manager.get_font('small'))
        self.status_label.setStyleSheet('color: #909399;')
        
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton('开始')
        self.start_btn.setStyleSheet('background-color: #409eff; color: white; padding: 10px 30px;')
        self.start_btn.setFont(self.font_manager.get_font('button'))
        self.start_btn.clicked.connect(self.start_import)
        self.close_btn = QPushButton('关闭')
        self.close_btn.setFont(self.font_manager.get_font('button'))
        self.close_btn.setStyleSheet('background-color: #f4f4f5; color: #606266; padding: 10px 30px;')
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        
        layout.addWidget(info_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)

    def start_import(self):
        self.start_btn.setEnabled(False)
        self.status_label.setText('正在导入...')
        
        self.import_thread = ImportThread(self.db)
        self.import_thread.progress.connect(self.update_progress)
        self.import_thread.finished.connect(self.import_finished)
        self.import_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f'进度: {value}%')

    def import_finished(self, success, message, added, updated):
        self.status_label.setText(message)
        if success:
            QMessageBox.information(self, '完成', message)
        else:
            QMessageBox.warning(self, '提示', message)
        
        self.close_btn.setEnabled(True)
        self.start_btn.setEnabled(False)


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
        self._check_update_on_startup()
    
    def init_ui(self):
        self.setWindowTitle('中药材销售管理系统')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(800, 600)
        
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
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                padding: 5px 10px;
            }
            QMenuBar::item {
                padding: 8px 15px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QMenu {
                background-color: white;
                border: 1px solid #dcdfe6;
            }
            QMenu::item {
                padding: 8px 30px;
                color: #303133;
            }
            QMenu::item:selected {
                background-color: #f5f7fa;
            }
        """)
        
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
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f5f7fa;
                color: #606266;
                border-top: 1px solid #e4e7ed;
            }
        """)
        self.status_bar.showMessage('就绪')
    
    def _create_sidebar(self, main_layout):
        self.sidebar = QFrame()
        self.sidebar.setObjectName('sidebar')
        self._update_sidebar_width(1400)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        brand_container = QWidget()
        brand_container.setObjectName('brand_container')
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(15, 20, 15, 25)
        brand_layout.setSpacing(6)
        
        self.brand_title = QLabel('中药材管理系统')
        self.brand_title.setObjectName('brand_title')
        self.brand_title.setAlignment(Qt.AlignCenter)
        
        self.brand_subtitle = QLabel('专业中医药信息平台')
        self.brand_subtitle.setObjectName('brand_subtitle')
        self.brand_subtitle.setAlignment(Qt.AlignCenter)
        
        brand_layout.addWidget(self.brand_title)
        brand_layout.addWidget(self.brand_subtitle)
        
        sidebar_layout.addWidget(brand_container)
        
        separator = QFrame()
        separator.setObjectName('sidebar_separator')
        separator.setFixedHeight(1)
        sidebar_layout.addWidget(separator)
        
        self.nav_buttons = []
        nav_items = [
            ('药材管理', 'medicine'),
            ('开处方', 'prescription'),
            ('库存管理', 'inventory'),
            ('处方历史', 'history')
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
        sidebar_layout.addWidget(self.version_label)
        
        main_layout.addWidget(self.sidebar)
    
    def _create_content_area(self, main_layout):
        content_area = QFrame()
        content_area.setObjectName('content_area')
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        self.page_header = PageHeader('medicine')
        content_layout.addWidget(self.page_header)
        
        self.stacked_widget = QStackedWidget()
        
        self.medicine_view = MedicineView(self.db)
        self.prescription_view = PrescriptionView(self.db)
        self.inventory_view = InventoryView(self.db)
        self.history_view = HistoryView(self.db)
        
        self.stacked_widget.addWidget(self.medicine_view)
        self.stacked_widget.addWidget(self.prescription_view)
        self.stacked_widget.addWidget(self.inventory_view)
        self.stacked_widget.addWidget(self.history_view)
        
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_area)
    
    def _apply_responsive_styles(self):
        base_size = self.font_manager.current_base_size
        self.setStyleSheet(get_main_window_style(base_size))
    
    def _get_sidebar_width(self, window_width):
        if window_width < 900:
            return 200
        elif window_width < 1200:
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
        
        if hasattr(self.medicine_view, 'update_fonts'):
            self.medicine_view.update_fonts()
        if hasattr(self.inventory_view, 'update_fonts'):
            self.inventory_view.update_fonts()
        if hasattr(self.prescription_view, 'update_fonts'):
            self.prescription_view.update_fonts()
        if hasattr(self.history_view, 'update_fonts'):
            self.history_view.update_fonts()
    
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
                    self._apply_responsive_styles()
                    QApplication.processEvents()
    
    def timerEvent(self, event):
        self.killTimer(self._resize_timer)
        self._resize_timer = None
        
        new_width = self.width()
        old_base_size = self.font_manager.current_base_size
        
        self.font_manager.update_for_window_size(new_width)
        
        if self.font_manager.current_base_size != old_base_size:
            self._apply_responsive_styles()
            self._update_sidebar_width(new_width)
            
            QApplication.processEvents()
            
            for view in [self.medicine_view, self.inventory_view, 
                        self.prescription_view, self.history_view]:
                if hasattr(view, 'update'):
                    view.update()
                if hasattr(view, 'viewport'):
                    view.viewport().update()
    
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
        dialog = QDialog(self)
        dialog.setWindowTitle('批量导入药材数据')
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        import_widget = BatchImportView(self.db, dialog)
        layout.addWidget(import_widget)
        
        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet('background-color: #909399; color: white; padding: 10px 30px;')
        close_btn.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
        self.medicine_view.load_data()
        self.inventory_view.refresh_data()
    
    def _export_data(self):
        self.status_bar.showMessage('正在导出数据...')
        try:
            from PyQt5.QtWidgets import QFileDialog
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
        QMessageBox.about(self, '关于', 
            f'<h3>中药材销售管理系统</h3>'
            f'<p>版本: {CURRENT_VERSION}</p>'
            f'<p>发布日期: {VERSION_DATE}</p>'
            f'<hr>'
            f'<p>一款专业的中药材信息管理系统</p>'
            f'<p>支持药材管理、处方开具、库存管理等功能</p>'
        )
    
    def switch_view(self, view_name):
        view_map = {
            'medicine': 0,
            'prescription': 1,
            'inventory': 2,
            'history': 3
        }
        
        index = view_map.get(view_name, 0)
        self.stacked_widget.setCurrentIndex(index)
        
        self.page_header.set_page(view_name)
        
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        if view_name == 'inventory':
            self.inventory_view.refresh_data()
        elif view_name == 'history':
            self.history_view.refresh_data()
        
        view_names = {
            'medicine': '药材管理',
            'prescription': '开处方',
            'inventory': '库存管理',
            'history': '处方历史'
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
    font = QFont(font_manager.base_font_family, font_manager.current_base_size)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
