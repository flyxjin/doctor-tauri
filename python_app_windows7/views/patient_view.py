# -*- coding: utf-8 -*-
"""
患者管理视图 - Windows 7兼容版本
支持患者信息记录、历史处方关联
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QLineEdit,
                             QSpinBox, QComboBox, QTextEdit, QMessageBox,
                             QGroupBox, QTabWidget)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger('MedicineSystem')


class PatientDialog(QDialog):
    """患者信息编辑对话框"""
    
    def __init__(self, parent=None, patient_data=None):
        super().__init__(parent)
        self.patient_data = patient_data
        self.setWindowTitle('患者信息')
        self.setFixedWidth(450)
        self.init_ui()
        
        if patient_data:
            self._populate_fields(patient_data)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入患者姓名')
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['男', '女'])
        
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 150)
        self.age_spin.setValue(0)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText('请输入联系电话')
        
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText('请输入地址（可选）')
        
        self.allergy_edit = QTextEdit()
        self.allergy_edit.setPlaceholderText('请输入过敏史（可选）')
        self.allergy_edit.setMaximumHeight(60)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText('备注信息（可选）')
        self.notes_edit.setMaximumHeight(60)
        
        form_layout.addRow('姓名*:', self.name_edit)
        form_layout.addRow('性别:', self.gender_combo)
        form_layout.addRow('年龄:', self.age_spin)
        form_layout.addRow('电话:', self.phone_edit)
        form_layout.addRow('地址:', self.address_edit)
        form_layout.addRow('过敏史:', self.allergy_edit)
        form_layout.addRow('备注:', self.notes_edit)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton('保存')
        self.save_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 8px 24px;')
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setStyleSheet('background-color: #ffffff; color: #666666; border: 1px solid #e0e0e0; padding: 8px 24px;')
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _populate_fields(self, data):
        if isinstance(data, dict):
            self.name_edit.setText(data.get('name', ''))
            
            gender = data.get('gender', '男')
            index = self.gender_combo.findText(gender)
            if index >= 0:
                self.gender_combo.setCurrentIndex(index)
            
            self.age_spin.setValue(data.get('age', 0))
            self.phone_edit.setText(data.get('phone', ''))
            self.address_edit.setText(data.get('address', ''))
            self.allergy_edit.setPlainText(data.get('allergy', ''))
            self.notes_edit.setPlainText(data.get('notes', ''))
    
    def get_data(self) -> dict:
        return {
            'name': self.name_edit.text().strip(),
            'gender': self.gender_combo.currentText(),
            'age': self.age_spin.value(),
            'phone': self.phone_edit.text().strip(),
            'address': self.address_edit.text().strip(),
            'allergy': self.allergy_edit.toPlainText().strip(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class PatientView(QWidget):
    """患者管理主视图"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._ensure_table()
        self.init_ui()
        self.load_data()
    
    def _ensure_table(self):
        try:
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    gender TEXT DEFAULT '男',
                    age INTEGER DEFAULT 0,
                    phone TEXT,
                    address TEXT,
                    allergy TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        except Exception as e:
            logger.error(f"创建患者表失败: {e}")
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        title_label = QLabel('患者管理')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #000000;')
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索患者姓名或电话...')
        self.search_input.setMinimumWidth(200)
        self.search_input.textChanged.connect(self.search_patient)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        
        layout.addLayout(header_layout)
        
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('添加患者')
        self.add_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 8px 16px;')
        self.add_btn.clicked.connect(self.add_patient)
        
        self.edit_btn = QPushButton('编辑信息')
        self.edit_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 1px solid #000000; padding: 8px 16px;')
        self.edit_btn.clicked.connect(self.edit_patient)
        
        self.delete_btn = QPushButton('删除患者')
        self.delete_btn.setStyleSheet('background-color: #ffffff; color: #ff4d4f; border: 1px solid #ff4d4f; padding: 8px 16px;')
        self.delete_btn.clicked.connect(self.delete_patient)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', '姓名', '性别', '年龄', '电话', '地址', '处方数'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(6, 80)
        
        layout.addWidget(self.table)
        
        history_group = QGroupBox('历史处方')
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(['处方ID', '诊断', '金额', '开具时间'])
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setMaximumHeight(200)
        
        history_layout.addWidget(self.history_table)
        layout.addWidget(history_group)
        
        self.table.itemSelectionChanged.connect(self.show_history)
    
    def load_data(self):
        try:
            rows = self.db.fetchall('''
                SELECT p.*, 
                       (SELECT COUNT(*) FROM prescriptions WHERE patient_name = p.name) as prescription_count
                FROM patients p
                ORDER BY p.created_at DESC
            ''')
            
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                if isinstance(row, dict):
                    data = [
                        row.get('id', ''),
                        row.get('name', ''),
                        row.get('gender', ''),
                        row.get('age', 0),
                        row.get('phone', ''),
                        row.get('address', ''),
                        row.get('prescription_count', 0)
                    ]
                else:
                    data = [row[0], row[1], row[2], row[3], row[4], row[5], row[8] if len(row) > 8 else 0]
                
                for j, value in enumerate(data):
                    item = QTableWidgetItem(str(value) if value else '')
                    self.table.setItem(i, j, item)
                    
        except Exception as e:
            logger.error(f"加载患者数据失败: {e}")
    
    def search_patient(self, keyword: str):
        if not keyword:
            self.load_data()
            return
        
        try:
            rows = self.db.fetchall('''
                SELECT p.*, 
                       (SELECT COUNT(*) FROM prescriptions WHERE patient_name = p.name) as prescription_count
                FROM patients p
                WHERE p.name LIKE ? OR p.phone LIKE ?
                ORDER BY p.created_at DESC
            ''', (f'%{keyword}%', f'%{keyword}%'))
            
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                if isinstance(row, dict):
                    data = [
                        row.get('id', ''),
                        row.get('name', ''),
                        row.get('gender', ''),
                        row.get('age', 0),
                        row.get('phone', ''),
                        row.get('address', ''),
                        row.get('prescription_count', 0)
                    ]
                else:
                    data = [row[0], row[1], row[2], row[3], row[4], row[5], row[8] if len(row) > 8 else 0]
                
                for j, value in enumerate(data):
                    item = QTableWidgetItem(str(value) if value else '')
                    self.table.setItem(i, j, item)
                    
        except Exception as e:
            logger.error(f"搜索患者失败: {e}")
    
    def add_patient(self):
        dialog = PatientDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            
            if not data['name']:
                QMessageBox.warning(self, '提示', '请输入患者姓名')
                return
            
            try:
                self.db.execute('''
                    INSERT INTO patients (name, gender, age, phone, address, allergy, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['name'], data['gender'], data['age'], data['phone'], 
                      data['address'], data['allergy'], data['notes']))
                
                QMessageBox.information(self, '成功', '患者添加成功')
                self.load_data()
                
            except Exception as e:
                logger.error(f"添加患者失败: {e}")
                QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')
    
    def edit_patient(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个患者')
            return
        
        row = selected[0].row()
        patient_id = self.table.item(row, 0).text()
        
        patient_data = self.db.fetchone(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,)
        )
        
        if not patient_data:
            QMessageBox.warning(self, '错误', '未找到患者')
            return
        
        dialog = PatientDialog(self, patient_data=patient_data)
        if dialog.exec_():
            data = dialog.get_data()
            
            try:
                self.db.execute('''
                    UPDATE patients 
                    SET name=?, gender=?, age=?, phone=?, address=?, allergy=?, notes=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (data['name'], data['gender'], data['age'], data['phone'],
                      data['address'], data['allergy'], data['notes'], patient_id))
                
                QMessageBox.information(self, '成功', '患者信息更新成功')
                self.load_data()
                
            except Exception as e:
                logger.error(f"更新患者信息失败: {e}")
                QMessageBox.warning(self, '错误', f'更新失败: {str(e)}')
    
    def delete_patient(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个患者')
            return
        
        row = selected[0].row()
        patient_id = self.table.item(row, 0).text()
        patient_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除患者 "{patient_name}" 吗？\n此操作不会删除关联的处方记录。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                QMessageBox.information(self, '成功', '患者删除成功')
                self.load_data()
                self.history_table.setRowCount(0)
                
            except Exception as e:
                logger.error(f"删除患者失败: {e}")
                QMessageBox.warning(self, '错误', f'删除失败: {str(e)}')
    
    def show_history(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        patient_name = self.table.item(row, 1).text()
        
        try:
            rows = self.db.fetchall('''
                SELECT id, diagnosis, total_amount, created_at
                FROM prescriptions
                WHERE patient_name = ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (patient_name,))
            
            self.history_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                if isinstance(row, dict):
                    data = [
                        row.get('id', ''),
                        row.get('diagnosis', ''),
                        row.get('total_amount', 0),
                        row.get('created_at', '')
                    ]
                else:
                    data = [row[0], row[3], row[5], row[7]]
                
                for j, value in enumerate(data):
                    if j == 2:
                        value = f'¥{value:.2f}' if value else '¥0.00'
                    item = QTableWidgetItem(str(value) if value else '')
                    self.history_table.setItem(i, j, item)
                    
        except Exception as e:
            logger.error(f"加载患者历史处方失败: {e}")
    
    def get_patient_suggestions(self, keyword: str) -> list:
        """获取患者姓名建议列表（用于处方开具自动补全）"""
        try:
            rows = self.db.fetchall(
                "SELECT name, gender, age, phone FROM patients WHERE name LIKE ? LIMIT 10",
                (f'%{keyword}%',)
            )
            
            suggestions = []
            for row in rows:
                if isinstance(row, dict):
                    suggestions.append({
                        'name': row.get('name', ''),
                        'gender': row.get('gender', ''),
                        'age': row.get('age', 0),
                        'phone': row.get('phone', '')
                    })
                else:
                    suggestions.append({
                        'name': row[0],
                        'gender': row[1],
                        'age': row[2],
                        'phone': row[3]
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"获取患者建议失败: {e}")
            return []
