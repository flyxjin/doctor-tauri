import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox, QProgressBar, QDialog)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from database import Database
from views.medicine_view import MedicineView
from views.prescription_view import PrescriptionView
from views.inventory_view import InventoryView
from views.history_view import HistoryView
from views.batch_import_view import BatchImportView
from utils.responsive_font import get_font_manager


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
        self.setWindowTitle('导入300味药材')
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel('即将导入300味常用中药材数据\n包括完整的药材信息和库存数据')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('color: #666; padding: 20px;')
        info_label.setFont(self.font_manager.get_font('body'))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(self.font_manager.get_font('small'))
        
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton('开始导入')
        self.start_btn.setStyleSheet('background-color: #409eff; color: white; padding: 10px 30px;')
        self.start_btn.setFont(self.font_manager.get_font('button'))
        self.start_btn.clicked.connect(self.start_import)
        self.close_btn = QPushButton('关闭')
        self.close_btn.setFont(self.font_manager.get_font('button'))
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
        self.status_label.setText(f'正在导入... {value}%')

    def import_finished(self, success, message, added, updated):
        if success:
            self.status_label.setText(message)
            QMessageBox.information(self, '成功', message)
        else:
            self.status_label.setText('导入失败')
            QMessageBox.warning(self, '错误', message)
        
        self.close_btn.setEnabled(True)
        self.start_btn.setEnabled(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.font_manager = get_font_manager()
        self.font_manager.font_changed.connect(self._on_font_changed)
        self._resize_timer = None
        self._last_window_state = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('中药材销售管理系统')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(800, 600)
        
        self._apply_responsive_styles()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = QFrame()
        self.sidebar.setObjectName('sidebar')
        self._update_sidebar_width(1400)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        self.title_label = QLabel('中药材管理系统')
        self.title_label.setObjectName('title_label')
        self.title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.title_label)
        
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
        
        self.help_btn = QPushButton('使用帮助')
        self.help_btn.setObjectName('help_btn')
        self.help_btn.clicked.connect(self.show_help)
        sidebar_layout.addWidget(self.help_btn)
        
        self.import_btn = QPushButton('批量导入药材')
        self.import_btn.setObjectName('import_btn')
        self.import_btn.clicked.connect(self.show_import_dialog)
        sidebar_layout.addWidget(self.import_btn)
        
        self.version_label = QLabel('版本 2.0.0')
        self.version_label.setObjectName('version_label')
        self.version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.version_label)
        
        main_layout.addWidget(self.sidebar)
        
        content_area = QFrame()
        content_area.setObjectName('content_area')
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
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
        
        self.nav_buttons[0].setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
        
        self.font_manager.update_for_window_size(self.width())
    
    def _apply_responsive_styles(self):
        base_size = self.font_manager.current_base_size
        title_size = int(base_size * 1.6)
        subtitle_size = int(base_size * 1.3)
        body_size = base_size
        small_size = int(base_size * 0.9)
        tiny_size = int(base_size * 0.85)
        button_size = int(base_size * 1.1)
        
        sidebar_width = self._get_sidebar_width(self.width() if hasattr(self, 'width') else 1400)
        
        self.setStyleSheet(f'''
            QMainWindow {{
                background-color: #f5f7fa;
            }}
            QPushButton {{
                background-color: #409eff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: {button_size}px;
                text-align: left;
                min-width: 140px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: #66b1ff;
            }}
            QPushButton:pressed {{
                background-color: #3a8ee6;
            }}
            QPushButton:checked {{
                background-color: #3a8ee6;
                font-weight: bold;
            }}
            QLabel {{
                font-size: {body_size}px;
                color: #333;
            }}
            QFrame {{
                background-color: white;
                border-radius: 8px;
            }}
            QFrame#sidebar {{
                background-color: #2c3e50;
                border-radius: 0;
            }}
            QLabel#title_label {{
                color: white;
                font-size: {title_size}px;
                font-weight: bold;
                padding: 20px 10px;
                border-bottom: 1px solid #34495e;
            }}
            QPushButton#nav_btn {{
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 16px 24px;
                border-radius: 6px;
                min-width: 0;
                font-size: {button_size}px;
                min-height: 40px;
            }}
            QPushButton#nav_btn:hover {{
                background-color: #34495e;
            }}
            QPushButton#nav_btn:checked {{
                background-color: #3498db;
            }}
            QPushButton#help_btn {{
                background-color: #909399;
                color: white;
                text-align: center;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: {button_size}px;
                min-height: 40px;
            }}
            QPushButton#help_btn:hover {{
                background-color: #a6a9ad;
            }}
            QPushButton#import_btn {{
                background-color: #67c23a;
                color: white;
                text-align: center;
                padding: 14px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: {button_size}px;
                min-height: 44px;
            }}
            QPushButton#import_btn:hover {{
                background-color: #85ce61;
            }}
            QLabel#version_label {{
                color: #7f8c8d;
                font-size: {tiny_size}px;
                padding: 10px;
            }}
            QFrame#content_area {{
                background-color: transparent;
            }}
            QGroupBox {{
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
                font-size: {subtitle_size}px;
                color: #409eff;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
            QTableWidget {{
                font-size: {body_size}px;
                gridline-color: #e0e0e0;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                font-size: {button_size}px;
                font-weight: bold;
                padding: 10px 8px;
                background-color: #f5f7fa;
                border: none;
                border-bottom: 2px solid #e0e0e0;
            }}
            QLineEdit {{
                font-size: {body_size}px;
                padding: 8px 12px;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                min-height: 28px;
            }}
            QLineEdit:focus {{
                border-color: #409eff;
            }}
            QComboBox {{
                font-size: {body_size}px;
                padding: 6px 10px;
                min-height: 28px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QTextEdit {{
                font-size: {body_size}px;
                padding: 8px;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
            }}
            QScrollBar:vertical {{
                width: 16px;
                background-color: #f5f7fa;
            }}
            QScrollBar::handle:vertical {{
                background-color: #c0c4cc;
                border-radius: 8px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #909399;
            }}
            QScrollBar:horizontal {{
                height: 16px;
                background-color: #f5f7fa;
            }}
            QScrollBar::handle:horizontal {{
                background-color: #c0c4cc;
                border-radius: 8px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: #909399;
            }}
        ''')
    
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
    
    def show_help(self):
        help_text = '''
        <h2 style="color: #409eff;">中药材销售管理系统 - 使用帮助</h2>
        <hr>
        <h3>药材管理</h3>
        <ul>
            <li><b>添加药材</b>: 点击"添加药材"按钮，填写药材信息</li>
            <li><b>修改药材</b>: 选中表格行后点击"修改信息"</li>
            <li><b>删除药材</b>: 选中表格行后点击"删除药材"</li>
            <li><b>搜索药材</b>: 在搜索框输入名称、别名或功效</li>
            <li><b>筛选分类</b>: 使用下拉框按分类或药性筛选</li>
            <li><b>导出数据</b>: 点击"导出数据"保存为CSV文件</li>
        </ul>
        <h3>开处方</h3>
        <ul>
            <li><b>填写患者信息</b>: 输入姓名、年龄、性别、诊断</li>
            <li><b>添加药材</b>: 搜索药材后点击"添加到处方"</li>
            <li><b>修改数量</b>: 双击表格中的数量列修改</li>
            <li><b>保存处方</b>: 点击"保存处方并扣减库存"</li>
            <li><b>打印处方</b>: 点击"打印处方"打印当前处方</li>
        </ul>
        <h3>库存管理</h3>
        <ul>
            <li><b>入库</b>: 选中药材后点击"药材入库"</li>
            <li><b>出库</b>: 选中药材后点击"药材出库"</li>
            <li><b>调整库存</b>: 点击"库存调整"修改库存数量</li>
            <li><b>库存预警</b>: 库存低于最低值时显示红色警告</li>
        </ul>
        <h3>处方历史</h3>
        <ul>
            <li>查看所有历史处方记录</li>
            <li>支持按日期范围筛选</li>
            <li>可查看处方详情和重新打印</li>
        </ul>
        <hr>
        <h3>快捷键</h3>
        <ul>
            <li><b>Ctrl+F</b>: 快速搜索</li>
            <li><b>Ctrl+N</b>: 新增药材</li>
            <li><b>Ctrl+S</b>: 保存</li>
            <li><b>Ctrl+P</b>: 打印</li>
            <li><b>ESC</b>: 关闭弹窗</li>
        </ul>
        <hr>
        <p style="color: #909399;">版本: 2.0.0</p>
        '''
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('使用帮助')
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setMinimumWidth(600)
        msg_box.exec_()
    
    def switch_view(self, view_name):
        view_map = {
            'medicine': 0,
            'prescription': 1,
            'inventory': 2,
            'history': 3
        }
        
        index = view_map.get(view_name, 0)
        self.stacked_widget.setCurrentIndex(index)
        
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        if view_name == 'inventory':
            self.inventory_view.refresh_data()
        elif view_name == 'history':
            self.history_view.refresh_data()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出系统吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
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