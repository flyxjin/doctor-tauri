# -*- coding: utf-8 -*-
"""
处方模板管理视图 - Windows 7兼容版本
支持常用处方保存为模板，快速调用
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QLineEdit,
                             QTextEdit, QMessageBox, QComboBox, QGroupBox,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging

logger = logging.getLogger('MedicineSystem')


class TemplateDialog(QDialog):
    """处方模板编辑对话框"""
    
    def __init__(self, parent=None, template_data=None, db=None):
        super().__init__(parent)
        self.db = db
        self.template_data = template_data
        self.setWindowTitle('处方模板')
        self.setFixedWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
        
        if template_data:
            self._populate_fields(template_data)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入模板名称')
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(['通用', '感冒', '消化系统', '心血管', '妇科', '儿科', '其他'])
        
        self.diagnosis_edit = QLineEdit()
        self.diagnosis_edit.setPlaceholderText('请输入诊断')
        
        self.medicines_edit = QTextEdit()
        self.medicines_edit.setPlaceholderText('每行一味药材，格式：药材名 数量\n例如：\n黄芪 30\n当归 15\n白术 20')
        self.medicines_edit.setMinimumHeight(150)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText('备注信息（可选）')
        self.notes_edit.setMaximumHeight(80)
        
        form_layout.addRow('模板名称*:', self.name_edit)
        form_layout.addRow('分类:', self.category_combo)
        form_layout.addRow('诊断:', self.diagnosis_edit)
        form_layout.addRow('药材组成*:', self.medicines_edit)
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
            
            index = self.category_combo.findText(data.get('category', '通用'))
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            self.diagnosis_edit.setText(data.get('diagnosis', ''))
            self.medicines_edit.setPlainText(data.get('medicines', ''))
            self.notes_edit.setPlainText(data.get('notes', ''))
    
    def get_data(self) -> dict:
        return {
            'name': self.name_edit.text().strip(),
            'category': self.category_combo.currentText(),
            'diagnosis': self.diagnosis_edit.text().strip(),
            'medicines': self.medicines_edit.toPlainText().strip(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class PrescriptionTemplateView(QWidget):
    """处方模板管理视图"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._ensure_table()
        self.init_ui()
        self.load_data()
    
    def _ensure_table(self):
        try:
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS prescription_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT '通用',
                    diagnosis TEXT,
                    medicines TEXT NOT NULL,
                    notes TEXT,
                    use_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        except Exception as e:
            logger.error(f"创建处方模板表失败: {e}")
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        title_label = QLabel('处方模板管理')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #000000;')
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(['全部分类', '通用', '感冒', '消化系统', '心血管', '妇科', '儿科', '其他'])
        self.category_filter.currentIndexChanged.connect(self.load_data)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel('分类筛选:'))
        header_layout.addWidget(self.category_filter)
        
        layout.addLayout(header_layout)
        
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('新建模板')
        self.add_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 8px 16px;')
        self.add_btn.clicked.connect(self.add_template)
        
        self.edit_btn = QPushButton('编辑模板')
        self.edit_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 1px solid #000000; padding: 8px 16px;')
        self.edit_btn.clicked.connect(self.edit_template)
        
        self.delete_btn = QPushButton('删除模板')
        self.delete_btn.setStyleSheet('background-color: #ffffff; color: #ff4d4f; border: 1px solid #ff4d4f; padding: 8px 16px;')
        self.delete_btn.clicked.connect(self.delete_template)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', '模板名称', '分类', '诊断', '使用次数'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(4, 80)
        
        layout.addWidget(self.table)
        
        detail_group = QGroupBox('模板详情')
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_label = QLabel('请选择一个模板查看详情')
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet('padding: 10px; background-color: #f5f5f5; border-radius: 4px;')
        self.detail_label.setMinimumHeight(120)
        
        detail_layout.addWidget(self.detail_label)
        layout.addWidget(detail_group)
        
        self.table.itemSelectionChanged.connect(self.show_detail)
    
    def load_data(self):
        try:
            category = self.category_filter.currentText()
            
            if category == '全部分类':
                rows = self.db.fetchall(
                    "SELECT * FROM prescription_templates ORDER BY use_count DESC, created_at DESC"
                )
            else:
                rows = self.db.fetchall(
                    "SELECT * FROM prescription_templates WHERE category = ? ORDER BY use_count DESC, created_at DESC",
                    (category,)
                )
            
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                if isinstance(row, dict):
                    data = [
                        row.get('id', ''),
                        row.get('name', ''),
                        row.get('category', ''),
                        row.get('diagnosis', ''),
                        row.get('use_count', 0)
                    ]
                else:
                    data = [row[0], row[1], row[2], row[3], row[7] if len(row) > 7 else 0]
                
                for j, value in enumerate(data):
                    item = QTableWidgetItem(str(value) if value else '')
                    self.table.setItem(i, j, item)
                    
        except Exception as e:
            logger.error(f"加载处方模板失败: {e}")
    
    def add_template(self):
        dialog = TemplateDialog(self, db=self.db)
        if dialog.exec_():
            data = dialog.get_data()
            
            if not data['name']:
                QMessageBox.warning(self, '提示', '请输入模板名称')
                return
            
            if not data['medicines']:
                QMessageBox.warning(self, '提示', '请输入药材组成')
                return
            
            try:
                self.db.execute('''
                    INSERT INTO prescription_templates (name, category, diagnosis, medicines, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data['name'], data['category'], data['diagnosis'], data['medicines'], data['notes']))
                
                QMessageBox.information(self, '成功', '模板添加成功')
                self.load_data()
                
            except Exception as e:
                logger.error(f"添加处方模板失败: {e}")
                QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')
    
    def edit_template(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个模板')
            return
        
        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        
        template_data = self.db.fetchone(
            "SELECT * FROM prescription_templates WHERE id = ?",
            (template_id,)
        )
        
        if not template_data:
            QMessageBox.warning(self, '错误', '未找到模板')
            return
        
        dialog = TemplateDialog(self, template_data=template_data, db=self.db)
        if dialog.exec_():
            data = dialog.get_data()
            
            if not data['name']:
                QMessageBox.warning(self, '提示', '请输入模板名称')
                return
            
            if not data['medicines']:
                QMessageBox.warning(self, '提示', '请输入药材组成')
                return
            
            try:
                self.db.execute('''
                    UPDATE prescription_templates 
                    SET name=?, category=?, diagnosis=?, medicines=?, notes=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (data['name'], data['category'], data['diagnosis'], data['medicines'], data['notes'], template_id))
                
                QMessageBox.information(self, '成功', '模板更新成功')
                self.load_data()
                
            except Exception as e:
                logger.error(f"更新处方模板失败: {e}")
                QMessageBox.warning(self, '错误', f'更新失败: {str(e)}')
    
    def delete_template(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个模板')
            return
        
        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        template_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除模板 "{template_name}" 吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute("DELETE FROM prescription_templates WHERE id = ?", (template_id,))
                QMessageBox.information(self, '成功', '模板删除成功')
                self.load_data()
                self.detail_label.setText('请选择一个模板查看详情')
                
            except Exception as e:
                logger.error(f"删除处方模板失败: {e}")
                QMessageBox.warning(self, '错误', f'删除失败: {str(e)}')
    
    def show_detail(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        
        template_data = self.db.fetchone(
            "SELECT * FROM prescription_templates WHERE id = ?",
            (template_id,)
        )
        
        if template_data:
            if isinstance(template_data, dict):
                name = template_data.get('name', '')
                category = template_data.get('category', '')
                diagnosis = template_data.get('diagnosis', '')
                medicines = template_data.get('medicines', '')
                notes = template_data.get('notes', '')
            else:
                name = template_data[1]
                category = template_data[2]
                diagnosis = template_data[3]
                medicines = template_data[4]
                notes = template_data[5] if len(template_data) > 5 else ''
            
            detail_text = f'''
<b>模板名称:</b> {name}<br>
<b>分类:</b> {category}<br>
<b>诊断:</b> {diagnosis}<br>
<b>药材组成:</b><br>
<pre style="background-color: #fff; padding: 8px; border-radius: 4px; margin: 5px 0;">{medicines}</pre>
'''
            if notes:
                detail_text += f'<b>备注:</b> {notes}'
            
            self.detail_label.setText(detail_text)
    
    def get_template_for_prescription(self, template_id: int) -> dict:
        """获取模板数据用于处方开具"""
        template_data = self.db.fetchone(
            "SELECT * FROM prescription_templates WHERE id = ?",
            (template_id,)
        )
        
        if template_data:
            if isinstance(template_data, dict):
                return {
                    'diagnosis': template_data.get('diagnosis', ''),
                    'medicines': template_data.get('medicines', '')
                }
            else:
                return {
                    'diagnosis': template_data[3] if len(template_data) > 3 else '',
                    'medicines': template_data[4] if len(template_data) > 4 else ''
                }
        return None
    
    def increment_use_count(self, template_id: int):
        """增加模板使用次数"""
        try:
            self.db.execute(
                "UPDATE prescription_templates SET use_count = use_count + 1 WHERE id = ?",
                (template_id,)
            )
        except Exception as e:
            logger.error(f"更新模板使用次数失败: {e}")
