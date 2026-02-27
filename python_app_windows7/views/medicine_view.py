# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit,
                             QDialog, QFormLayout, QMessageBox, QComboBox,
                             QTextEdit, QSplitter, QGroupBox, QLabel, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from utils.responsive_font import ResponsiveWidget, get_font_manager
from core import get_medicine_cache, measure, Timer


class MedicineDialog(QDialog):
    """添加/编辑药材的弹窗"""

    def __init__(self, parent=None, medicine_data=None):
        super().__init__(parent)
        self.medicine_data = medicine_data
        self.setWindowTitle('药材信息')
        self.setFixedWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.alias_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.addItems(['', '补虚药', '解表药', '清热药', '泻下药', '祛风湿药', '化湿药', '利水渗湿药', '温里药', '理气药', '消食药', '驱虫药', '止血药', '活血化瘀药', '化痰止咳平喘药', '安神药', '平肝息风药', '开窍药', '收涩药', '攻毒杀虫止痒药', '拔毒化腐生肌药'])
        self.nature_combo = QComboBox()
        self.nature_combo.addItems(['', '寒', '热', '温', '凉', '平', '微寒', '微温', '大寒'])
        self.taste_edit = QLineEdit()
        self.meridian_edit = QLineEdit()
        self.efficacy_edit = QTextEdit()
        self.efficacy_edit.setMaximumHeight(60)
        self.indications_edit = QTextEdit()
        self.indications_edit.setMaximumHeight(60)
        self.usage_edit = QLineEdit()
        self.dosage_edit = QLineEdit()
        self.contraindication_edit = QTextEdit()
        self.contraindication_edit.setMaximumHeight(60)
        self.notes_edit = QLineEdit()

        layout.addRow('药材名称*:', self.name_edit)
        layout.addRow('别名:', self.alias_edit)
        layout.addRow('分类:', self.category_combo)
        layout.addRow('药性:', self.nature_combo)
        layout.addRow('药味:', self.taste_edit)
        layout.addRow('归经:', self.meridian_edit)
        layout.addRow('功效:', self.efficacy_edit)
        layout.addRow('主治:', self.indications_edit)
        layout.addRow('用法:', self.usage_edit)
        layout.addRow('用量:', self.dosage_edit)
        layout.addRow('禁忌:', self.contraindication_edit)
        layout.addRow('备注:', self.notes_edit)

        btn_box = QHBoxLayout()
        self.ok_btn = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.ok_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addRow(btn_box)

        if self.medicine_data:
            self._populate_fields(medicine_data)

    def _populate_fields(self, data):
        if isinstance(data, dict):
            self.name_edit.setText(data.get('name', ''))
            self.alias_edit.setText(data.get('alias', ''))
            index = self.category_combo.findText(data.get('category', ''))
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            index = self.nature_combo.findText(data.get('nature', ''))
            if index >= 0:
                self.nature_combo.setCurrentIndex(index)
            self.taste_edit.setText(data.get('taste', ''))
            self.meridian_edit.setText(data.get('meridian', ''))
            self.efficacy_edit.setText(data.get('efficacy', ''))
            self.indications_edit.setText(data.get('indications', ''))
            self.usage_edit.setText(data.get('usage', ''))
            self.dosage_edit.setText(data.get('dosage', ''))
            self.contraindication_edit.setText(data.get('contraindication', ''))
            self.notes_edit.setText(data.get('notes', ''))
        else:
            self.name_edit.setText(data[1] or '')
            self.alias_edit.setText(data[2] or '')
            index = self.category_combo.findText(data[3] or '')
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            index = self.nature_combo.findText(data[4] or '')
            if index >= 0:
                self.nature_combo.setCurrentIndex(index)
            self.taste_edit.setText(data[5] or '')
            self.meridian_edit.setText(data[6] or '')
            self.efficacy_edit.setText(data[7] or '')
            self.indications_edit.setText(data[8] or '')
            self.usage_edit.setText(data[9] or '')
            self.dosage_edit.setText(data[10] or '')
            self.contraindication_edit.setText(data[11] or '')
            self.notes_edit.setText(data[12] or '')

    def get_data(self):
        return (
            self.name_edit.text(),
            self.alias_edit.text(),
            self.category_combo.currentText(),
            self.nature_combo.currentText(),
            self.taste_edit.text(),
            self.meridian_edit.text(),
            self.efficacy_edit.toPlainText(),
            self.indications_edit.toPlainText(),
            self.usage_edit.text(),
            self.dosage_edit.text(),
            self.contraindication_edit.toPlainText(),
            self.notes_edit.text()
        )


class MedicineView(QWidget, ResponsiveWidget):
    def __init__(self, db):
        QWidget.__init__(self)
        ResponsiveWidget.__init__(self)
        self.db = db
        self._font_manager = get_font_manager()
        self._base_column_widths = [0, 120, 100, 100, 80, 100, 150]
        self._cache = get_medicine_cache()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._delayed_search)
        self._full_data = []
        self.init_ui()
        self._init_cache()

    def _init_cache(self):
        if not self._cache.is_initialized():
            with Timer('cache_initialization'):
                medicines = self.db.fetchall("SELECT * FROM medicines")
                med_list = []
                for row in medicines:
                    med_dict = {
                        'id': row['id'],
                        'name': row['name'] or '',
                        'alias': row['alias'] or '',
                        'category': row['category'] or '',
                        'nature': row['nature'] or '',
                        'taste': row['taste'] or '',
                        'meridian': row['meridian'] or '',
                        'efficacy': row['efficacy'] or '',
                        'indications': row['indications'] or '',
                        'usage': row['usage'] or '',
                        'dosage': row['dosage'] or '',
                        'contraindication': row['contraindication'] or '',
                        'notes': row['notes'] or ''
                    }
                    med_list.append(med_dict)
                self._cache.initialize(med_list)
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        search_group = QGroupBox('搜索与筛选')
        search_layout = QHBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入药材名称、别名或功效搜索...')
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(['全部分类'])
        self.category_filter.currentIndexChanged.connect(self._on_filter_changed)
        
        self.nature_filter = QComboBox()
        self.nature_filter.addItems(['全部药性', '寒', '热', '温', '凉', '平'])
        self.nature_filter.currentIndexChanged.connect(self._on_filter_changed)
        
        self.reset_btn = QPushButton('重置')
        self.reset_btn.clicked.connect(self.reset_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(self.nature_filter)
        search_layout.addWidget(self.reset_btn)
        search_layout.addStretch()

        btn_bar = QHBoxLayout()
        self.add_btn = QPushButton('添加药材')
        self.edit_btn = QPushButton('修改信息')
        self.del_btn = QPushButton('删除药材')
        self.view_detail_btn = QPushButton('查看详情')
        self.export_btn = QPushButton('导出数据')
        
        self.add_btn.setStyleSheet('background-color: #67c23a; color: white;')
        self.edit_btn.setStyleSheet('background-color: #e6a23c; color: white;')
        self.del_btn.setStyleSheet('background-color: #f56c6c; color: white;')
        self.view_detail_btn.setStyleSheet('background-color: #409eff; color: white;')
        self.export_btn.setStyleSheet('background-color: #909399; color: white;')
        
        self.add_btn.clicked.connect(self.add_medicine)
        self.edit_btn.clicked.connect(self.edit_medicine)
        self.del_btn.clicked.connect(self.del_medicine)
        self.view_detail_btn.clicked.connect(self.view_detail)
        self.export_btn.clicked.connect(self.export_data)
        
        btn_bar.addWidget(self.add_btn)
        btn_bar.addWidget(self.edit_btn)
        btn_bar.addWidget(self.del_btn)
        btn_bar.addWidget(self.view_detail_btn)
        btn_bar.addWidget(self.export_btn)
        btn_bar.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', '名称', '别名', '分类', '药性', '药味', '归经'
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        self._apply_responsive_table()

        self.stats_label = QLabel('共 0 味药材')
        self.stats_label.setStyleSheet('color: #666; font-size: 12px;')

        layout.addWidget(search_group)
        layout.addLayout(btn_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.stats_label)

    def _on_search_text_changed(self):
        self._search_timer.start(200)

    def _on_filter_changed(self):
        self._search_timer.start(100)

    def _delayed_search(self):
        self.load_data()

    def reset_search(self):
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.nature_filter.setCurrentIndex(0)
        self.load_data()

    @measure('MedicineView.load_data')
    def load_data(self):
        keyword = self.search_input.text()
        category = self.category_filter.currentText()
        nature = self.nature_filter.currentText()
        
        if category == '全部分类':
            category = None
        if nature == '全部药性':
            nature = None
        
        with Timer('cache_search'):
            self._full_data = self._cache.search(keyword, category, nature)
        
        self._populate_table()
        self.stats_label.setText(f'共 {len(self._full_data)} 味药材')

    @measure('MedicineView.populate_table')
    def _populate_table(self):
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setRowCount(len(self._full_data))
            for row_idx, med in enumerate(self._full_data):
                self._set_table_row(row_idx, med)
        finally:
            self.table.setUpdatesEnabled(True)

    def _set_table_row(self, row_idx, med):
        fields = ['id', 'name', 'alias', 'category', 'nature', 'taste', 'meridian']
        for col_idx, field in enumerate(fields):
            value = med.get(field, '')
            item = QTableWidgetItem(str(value) if value else '')
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, col_idx, item)

    def add_medicine(self):
        dialog = MedicineDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, '提示', '请输入药材名称！')
                return
            try:
                self.db.execute('''
                    INSERT INTO medicines (name, alias, category, nature, taste, meridian, 
                                         efficacy, indications, usage, dosage, contraindication, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
                med_id = self.db.fetchone("SELECT id FROM medicines WHERE name = ?", (data[0],))[0]
                self.db.execute(
                    "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes) VALUES (?, 0, 'g', 0, 10, '')",
                    (med_id,))
                
                new_med = {
                    'id': med_id,
                    'name': data[0],
                    'alias': data[1],
                    'category': data[2],
                    'nature': data[3],
                    'taste': data[4],
                    'meridian': data[5],
                    'efficacy': data[6],
                    'indications': data[7],
                    'usage': data[8],
                    'dosage': data[9],
                    'contraindication': data[10],
                    'notes': data[11]
                }
                self._cache.add_medicine(new_med)
                
                QMessageBox.information(self, '成功', '药材添加成功！')
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')

    def edit_medicine(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        medicine_data = self._full_data[row]

        dialog = MedicineDialog(self, medicine_data)
        if dialog.exec_():
            data = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, '提示', '请输入药材名称！')
                return
            med_id = medicine_data['id']
            self.db.execute('''
                UPDATE medicines SET name=?, alias=?, category=?, nature=?, taste=?, meridian=?, 
                                   efficacy=?, indications=?, usage=?, dosage=?, contraindication=?, notes=? 
                WHERE id=?
            ''', (*data, med_id))
            
            updated_med = {
                'id': med_id,
                'name': data[0],
                'alias': data[1],
                'category': data[2],
                'nature': data[3],
                'taste': data[4],
                'meridian': data[5],
                'efficacy': data[6],
                'indications': data[7],
                'usage': data[8],
                'dosage': data[9],
                'contraindication': data[10],
                'notes': data[11]
            }
            self._cache.update_medicine(updated_med)
            
            QMessageBox.information(self, '成功', '修改成功！')
            self.load_data()

    def del_medicine(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        med_id = self._full_data[row]['id']
        med_name = self._full_data[row]['name']

        reply = QMessageBox.question(self, '确认', f'确定要删除药材 "{med_name}" 吗？\n此操作将同时删除库存记录！', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.execute("DELETE FROM inventory WHERE medicine_id = ?", (med_id,))
            self.db.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
            self._cache.delete_medicine(med_id)
            QMessageBox.information(self, '成功', '删除成功！')
            self.load_data()

    def view_detail(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        medicine_data = self._full_data[row]
        
        detail_text = f'''
        <h2 style="color: #409eff;">{medicine_data['name']}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; background: #f5f7fa;"><b>别名</b></td><td style="padding: 8px;">{medicine_data['alias'] or '无'}</td></tr>
            <tr><td style="padding: 8px; background: #f5f7fa;"><b>分类</b></td><td style="padding: 8px;">{medicine_data['category'] or '未分类'}</td></tr>
            <tr><td style="padding: 8px; background: #f5f7fa;"><b>药性</b></td><td style="padding: 8px;">{medicine_data['nature'] or '未知'}</td></tr>
            <tr><td style="padding: 8px; background: #f5f7fa;"><b>药味</b></td><td style="padding: 8px;">{medicine_data['taste'] or '未知'}</td></tr>
            <tr><td style="padding: 8px; background: #f5f7fa;"><b>归经</b></td><td style="padding: 8px;">{medicine_data['meridian'] or '未知'}</td></tr>
        </table>
        <hr style="margin: 15px 0;">
        <h3 style="color: #67c23a;">功效</h3>
        <p style="padding: 10px; background: #f0f9eb; border-radius: 5px;">{medicine_data['efficacy'] or '暂无'}</p>
        <h3 style="color: #409eff;">主治</h3>
        <p style="padding: 10px; background: #ecf5ff; border-radius: 5px;">{medicine_data['indications'] or '暂无'}</p>
        <h3 style="color: #e6a23c;">用法用量</h3>
        <p style="padding: 10px; background: #fdf6ec; border-radius: 5px;">{medicine_data['usage'] or '暂无'} | {medicine_data['dosage'] or '暂无'}</p>
        <h3 style="color: #f56c6c;">禁忌</h3>
        <p style="padding: 10px; background: #fef0f0; border-radius: 5px;">{medicine_data['contraindication'] or '暂无'}</p>
        <h3 style="color: #909399;">备注</h3>
        <p style="padding: 10px; background: #f4f4f5; border-radius: 5px;">{medicine_data['notes'] or '无'}</p>
        '''
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('药材详情')
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(detail_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setMinimumWidth(500)
        msg_box.exec_()

    def export_data(self):
        try:
            import csv
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(self, '导出药材数据', '', 'CSV文件 (*.csv)')
            if filename:
                rows = self._cache.get_all()
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '名称', '别名', '分类', '药性', '药味', '归经', 
                                    '功效', '主治', '用法', '用量', '禁忌', '备注'])
                    for row in rows:
                        writer.writerow([
                            row['id'], row['name'], row['alias'], row['category'],
                            row['nature'], row['taste'], row['meridian'],
                            row['efficacy'], row['indications'], row['usage'],
                            row['dosage'], row['contraindication'], row['notes']
                        ])
                QMessageBox.information(self, '成功', '数据导出成功！')
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
        
        self.table.setStyleSheet(f'''
            QTableWidget {{
                gridline-color: #e0e0e0;
                font-size: {config['font_size']}px;
            }}
            QTableWidget::item {{
                padding: {config['cell_padding']}px;
            }}
            QHeaderView::section {{
                font-size: {config['header_font_size']}px;
                font-weight: bold;
                padding: {config['cell_padding']}px;
                background-color: #f5f7fa;
                border: none;
                border-bottom: 2px solid #e0e0e0;
            }}
        ''')
        
        if hasattr(self, 'stats_label'):
            self.stats_label.setStyleSheet(f'color: #666; font-size: {self._font_manager.get_font_size("small")}px;')
    
    def update_fonts(self):
        self._apply_responsive_table()
        self.load_data()
