# -*- coding: utf-8 -*-
"""
处方开具视图 - Windows 7兼容版本
支持患者信息智能复用和处方模板
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem,
                             QPushButton, QMessageBox, QTextEdit, QLabel, QComboBox,
                             QInputDialog, QHeaderView, QFrame, QCompleter, QGroupBox,
                             QSplitter, QDialog, QListWidget, QListWidgetItem)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from datetime import datetime
import json
import logging

logger = logging.getLogger('MedicineSystem')


class PatientSelector(QComboBox):
    """患者选择器 - 支持搜索和自动完成"""
    
    patient_selected = pyqtSignal(dict)
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._patients_cache = []
        self._is_searching = False
        self.setEditable(True)
        self.setPlaceholderText('输入姓名搜索患者...')
        self._setup_completer()
        self.currentIndexChanged.connect(self._on_patient_selected)
        self.lineEdit().textEdited.connect(self._search_patients)
        
    def _setup_completer(self):
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(self.completer)
        
    def _search_patients(self, text):
        if len(text) < 1:
            return
        self._is_searching = True
        try:
            rows = self.db.fetchall(
                "SELECT id, name, gender, age, phone, allergy, notes FROM patients WHERE name LIKE ? ORDER BY created_at DESC LIMIT 20",
                (f'%{text}%',)
            )
            self._patients_cache = rows
            self.blockSignals(True)
            self.clear()
            self.addItem('-- 新患者 --', None)
            for row in rows:
                patient_id = row.get('id') if isinstance(row, dict) else row[0]
                name = row.get('name', '') if isinstance(row, dict) else row[1]
                gender = row.get('gender', '') if isinstance(row, dict) else row[2]
                age = row.get('age', '') if isinstance(row, dict) else row[3]
                display_text = f"{name} ({gender}, {age}岁)"
                self.addItem(display_text, patient_id)
            self.blockSignals(False)
            self.showPopup()
        except Exception as e:
            logger.error(f"搜索患者失败: {e}")
        finally:
            self._is_searching = False
            
    def _on_patient_selected(self, index):
        if self._is_searching:
            return
        if index == 0:
            self.patient_selected.emit({})
            return
        if index > 0 and index <= len(self._patients_cache):
            patient = self._patients_cache[index - 1]
            if isinstance(patient, dict):
                self.patient_selected.emit(patient)
            else:
                keys = ['id', 'name', 'gender', 'age', 'phone', 'allergy', 'notes']
                self.patient_selected.emit(dict(zip(keys, patient)))
                
    def get_selected_patient_id(self):
        data = self.currentData()
        return data if data else None
    
    def clear_selection(self):
        self.blockSignals(True)
        self.setCurrentIndex(0)
        self.blockSignals(False)


class TemplateSelectorDialog(QDialog):
    """处方模板选择对话框"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_template = None
        self.setWindowTitle('选择处方模板')
        self.setMinimumSize(600, 400)
        self._init_ui()
        self._load_templates()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('搜索:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入模板名称搜索...')
        self.search_input.textChanged.connect(self._filter_templates)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        content_layout = QHBoxLayout()
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_clicked)
        content_layout.addWidget(self.template_list, 1)
        
        preview_group = QGroupBox('模板预览')
        preview_layout = QVBoxLayout(preview_group)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        content_layout.addWidget(preview_group, 1)
        
        layout.addLayout(content_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.use_btn = QPushButton('使用模板')
        self.use_btn.setEnabled(False)
        self.use_btn.clicked.connect(self._use_template)
        self.use_btn.setStyleSheet('''
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:disabled {
                background-color: #d9d9d9;
            }
        ''')
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.use_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def _load_templates(self):
        try:
            templates = self.db.fetchall(
                "SELECT id, name, category, diagnosis, medicines, notes FROM prescription_templates ORDER BY use_count DESC"
            )
            self._templates_cache = templates
            self._display_templates(templates)
        except Exception as e:
            logger.error(f"加载处方模板失败: {e}")
            
    def _display_templates(self, templates):
        self.template_list.clear()
        for t in templates:
            if isinstance(t, dict):
                item = QListWidgetItem(f"{t.get('name', '')} [{t.get('category', '未分类')}]")
                item.setData(Qt.UserRole, t)
            else:
                item = QListWidgetItem(f"{t[1]} [{t[2] or '未分类'}]")
                keys = ['id', 'name', 'category', 'diagnosis', 'medicines', 'notes']
                item.setData(Qt.UserRole, dict(zip(keys, t)))
            self.template_list.addItem(item)
            
    def _filter_templates(self, text):
        if not text:
            self._display_templates(self._templates_cache)
            return
        filtered = [t for t in self._templates_cache if text.lower() in (t.get('name', '') if isinstance(t, dict) else t[1]).lower()]
        self._display_templates(filtered)
        
    def _on_template_clicked(self, item):
        template = item.data(Qt.UserRole)
        self.selected_template = template
        self.use_btn.setEnabled(True)
        
        preview = f"<b>模板名称:</b> {template.get('name', '')}<br>"
        preview += f"<b>分类:</b> {template.get('category', '未分类')}<br>"
        preview += f"<b>诊断:</b> {template.get('diagnosis', '')}<br><br>"
        preview += "<b>药材列表:</b><br>"
        
        medicines_text = template.get('medicines', '')
        if medicines_text:
            for line in medicines_text.strip().split('\n'):
                line = line.strip()
                if line:
                    preview += f"• {line}<br>"
        else:
            preview += "（无药材）"
            
        if template.get('notes'):
            preview += f"<br><b>备注:</b> {template.get('notes')}"
            
        self.preview_text.setHtml(preview)
        
    def _use_template(self):
        if self.selected_template:
            try:
                self.db.execute(
                    "UPDATE prescription_templates SET use_count = use_count + 1 WHERE id = ?",
                    (self.selected_template.get('id'),)
                )
            except:
                pass
            self.accept()


class PrescriptionView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cart = []
        self._current_patient_id = None
        self._current_patient_allergy = ''
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)
        
        patient_group = QGroupBox("患者信息")
        patient_group.setMinimumHeight(280)
        patient_group.setStyleSheet('''
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #1890ff;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                padding-left: 8px;
                padding-right: 8px;
                padding-bottom: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #1890ff;
            }
        ''')
        patient_layout = QVBoxLayout(patient_group)
        patient_layout.setSpacing(8)
        
        patient_select_layout = QHBoxLayout()
        patient_select_layout.setSpacing(8)
        select_label = QLabel('选择患者:')
        select_label.setMinimumWidth(70)
        select_label.setStyleSheet('font-weight: bold;')
        patient_select_layout.addWidget(select_label)
        
        self.patient_selector = PatientSelector(self.db)
        self.patient_selector.patient_selected.connect(self._on_patient_selected)
        self.patient_selector.setMinimumHeight(32)
        patient_select_layout.addWidget(self.patient_selector, 1)
        
        new_patient_btn = QPushButton('新建')
        new_patient_btn.setFixedSize(60, 32)
        new_patient_btn.setStyleSheet('''
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        ''')
        new_patient_btn.clicked.connect(self._clear_patient_form)
        patient_select_layout.addWidget(new_patient_btn)
        
        patient_layout.addLayout(patient_select_layout)
        
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(12)
        
        left_form = QFormLayout()
        left_form.setSpacing(6)
        left_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.patient_name = QLineEdit()
        self.patient_name.setPlaceholderText('必填')
        self.patient_name.setMinimumHeight(28)
        
        self.patient_age = QSpinBox()
        self.patient_age.setRange(0, 150)
        self.patient_age.setMinimumHeight(28)
        self.patient_age.setMinimumWidth(80)
        
        self.patient_gender = QComboBox()
        self.patient_gender.addItems(['男', '女'])
        self.patient_gender.setMinimumHeight(28)
        self.patient_gender.setMinimumWidth(80)
        
        name_label = QLabel('姓名:')
        name_label.setStyleSheet('font-weight: bold;')
        age_label = QLabel('年龄:')
        gender_label = QLabel('性别:')
        
        left_form.addRow(name_label, self.patient_name)
        left_form.addRow(age_label, self.patient_age)
        left_form.addRow(gender_label, self.patient_gender)
        
        right_form = QFormLayout()
        right_form.setSpacing(6)
        right_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.patient_phone = QLineEdit()
        self.patient_phone.setPlaceholderText('选填')
        self.patient_phone.setMinimumHeight(28)
        
        self.allergy_display = QLineEdit()
        self.allergy_display.setPlaceholderText('无')
        self.allergy_display.setReadOnly(True)
        self.allergy_display.setStyleSheet('background-color: #fff1f0; color: #ff4d4f;')
        self.allergy_display.setMinimumHeight(28)
        
        phone_label = QLabel('电话:')
        allergy_label = QLabel('过敏史:')
        allergy_label.setStyleSheet('font-weight: bold; color: #ff4d4f;')
        
        right_form.addRow(phone_label, self.patient_phone)
        right_form.addRow(allergy_label, self.allergy_display)
        
        info_layout.addLayout(left_form, 1)
        info_layout.addLayout(right_form, 1)
        
        patient_layout.addWidget(info_container)
        
        diagnosis_layout = QVBoxLayout()
        diagnosis_layout.setSpacing(4)
        diagnosis_label = QLabel('诊断:')
        diagnosis_label.setStyleSheet('font-weight: bold;')
        self.diagnosis = QTextEdit()
        self.diagnosis.setPlaceholderText('请输入诊断信息...')
        self.diagnosis.setMaximumHeight(60)
        self.diagnosis.setStyleSheet('''
            QTextEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #1890ff;
            }
        ''')
        diagnosis_layout.addWidget(diagnosis_label)
        diagnosis_layout.addWidget(self.diagnosis)
        
        patient_layout.addLayout(diagnosis_layout)
        
        self.allergy_label = QLabel()
        self.allergy_label.setStyleSheet('''
            color: #ff4d4f; 
            font-weight: bold;
            background-color: #fff1f0;
            padding: 6px;
            border-radius: 4px;
            border: 1px solid #ffa39e;
        ''')
        self.allergy_label.setWordWrap(True)
        self.allergy_label.hide()
        
        patient_layout.addWidget(self.allergy_label)
        
        left_panel.addWidget(patient_group)

        self.med_search = QLineEdit()
        self.med_search.setPlaceholderText('输入药材名称搜索')
        self.med_search.textChanged.connect(self.search_medicine)
        self.med_list = QTableWidget()
        self.med_list.setColumnCount(3)
        self.med_list.setHorizontalHeaderLabels(['名称', '价格', '库存'])
        self.med_list.setColumnWidth(0, 150)
        self.med_list.setColumnWidth(1, 80)
        self.med_list.setColumnWidth(2, 80)
        self.med_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.med_list.verticalHeader().setVisible(False)
        self.med_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.med_list.verticalHeader().setDefaultSectionSize(35)

        add_btn = QPushButton('添加到处方')
        add_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 10px 20px;')
        add_btn.clicked.connect(self.add_to_prescription)

        left_panel.addWidget(QLabel('药材库:'))
        left_panel.addWidget(self.med_search)
        left_panel.addWidget(self.med_list)
        left_panel.addWidget(add_btn)

        right_panel = QVBoxLayout()
        
        prescription_header_layout = QHBoxLayout()
        prescription_header = QLabel('当前处方:')
        prescription_header.setStyleSheet('font-weight: bold; font-size: 14px; color: #000000;')
        
        template_btn = QPushButton('📋 使用模板')
        template_btn.setStyleSheet('''
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        ''')
        template_btn.clicked.connect(self._show_template_selector)
        
        prescription_header_layout.addWidget(prescription_header)
        prescription_header_layout.addStretch()
        prescription_header_layout.addWidget(template_btn)
        
        right_panel.addLayout(prescription_header_layout)
        
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(5)
        self.prescription_table.setHorizontalHeaderLabels(['药材', '数量', '单价', '小计', '操作'])
        self.prescription_table.verticalHeader().setVisible(False)
        self.prescription_table.verticalHeader().setDefaultSectionSize(40)
        self.prescription_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.prescription_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.prescription_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.prescription_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.prescription_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.prescription_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.prescription_table.setColumnWidth(1, 80)
        self.prescription_table.setColumnWidth(2, 80)
        self.prescription_table.setColumnWidth(3, 80)
        self.prescription_table.setColumnWidth(4, 70)

        self.total_label = QLabel('总计: ¥ 0.00')
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")

        save_btn = QPushButton('保存处方')
        save_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 10px 20px;')
        save_btn.clicked.connect(self.save_prescription)
        print_btn = QPushButton('打印处方')
        print_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 1px solid #000000; padding: 10px 20px;')
        print_btn.clicked.connect(self.print_prescription)
        clear_btn = QPushButton('清空')
        clear_btn.setStyleSheet('background-color: #ffffff; color: #666666; border: 1px solid #e0e0e0; padding: 10px 20px;')
        clear_btn.clicked.connect(self.clear_form)

        btn_row = QHBoxLayout()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(print_btn)
        btn_row.addWidget(clear_btn)

        right_panel.addWidget(self.prescription_table)
        right_panel.addWidget(self.total_label)
        right_panel.addLayout(btn_row)

        main_layout.addLayout(left_panel, 40)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        main_layout.addWidget(right_widget, 60)

    def _on_patient_selected(self, patient):
        logger.info(f"患者选择信号收到: {patient}")
        if not patient:
            self._clear_patient_form()
            return
            
        self._current_patient_id = patient.get('id')
        self.patient_name.setText(str(patient.get('name', '')))
        self.patient_age.setValue(int(patient.get('age', 0) or 0))
        
        gender = str(patient.get('gender', '男'))
        index = self.patient_gender.findText(gender)
        if index >= 0:
            self.patient_gender.setCurrentIndex(index)
        self.patient_phone.setText(str(patient.get('phone', '') or ''))
        
        allergy = str(patient.get('allergy', '') or '')
        self._current_patient_allergy = allergy
        
        if allergy:
            self.allergy_display.setText(allergy)
            self.allergy_display.show()
            self.allergy_label.setText(f'⚠️ 过敏警告: {allergy}')
            self.allergy_label.show()
        else:
            self.allergy_display.clear()
            self.allergy_label.hide()
            
        logger.info(f"患者信息已填充: {patient.get('name')}, ID: {self._current_patient_id}")

    def _clear_patient_form(self):
        self._current_patient_id = None
        self._current_patient_allergy = ''
        self.patient_selector.clear_selection()
        self.patient_name.clear()
        self.patient_age.setValue(0)
        self.patient_gender.setCurrentIndex(0)
        self.patient_phone.clear()
        self.allergy_display.clear()
        self.allergy_label.hide()
        logger.info("清空患者表单，准备新建患者")
        
    def _show_template_selector(self):
        dialog = TemplateSelectorDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_template:
            self._apply_template(dialog.selected_template)
            
    def _apply_template(self, template):
        logger.info(f"应用处方模板: {template.get('name')}")
        
        if template.get('diagnosis'):
            self.diagnosis.setText(template.get('diagnosis'))
            
        medicines_text = template.get('medicines', '')
        if not medicines_text:
            QMessageBox.warning(self, '模板为空', '该模板没有药材信息')
            return
            
        try:
            added_count = 0
            skipped_count = 0
            
            for line in medicines_text.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 2:
                    med_name = parts[0]
                    try:
                        quantity = float(parts[1])
                    except ValueError:
                        quantity = 10
                else:
                    med_name = line
                    quantity = 10
                
                med_info = self.db.fetchone(
                    "SELECT m.id, i.price, i.quantity FROM medicines m JOIN inventory i ON m.id = i.medicine_id WHERE m.name = ?",
                    (med_name,)
                )
                
                if med_info:
                    if isinstance(med_info, dict):
                        med_id = med_info.get('id')
                        price = float(med_info.get('price', 0) or 0)
                        stock = float(med_info.get('quantity', 0) or 0)
                    else:
                        med_id, price, stock = med_info
                        price = float(price or 0)
                        stock = float(stock or 0)
                    
                    if stock >= quantity:
                        existing = next((item for item in self.cart if item['id'] == med_id), None)
                        if existing:
                            existing['qty'] += quantity
                            existing['amount'] = existing['qty'] * existing['price']
                        else:
                            self.cart.append({
                                'id': med_id,
                                'name': med_name,
                                'qty': quantity,
                                'price': price,
                                'amount': quantity * price
                            })
                        added_count += 1
                    else:
                        skipped_count += 1
                        logger.warning(f'药材 "{med_name}" 库存不足: 需要{quantity}, 库存{stock}')
                else:
                    skipped_count += 1
                    logger.warning(f'未找到药材: {med_name}')
                        
            self.refresh_prescription_table()
            
            msg = f'已应用模板: {template.get("name")}\n成功添加 {added_count} 味药材'
            if skipped_count > 0:
                msg += f'\n跳过 {skipped_count} 味（库存不足或未找到）'
            QMessageBox.information(self, '模板应用完成', msg)
            
        except Exception as e:
            logger.error(f"应用模板失败: {e}")
            QMessageBox.warning(self, '应用失败', f'模板应用失败: {str(e)}')

    def search_medicine(self, text):
        try:
            rows = self.db.fetchall(
                "SELECT m.name, i.price, i.quantity FROM medicines m JOIN inventory i ON m.id = i.medicine_id WHERE m.name LIKE ?",
                (f'%{text}%',))
            self.med_list.setRowCount(len(rows))
            for i, row in enumerate(rows):
                name = row.get('name', '') if isinstance(row, dict) else row[0]
                price = row.get('price', 0) if isinstance(row, dict) else row[1]
                qty = row.get('quantity', 0) if isinstance(row, dict) else row[2]
                
                name_item = QTableWidgetItem(str(name))
                name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.med_list.setItem(i, 0, name_item)
                
                price_item = QTableWidgetItem(f'¥{price}')
                price_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.med_list.setItem(i, 1, price_item)
                
                qty_item = QTableWidgetItem(f'{qty}g')
                qty_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.med_list.setItem(i, 2, qty_item)
        except Exception as e:
            logger.error(f"搜索药材失败: {e}")
            self.med_list.setRowCount(0)

    def add_to_prescription(self):
        try:
            selected = self.med_list.selectedItems()
            if not selected:
                QMessageBox.warning(self, '提示', '请先选择要添加的药材')
                return

            name = selected[0].text()
            med_info = self.db.fetchone(
                "SELECT m.id, i.price, i.quantity, m.contraindication FROM medicines m JOIN inventory i ON m.id = i.medicine_id WHERE m.name = ?",
                (name,))
            
            if not med_info:
                QMessageBox.warning(self, '提示', '未找到该药材信息')
                return

            if isinstance(med_info, dict):
                med_id = med_info.get('id')
                price = med_info.get('price', 0) or 0
                stock = med_info.get('quantity', 0) or 0
                contraindication = med_info.get('contraindication', '') or ''
            else:
                med_id, price, stock, contraindication = med_info
                price = price or 0
                stock = stock or 0
                contraindication = contraindication or ''

            if self._current_patient_allergy:
                if name in self._current_patient_allergy or any(a in name for a in self._current_patient_allergy.split()):
                    reply = QMessageBox.warning(self, '过敏提醒',
                        f'⚠️ 患者对 "{name}" 或相关成分可能过敏！\n过敏史: {self._current_patient_allergy}\n\n是否继续添加？',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return

            for item in self.cart:
                if contraindication and item['name'] in str(contraindication):
                    QMessageBox.warning(self, '配伍禁忌提醒',
                                        f'警告："{name}" 与 "{item["name"]}" 可能存在配伍禁忌！\n禁忌说明：{contraindication}')

            if stock <= 0:
                QMessageBox.warning(self, '库存不足', f'药材 "{name}" 库存不足，无法添加')
                return

            qty, ok = QInputDialog.getDouble(self, '输入数量', f'请输入{name}的克数:', 10, 0.1, stock, 1)
            if ok:
                if qty > stock:
                    QMessageBox.warning(self, '库存不足', f'药材 "{name}" 库存不足，当前库存: {stock}g')
                    return

                existing_item = next((item for item in self.cart if item['id'] == med_id), None)
                if existing_item:
                    new_qty = existing_item['qty'] + qty
                    if new_qty > stock:
                        QMessageBox.warning(self, '库存不足', f'药材 "{name}" 总数量超过库存，当前库存: {stock}g')
                        return
                    existing_item['qty'] = new_qty
                    existing_item['amount'] = new_qty * existing_item['price']
                else:
                    amount = qty * price
                    self.cart.append({
                        'id': med_id,
                        'name': name,
                        'qty': qty,
                        'price': price,
                        'amount': amount
                    })
                self.refresh_prescription_table()
                logger.info(f"添加药材到处方: {name}, 数量: {qty}g")
        except Exception as e:
            logger.error(f"添加药材到处方失败: {e}")
            QMessageBox.critical(self, '错误', f'添加失败：{str(e)}')

    def remove_from_prescription(self, row):
        try:
            if 0 <= row < len(self.cart):
                removed = self.cart.pop(row)
                logger.info(f"从处方移除药材: {removed['name']}")
                self.refresh_prescription_table()
        except Exception as e:
            logger.error(f"移除药材失败: {e}")

    def refresh_prescription_table(self):
        try:
            self.prescription_table.setRowCount(len(self.cart))
            total_amount = 0
            for i, item in enumerate(self.cart):
                name_item = QTableWidgetItem(item['name'])
                name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.prescription_table.setItem(i, 0, name_item)
                
                qty_item = QTableWidgetItem(f"{item['qty']}g")
                qty_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.prescription_table.setItem(i, 1, qty_item)
                
                price_item = QTableWidgetItem(f"¥{item['price']}")
                price_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.prescription_table.setItem(i, 2, price_item)
                
                amount_item = QTableWidgetItem(f"¥{item['amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.prescription_table.setItem(i, 3, amount_item)
                
                remove_btn = QPushButton('删除')
                remove_btn.setCursor(Qt.PointingHandCursor)
                remove_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #ffffff;
                        color: #ff4d4f;
                        border: 1px solid #ff4d4f;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #fff1f0;
                    }
                    QPushButton:pressed {
                        background-color: #ff4d4f;
                        color: #ffffff;
                    }
                ''')
                remove_btn.clicked.connect(lambda checked, row=i: self.remove_from_prescription(row))
                self.prescription_table.setCellWidget(i, 4, remove_btn)
                
                total_amount += item['amount']

            self.total_label.setText(f'总计: ¥ {total_amount:.2f}')
        except Exception as e:
            logger.error(f"刷新处方表格失败: {e}")

    def save_prescription(self):
        if not self.patient_name.text().strip():
            QMessageBox.warning(self, '提示', '请填写患者姓名')
            return
        
        if not self.cart:
            QMessageBox.warning(self, '提示', '请添加药材到处方')
            return

        try:
            patient_name = self.patient_name.text().strip()
            patient_age = self.patient_age.value()
            patient_gender = self.patient_gender.currentText()
            patient_phone = self.patient_phone.text().strip()
            diagnosis = self.diagnosis.toPlainText().strip()
            total_amount = sum(item['amount'] for item in self.cart)

            if not self._current_patient_id:
                existing = self.db.fetchone(
                    "SELECT id FROM patients WHERE name = ? AND age = ? AND gender = ?",
                    (patient_name, patient_age, patient_gender)
                )
                if existing:
                    self._current_patient_id = existing.get('id') if isinstance(existing, dict) else existing[0]
                else:
                    cursor = self.db.execute('''
                        INSERT INTO patients (name, gender, age, phone)
                        VALUES (?, ?, ?, ?)
                    ''', (patient_name, patient_gender, patient_age, patient_phone))
                    self._current_patient_id = cursor.lastrowid
                    logger.info(f"创建新患者: {patient_name}, ID: {self._current_patient_id}")

            cursor = self.db.execute('''
                INSERT INTO prescriptions (patient_id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self._current_patient_id, patient_name, patient_age, patient_gender, diagnosis, total_amount, '医生'))

            pres_id = cursor.lastrowid
            if not pres_id:
                raise Exception("获取处方ID失败")

            for item in self.cart:
                self.db.execute('''
                    INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount)
                    VALUES (?, ?, ?, ?, 'g', ?, ?)
                ''', (pres_id, item['id'], item['name'], item['qty'], item['price'], item['amount']))

                self.db.execute("UPDATE inventory SET quantity = quantity - ? WHERE medicine_id = ?",
                                (item['qty'], item['id']))

                self.db.execute('''
                    INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, total_amount, notes)
                    VALUES (?, ?, '出库', ?, ?, ?)
                ''', (item['id'], item['name'], item['qty'], item['amount'], f'处方销售-{pres_id}'))

            logger.info(f"处方保存成功, 处方ID: {pres_id}, 患者: {patient_name}, 总金额: {total_amount}")
            QMessageBox.information(self, '成功', f'处方保存成功，库存已更新。\n处方编号：{pres_id}')
            self.clear_form()
            
        except Exception as e:
            logger.error(f"保存处方失败: {e}")
            QMessageBox.critical(self, '错误', f'保存失败：{str(e)}')

    def print_prescription(self):
        if not self.cart:
            QMessageBox.warning(self, '提示', '当前处方为空，无法打印')
            return

        try:
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                doc = QTextDocument()
                total = sum(item['amount'] for item in self.cart)
                content = f"""
                <h2 align='center'>中药材处方单</h2>
                <hr>
                <p>患者姓名：{self.patient_name.text()} &nbsp;&nbsp;&nbsp; 年龄：{self.patient_age.value()} &nbsp;&nbsp;&nbsp; 性别：{self.patient_gender.currentText()}</p>
                <p>诊断：{self.diagnosis.toPlainText()}</p>
                <hr>
                <table width='100%' border='1' cellspacing='0' cellpadding='2'>
                <tr><th>药材</th><th>数量</th><th>单价</th><th>金额</th></tr>
                """
                for item in self.cart:
                    content += f"<tr><td>{item['name']}</td><td>{item['qty']}g</td><td>¥{item['price']}</td><td>¥{item['amount']:.2f}</td></tr>"
                content += f"""
                </table>
                <hr>
                <p align='right'><b>总计：¥{total:.2f}</b></p>
                <p align='right'>日期：{datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                """
                doc.setHtml(content)
                doc.print_(printer)
                logger.info(f"打印处方成功")
        except Exception as e:
            logger.error(f"打印处方失败: {e}")
            QMessageBox.critical(self, '错误', f'打印失败：{str(e)}')

    def clear_form(self):
        self._clear_patient_form()
        self.diagnosis.clear()
        self.cart = []
        self.refresh_prescription_table()
