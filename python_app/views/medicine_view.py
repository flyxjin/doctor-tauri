from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit,
                             QDialog, QFormLayout, QMessageBox, QComboBox,
                             QTextEdit, QSplitter, QGroupBox, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


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
            self.name_edit.setText(self.medicine_data[1] or '')
            self.alias_edit.setText(self.medicine_data[2] or '')
            index = self.category_combo.findText(self.medicine_data[3] or '')
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            index = self.nature_combo.findText(self.medicine_data[4] or '')
            if index >= 0:
                self.nature_combo.setCurrentIndex(index)
            self.taste_edit.setText(self.medicine_data[5] or '')
            self.meridian_edit.setText(self.medicine_data[6] or '')
            self.efficacy_edit.setText(self.medicine_data[7] or '')
            self.indications_edit.setText(self.medicine_data[8] or '')
            self.usage_edit.setText(self.medicine_data[9] or '')
            self.dosage_edit.setText(self.medicine_data[10] or '')
            self.contraindication_edit.setText(self.medicine_data[11] or '')
            self.notes_edit.setText(self.medicine_data[12] or '')

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


class MedicineView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 顶部搜索和筛选栏
        search_group = QGroupBox('搜索与筛选')
        search_layout = QHBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入药材名称、别名或功效搜索...')
        self.search_input.setMinimumWidth(300)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(['全部分类', '补虚药', '解表药', '清热药', '泻下药', '祛风湿药', '化湿药', '利水渗湿药', '温里药', '理气药', '消食药', '驱虫药', '止血药', '活血化瘀药', '化痰止咳平喘药', '安神药', '平肝息风药', '开窍药', '收涩药', '攻毒杀虫止痒药', '拔毒化腐生肌药'])
        
        self.nature_filter = QComboBox()
        self.nature_filter.addItems(['全部药性', '寒', '热', '温', '凉', '平'])
        
        self.search_btn = QPushButton('搜索')
        self.reset_btn = QPushButton('重置')
        self.search_btn.clicked.connect(self.load_data)
        self.reset_btn.clicked.connect(self.reset_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(self.nature_filter)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)
        search_layout.addStretch()

        # 操作按钮
        btn_bar = QHBoxLayout()
        self.add_btn = QPushButton('添加药材')
        self.edit_btn = QPushButton('修改信息')
        self.del_btn = QPushButton('删除药材')
        self.view_detail_btn = QPushButton('查看详情')
        self.export_btn = QPushButton('导出数据')
        
        self.add_btn.setStyleSheet('background-color: #67c23a;')
        self.edit_btn.setStyleSheet('background-color: #e6a23c;')
        self.del_btn.setStyleSheet('background-color: #f56c6c;')
        
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

        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            'ID', '名称', '别名', '分类', '药性', '药味', '归经', 
            '功效', '主治', '用法', '用量', '禁忌', '备注'
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 60)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 200)
        self.table.setColumnWidth(8, 200)
        self.table.setColumnWidth(9, 80)
        self.table.setColumnWidth(10, 100)
        self.table.setColumnWidth(11, 150)
        self.table.setColumnWidth(12, 100)
        
        # 统计信息
        self.stats_label = QLabel('共 0 味药材')
        self.stats_label.setStyleSheet('color: #666; font-size: 12px;')

        layout.addWidget(search_group)
        layout.addLayout(btn_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.stats_label)

    def reset_search(self):
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.nature_filter.setCurrentIndex(0)
        self.load_data()

    def load_data(self):
        keyword = self.search_input.text()
        category = self.category_filter.currentText()
        nature = self.nature_filter.currentText()
        
        query = "SELECT * FROM medicines WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND (name LIKE ? OR alias LIKE ? OR efficacy LIKE ?)"
            params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
        
        if category != '全部分类':
            query += " AND category = ?"
            params.append(category)
        
        if nature != '全部药性':
            query += " AND nature = ?"
            params.append(nature)
        
        rows = self.db.fetchall(query, params)
        
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data) if col_data else '')
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
        
        self.stats_label.setText(f'共 {len(rows)} 味药材')

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
        medicine_data = [self.table.item(row, col).text() if self.table.item(row, col) else '' 
                         for col in range(self.table.columnCount())]

        dialog = MedicineDialog(self, medicine_data)
        if dialog.exec_():
            data = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, '提示', '请输入药材名称！')
                return
            med_id = medicine_data[0]
            self.db.execute('''
                UPDATE medicines SET name=?, alias=?, category=?, nature=?, taste=?, meridian=?, 
                                   efficacy=?, indications=?, usage=?, dosage=?, contraindication=?, notes=? 
                WHERE id=?
            ''', (*data, med_id))
            QMessageBox.information(self, '成功', '修改成功！')
            self.load_data()

    def del_medicine(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        med_id = self.table.item(row, 0).text()
        med_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(self, '确认', f'确定要删除药材 "{med_name}" 吗？\n此操作将同时删除库存记录！', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.execute("DELETE FROM inventory WHERE medicine_id = ?", (med_id,))
            self.db.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
            QMessageBox.information(self, '成功', '删除成功！')
            self.load_data()

    def view_detail(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        medicine_data = [self.table.item(row, col).text() if self.table.item(row, col) else '' 
                         for col in range(self.table.columnCount())]
        
        detail_text = f'''
        <h2 style="color: #409eff;">{medicine_data[1]}</h2>
        <p><b>别名：</b>{medicine_data[2] or '无'}</p>
        <p><b>分类：</b>{medicine_data[3] or '未分类'}</p>
        <p><b>药性：</b>{medicine_data[4] or '未知'}</p>
        <p><b>药味：</b>{medicine_data[5] or '未知'}</p>
        <p><b>归经：</b>{medicine_data[6] or '未知'}</p>
        <hr>
        <p><b>功效：</b><br>{medicine_data[7] or '暂无'}</p>
        <p><b>主治：</b><br>{medicine_data[8] or '暂无'}</p>
        <p><b>用法：</b>{medicine_data[9] or '暂无'}</p>
        <p><b>用量：</b>{medicine_data[10] or '暂无'}</p>
        <p><b>禁忌：</b><br>{medicine_data[11] or '暂无'}</p>
        <p><b>备注：</b>{medicine_data[12] or '无'}</p>
        '''
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('药材详情')
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(detail_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def export_data(self):
        try:
            import csv
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(self, '导出药材数据', '', 'CSV文件 (*.csv)')
            if filename:
                rows = self.db.fetchall("SELECT * FROM medicines")
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '名称', '别名', '分类', '药性', '药味', '归经', 
                                    '功效', '主治', '用法', '用量', '禁忌', '备注'])
                    for row in rows:
                        writer.writerow(row)
                QMessageBox.information(self, '成功', '数据导出成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'导出失败: {str(e)}')
