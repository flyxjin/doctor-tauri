from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                             QDoubleSpinBox, QMessageBox, QGroupBox, QLabel, QLineEdit,
                             QComboBox, QFileDialog, QHeaderView)
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtCore import Qt
from utils.responsive_font import ResponsiveWidget, get_font_manager
from core import InventoryService
from core.theme import AppColors, get_button_style, get_dialog_style, get_table_style
import csv


class StockDialog(QDialog):
    """入库/出库操作弹窗"""

    def __init__(self, parent=None, medicine_name="", medicine_id=None, operation="入库", current_qty=0, current_price=0):
        super().__init__(parent)
        self.setWindowTitle(f'{operation}操作 - {medicine_name}')
        self.medicine_id = medicine_id
        self.operation = operation
        self.current_qty = current_qty
        self.current_price = current_price
        self.setFixedWidth(350)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.setStyleSheet(get_dialog_style())

        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 10000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setSuffix(' g')

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 10000)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix('¥ ')
        if self.current_price > 0:
            self.price_spin.setValue(self.current_price)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['g', 'kg', '片', '条', '个', '包', '盒'])
        self.unit_combo.setCurrentText('g')

        self.notes_edit = QLineEdit()

        layout.addRow('数量:', self.quantity_spin)
        layout.addRow('单位:', self.unit_combo)
        if self.operation == "入库":
            layout.addRow('进价:', self.price_spin)
        layout.addRow('备注:', self.notes_edit)

        if self.operation == "出库":
            info_label = QLabel(f'当前库存: {self.current_qty} g')
            info_label.setStyleSheet(f'color: {AppColors.TEXT_REGULAR}; font-size: 12px;')
            layout.addRow('', info_label)

        btn_box = QHBoxLayout()
        ok_btn = QPushButton('确认')
        ok_btn.setStyleSheet(get_button_style(AppColors.PRIMARY))
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet(get_button_style(AppColors.INFO))
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def get_data(self):
        return self.quantity_spin.value(), self.price_spin.value(), self.unit_combo.currentText(), self.notes_edit.text()


class InventoryView(QWidget, ResponsiveWidget):
    def __init__(self, db):
        QWidget.__init__(self)
        ResponsiveWidget.__init__(self)
        self.db = db
        self._inventory_service = InventoryService(db)
        self._font_manager = get_font_manager()
        self._base_column_widths = [0, 150, 80, 100, 60, 90, 110, 80, 120]
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        stats_group = QGroupBox('库存统计')
        stats_layout = QHBoxLayout(stats_group)
        
        self.total_meds_label = QLabel('药材种类: 0')
        self.total_meds_label.setStyleSheet(f'font-size: 14px; font-weight: bold; color: {AppColors.PRIMARY};')

        self.total_value_label = QLabel('库存总值: ¥0.00')
        self.total_value_label.setStyleSheet(f'font-size: 14px; font-weight: bold; color: {AppColors.SUCCESS};')

        self.low_stock_label = QLabel('低库存: 0')
        self.low_stock_label.setStyleSheet(f'font-size: 14px; font-weight: bold; color: {AppColors.DANGER};')
        
        stats_layout.addWidget(self.total_meds_label)
        stats_layout.addWidget(self.total_value_label)
        stats_layout.addWidget(self.low_stock_label)
        stats_layout.addStretch()

        self.warning_group = QGroupBox('库存预警')
        warning_layout = QHBoxLayout(self.warning_group)
        self.warning_label = QLabel('库存状态正常')
        self.warning_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")
        warning_layout.addWidget(self.warning_label)

        search_group = QGroupBox('搜索筛选')
        search_layout = QHBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入药材名称搜索...')
        self.search_input.setMinimumWidth(200)
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItems(['全部', '库存充足', '低库存', '缺货'])
        
        self.search_btn = QPushButton('搜索')
        self.refresh_btn = QPushButton('刷新')
        
        self.search_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.stock_filter)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.refresh_btn)
        search_layout.addStretch()

        btn_bar = QHBoxLayout()
        self.stock_in_btn = QPushButton('药材入库')
        self.stock_out_btn = QPushButton('药材出库')
        self.adjust_btn = QPushButton('库存调整')
        self.export_btn = QPushButton('导出库存')
        
        self.stock_in_btn.setStyleSheet(get_button_style(AppColors.SUCCESS))
        self.stock_out_btn.setStyleSheet(get_button_style(AppColors.WARNING))
        self.adjust_btn.setStyleSheet(get_button_style(AppColors.PRIMARY))
        self.export_btn.setStyleSheet(get_button_style(AppColors.INFO))
        
        self.stock_in_btn.clicked.connect(self.stock_in)
        self.stock_out_btn.clicked.connect(self.stock_out)
        self.adjust_btn.clicked.connect(self.adjust_stock)
        self.export_btn.clicked.connect(self.export_inventory)
        
        btn_bar.addWidget(self.stock_in_btn)
        btn_bar.addWidget(self.stock_out_btn)
        btn_bar.addWidget(self.adjust_btn)
        btn_bar.addWidget(self.export_btn)
        btn_bar.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            'ID', '药材名称', '分类', '库存数量', '单位', '单价(¥)', '库存总值(¥)', '最低库存', '备注'
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self._apply_responsive_table()

        layout.addWidget(stats_group)
        layout.addWidget(self.warning_group)
        layout.addWidget(search_group)
        layout.addLayout(btn_bar)
        layout.addWidget(self.table)

    def refresh_data(self):
        keyword = self.search_input.text()
        stock_filter = self.stock_filter.currentText()
        
        query = '''
            SELECT i.medicine_id, m.name, m.category, i.quantity, i.unit, i.price, i.min_stock, i.notes 
            FROM inventory i 
            JOIN medicines m ON i.medicine_id = m.id
            WHERE 1=1
        '''
        params = []
        
        if keyword:
            query += " AND m.name LIKE ?"
            params.append(f'%{keyword}%')
        
        rows = self.db.fetchall(query, params)
        
        filtered_rows = []
        low_stock_list = []
        total_value = 0
        
        for row in rows:
            med_id = row['medicine_id']
            name = row['name']
            category = row['category']
            qty = row['quantity'] or 0
            unit = row['unit']
            price = row['price'] or 0
            min_stock = row['min_stock'] or 0
            notes = row['notes']
            stock_value = qty * price
            total_value += stock_value
            
            include = (
                stock_filter == '全部'
                or (stock_filter == '库存充足' and qty >= min_stock)
                or (stock_filter == '低库存' and 0 < qty < min_stock)
                or (stock_filter == '缺货' and qty == 0)
            )
            if include:
                filtered_rows.append((med_id, name, category, qty, unit, price, min_stock, notes, stock_value))
            
            if qty < min_stock:
                low_stock_list.append(name)
        
        display_rows = filtered_rows
        
        self.table.setRowCount(len(display_rows))
        
        for row_idx, row_data in enumerate(display_rows):
            med_id, name, category, qty, unit, price, min_stock, notes, stock_value = row_data
            qty = qty or 0
            price = price or 0
            min_stock = min_stock or 0
            
            values = [med_id, name, category, qty, unit, price, stock_value, min_stock, notes]
            
            for col_idx, col_data in enumerate(values):
                if col_idx in [3, 5, 6, 7]:
                    if col_idx == 6:
                        item = QTableWidgetItem(f'¥{col_data:.2f}')
                    elif col_idx == 5:
                        item = QTableWidgetItem(f'¥{col_data:.2f}')
                    else:
                        item = QTableWidgetItem(f'{col_data:.2f}')
                else:
                    item = QTableWidgetItem(str(col_data) if col_data is not None else '')
                
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                
                if col_idx == 3:
                    if qty == 0:
                        item.setBackground(QBrush(QColor(AppColors.STOCK_ZERO_BG)))
                    elif qty < min_stock:
                        item.setBackground(QBrush(QColor(AppColors.STOCK_LOW_BG)))
                
                self.table.setItem(row_idx, col_idx, item)
        
        self.total_meds_label.setText(f'药材种类: {len(rows)}')
        self.total_value_label.setText(f'库存总值: ¥{total_value:.2f}')
        self.low_stock_label.setText(f'低库存: {len(low_stock_list)}')
        
        if low_stock_list:
            self.warning_label.setText(f"库存预警：{', '.join(low_stock_list[:5])}{'...' if len(low_stock_list) > 5 else ''} 库存不足！")
            self.warning_label.setStyleSheet(f"color: {AppColors.DANGER}; font-weight: bold;")
        else:
            self.warning_label.setText("库存状态正常")
            self.warning_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")

    def stock_in(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请选择要入库的药材')
            return

        row = selected[0].row()
        med_id = self.table.item(row, 0).text()
        med_name = self.table.item(row, 1).text()
        current_price = float(self.table.item(row, 5).text().replace('¥', ''))

        dialog = StockDialog(self, med_name, med_id, "入库", current_price=current_price)
        if dialog.exec_():
            qty, price, unit, notes = dialog.get_data()
            try:
                self._inventory_service.stock_in(med_id, qty, price, notes)
                QMessageBox.information(self, '成功', '入库成功！')
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'入库失败：{str(e)}')

    def stock_out(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请选择要出库的药材')
            return

        row = selected[0].row()
        med_id = self.table.item(row, 0).text()
        med_name = self.table.item(row, 1).text()
        current_qty = float(self.table.item(row, 3).text())
        current_price = float(self.table.item(row, 5).text().replace('¥', ''))

        dialog = StockDialog(self, med_name, med_id, "出库", current_qty=current_qty, current_price=current_price)
        if dialog.exec_():
            qty, price, unit, notes = dialog.get_data()

            if qty > current_qty:
                QMessageBox.warning(self, '错误', '出库数量不能大于当前库存！')
                return

            try:
                self._inventory_service.stock_out(med_id, qty, price, notes)
                QMessageBox.information(self, '成功', '出库成功！')
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'出库失败：{str(e)}')

    def adjust_stock(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请选择要调整的药材')
            return

        row = selected[0].row()
        med_id = self.table.item(row, 0).text()
        med_name = self.table.item(row, 1).text()
        current_qty = float(self.table.item(row, 3).text())
        current_price = float(self.table.item(row, 5).text().replace('¥', ''))
        min_stock = float(self.table.item(row, 7).text())

        dialog = QDialog(self)
        dialog.setWindowTitle(f'库存调整 - {med_name}')
        dialog.setFixedWidth(350)
        dialog.setStyleSheet(get_dialog_style())
        layout = QFormLayout(dialog)

        qty_spin = QDoubleSpinBox()
        qty_spin.setRange(0, 10000)
        qty_spin.setDecimals(2)
        qty_spin.setSuffix(' g')
        qty_spin.setValue(current_qty)

        price_spin = QDoubleSpinBox()
        price_spin.setRange(0, 10000)
        price_spin.setDecimals(2)
        price_spin.setPrefix('¥ ')
        price_spin.setValue(current_price)

        min_stock_spin = QDoubleSpinBox()
        min_stock_spin.setRange(0, 10000)
        min_stock_spin.setDecimals(2)
        min_stock_spin.setSuffix(' g')
        min_stock_spin.setValue(min_stock)

        notes_edit = QLineEdit()

        layout.addRow('调整后库存:', qty_spin)
        layout.addRow('单价:', price_spin)
        layout.addRow('最低库存:', min_stock_spin)
        layout.addRow('备注:', notes_edit)

        btn_box = QHBoxLayout()
        ok_btn = QPushButton('确认')
        ok_btn.setStyleSheet(get_button_style(AppColors.PRIMARY))
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet(get_button_style(AppColors.INFO))
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

        if dialog.exec_():
            try:
                self._inventory_service.adjust_stock(
                    med_id, qty_spin.value(), price_spin.value(),
                    min_stock_spin.value(), notes_edit.text()
                )
                QMessageBox.information(self, '成功', '库存调整成功！')
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'调整失败：{str(e)}')

    def export_inventory(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, '导出库存数据', '', 'CSV文件 (*.csv)')
            if filename:
                rows = self.db.fetchall('''
                    SELECT i.medicine_id, m.name, m.category, i.quantity, i.unit, i.price, i.min_stock, i.notes 
                    FROM inventory i 
                    JOIN medicines m ON i.medicine_id = m.id
                ''')
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['药材ID', '药材名称', '分类', '库存数量', '单位', '单价', '最低库存', '备注'])
                    for row in rows:
                        writer.writerow([
                            row['medicine_id'],
                            row['name'],
                            row['category'],
                            row['quantity'],
                            row['unit'],
                            row['price'],
                            row['min_stock'],
                            row['notes']
                        ])
                QMessageBox.information(self, '成功', '库存数据导出成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'导出失败: {str(e)}')
    
    def _apply_responsive_table(self):
        if not hasattr(self, 'table'):
            return
            
        config = self._font_manager.get_table_config()
        scale = config['scale']
        
        self.table.verticalHeader().setDefaultSectionSize(config['row_height'])
        self.table.verticalHeader().setMinimumSectionSize(config['row_height'])
        
        header = self.table.horizontalHeader()
        header.setMinimumSectionSize(config['cell_padding'] * 2)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        for col in range(len(self._base_column_widths)):
            if col == 0:
                continue
            base_width = self._base_column_widths[col]
            scaled_width = int(base_width * scale)
            self.table.setColumnWidth(col, scaled_width)
        
        font = self._font_manager.get_font('table_cell')
        self.table.setFont(font)
        
        header_font = self._font_manager.get_font('table_header')
        header.setFont(header_font)
        
        self.table.setStyleSheet(get_table_style(config['font_size'], config['header_font_size'], config['cell_padding']))
        
        font_size = self._font_manager.get_font_size('body')
        if hasattr(self, 'total_meds_label'):
            self.total_meds_label.setStyleSheet(f'font-size: {font_size}px; font-weight: bold; color: {AppColors.PRIMARY};')
        if hasattr(self, 'total_value_label'):
            self.total_value_label.setStyleSheet(f'font-size: {font_size}px; font-weight: bold; color: {AppColors.SUCCESS};')
        if hasattr(self, 'low_stock_label'):
            self.low_stock_label.setStyleSheet(f'font-size: {font_size}px; font-weight: bold; color: {AppColors.DANGER};')
    
    def update_fonts(self):
        self._apply_responsive_table()
        self.refresh_data()
