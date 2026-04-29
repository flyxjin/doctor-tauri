from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QMessageBox, QLabel,
                             QHeaderView, QDialog, QTextEdit, QGroupBox, QLineEdit,
                             QDateEdit)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime
import logging

logger = logging.getLogger('MedicineSystem')


class OperationLogDialog(QDialog):
    def __init__(self, parent=None, log_data=None):
        super().__init__(parent)
        self.setWindowTitle('操作日志')
        self.setMinimumSize(500, 400)
        self.log_data = log_data or []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(['操作类型', '目标类型', '目标ID', '操作者', '操作时间'])
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.load_logs()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(QLabel('操作日志记录:'))
        layout.addWidget(self.log_table)
        layout.addWidget(close_btn)
    
    def load_logs(self):
        self.log_table.setRowCount(len(self.log_data))
        for i, row in enumerate(self.log_data):
            if isinstance(row, dict):
                data_list = [
                    row.get('operation_type', ''),
                    row.get('target_type', ''),
                    row.get('target_id', ''),
                    row.get('operator', ''),
                    row.get('created_at', '')
                ]
            else:
                data_list = list(row)
            
            for j, data in enumerate(data_list):
                self.log_table.setItem(i, j, QTableWidgetItem(str(data) if data else ''))


class HistoryView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._ensure_operation_logs_table()
        self.init_ui()

    def _ensure_operation_logs_table(self):
        try:
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id INTEGER NOT NULL,
                    operator TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        except Exception as e:
            logger.error(f"创建操作日志表失败: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        header_label = QLabel('历史处方列表')
        header_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #262626;')
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        self.record_count_label = QLabel('共 0 条记录')
        self.record_count_label.setStyleSheet('color: #8c8c8c;')
        header_layout.addWidget(self.record_count_label)
        
        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.name_search = QLineEdit()
        self.name_search.setPlaceholderText('患者姓名')
        self.name_search.setFixedWidth(150)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat('yyyy-MM-dd')
        self.date_from.setFixedWidth(120)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat('yyyy-MM-dd')
        self.date_to.setFixedWidth(120)

        search_btn = QPushButton('搜索')
        search_btn.setStyleSheet('background-color: #1890ff; color: white; padding: 6px 16px; border-radius: 4px;')
        search_btn.clicked.connect(self.refresh_data)

        reset_btn = QPushButton('重置')
        reset_btn.setStyleSheet('background-color: #909399; color: white; padding: 6px 16px; border-radius: 4px;')
        reset_btn.clicked.connect(self._reset_filters)

        search_layout.addWidget(QLabel('患者:'))
        search_layout.addWidget(self.name_search)
        search_layout.addWidget(QLabel('从:'))
        search_layout.addWidget(self.date_from)
        search_layout.addWidget(QLabel('至:'))
        search_layout.addWidget(self.date_to)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(reset_btn)
        search_layout.addStretch()

        layout.addLayout(search_layout)

        self.list_table = QTableWidget()
        self.list_table.setColumnCount(7)
        self.list_table.setHorizontalHeaderLabels(['处方ID', '患者姓名', '年龄', '诊断', '总金额', '开具时间', '操作'])
        self.list_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.list_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.list_table.setAlternatingRowColors(True)
        self.list_table.verticalHeader().setVisible(False)
        self.list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.list_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.list_table.setColumnWidth(6, 100)
        
        layout.addWidget(self.list_table)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.refresh_btn = QPushButton('刷新列表')
        self.refresh_btn.setObjectName('refresh_btn')
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        self.view_log_btn = QPushButton('查看操作日志')
        self.view_log_btn.setObjectName('view_log_btn')
        self.view_log_btn.clicked.connect(self.show_operation_logs)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.view_log_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        detail_group = QGroupBox('处方详情')
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels(['药材名称', '数量', '单价', '金额'])
        self.detail_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        detail_layout.addWidget(self.detail_table)
        
        layout.addWidget(detail_group)
        
        self._apply_styles()
        
        self.list_table.itemSelectionChanged.connect(self.show_detail)

    def _apply_styles(self):
        self.setStyleSheet('''
            QPushButton#refresh_btn {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton#refresh_btn:hover {
                background-color: #40a9ff;
            }
            QPushButton#view_log_btn {
                background-color: #ffffff;
                color: #595959;
                border: 1px solid #d9d9d9;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton#view_log_btn:hover {
                border-color: #1890ff;
                color: #1890ff;
            }
            QGroupBox {
                font-weight: 500;
                color: #262626;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        ''')

    def _get_row_value(self, row, key, index=None):
        if isinstance(row, dict):
            return row.get(key, '')
        elif index is not None and index < len(row):
            return row[index]
        return ''

    def _reset_filters(self):
        self.name_search.clear()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.refresh_data()

    def refresh_data(self):
        try:
            query = "SELECT id, patient_name, patient_age, diagnosis, total_amount, created_at FROM prescriptions WHERE 1=1"
            params = []

            name = self.name_search.text().strip()
            if name:
                query += " AND patient_name LIKE ?"
                params.append(f'%{name}%')

            date_from = self.date_from.date().toString('yyyy-MM-dd')
            date_to = self.date_to.date().toString('yyyy-MM-dd')
            query += " AND DATE(created_at) >= ? AND DATE(created_at) <= ?"
            params.extend([date_from, date_to])

            query += " ORDER BY created_at DESC"

            rows = self.db.fetchall(query, tuple(params))
            
            self.list_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                pres_id = self._get_row_value(row, 'id', 0)
                patient_name = self._get_row_value(row, 'patient_name', 1)
                patient_age = self._get_row_value(row, 'patient_age', 2)
                diagnosis = self._get_row_value(row, 'diagnosis', 3)
                total_amount = self._get_row_value(row, 'total_amount', 4)
                created_at = self._get_row_value(row, 'created_at', 5)
                
                data_list = [pres_id, patient_name, patient_age, diagnosis, total_amount, created_at]
                
                for j, data in enumerate(data_list):
                    item = QTableWidgetItem(str(data) if data else '')
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.list_table.setItem(i, j, item)
                
                delete_btn = QPushButton('删除')
                delete_btn.setProperty('prescription_id', pres_id)
                delete_btn.setProperty('row_index', i)
                delete_btn.clicked.connect(self._on_delete_clicked)
                delete_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #ff4d4f;
                        color: white;
                        border: none;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #ff7875;
                    }
                ''')
                
                self.list_table.setCellWidget(i, 6, delete_btn)
            
            self.record_count_label.setText(f'共 {len(rows)} 条记录')
        except Exception as e:
            logger.error(f"刷新历史记录失败: {e}")
            QMessageBox.critical(self, '错误', f'刷新数据失败：{str(e)}')

    def _on_delete_clicked(self):
        btn = self.sender()
        prescription_id = btn.property('prescription_id')
        row_index = btn.property('row_index')
        
        patient_name_item = self.list_table.item(row_index, 1)
        patient_name = patient_name_item.text() if patient_name_item else '未知'
        
        reply = QMessageBox.question(
            self, '确认删除',
            f'<p style="font-size: 14px;">确定要删除此处方记录吗？</p>'
            f'<p style="color: #ff4d4f; font-weight: bold;">此操作不可撤销！</p>'
            f'<p>处方ID: {prescription_id}</p>'
            f'<p>患者姓名: {patient_name}</p>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._delete_prescription(prescription_id, patient_name)

    def _delete_prescription(self, prescription_id, patient_name):
        try:
            self.db.begin_transaction()
            
            items = self.db.fetchall(
                "SELECT medicine_name, quantity FROM prescription_items WHERE prescription_id = ?",
                (prescription_id,)
            )
            
            self.db.execute(
                "DELETE FROM prescription_items WHERE prescription_id = ?",
                (prescription_id,)
            )
            
            self.db.execute(
                "DELETE FROM prescriptions WHERE id = ?",
                (prescription_id,)
            )
            
            details = f"删除处方ID:{prescription_id}, 患者:{patient_name}, 包含{len(items)}味药材"
            self._log_operation('DELETE', 'prescription', prescription_id, details)
            
            self.db.commit()
            
            logger.info(f"删除处方成功: ID={prescription_id}, 患者={patient_name}")
            QMessageBox.information(self, '删除成功', '处方记录已成功删除')
            self.refresh_data()
            
            self.detail_table.setRowCount(0)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除处方失败: {e}")
            QMessageBox.critical(self, '删除失败', f'删除处方记录时发生错误：\n{str(e)}')

    def _log_operation(self, operation_type, target_type, target_id, details):
        try:
            self.db.execute('''
                INSERT INTO operation_logs (operation_type, target_type, target_id, operator, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (operation_type, target_type, target_id, '系统管理员', details))
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")

    def show_detail(self):
        try:
            selected = self.list_table.selectedItems()
            if not selected:
                return

            pres_id = selected[0].text()
            rows = self.db.fetchall(
                "SELECT medicine_name, quantity, price, amount FROM prescription_items WHERE prescription_id = ?",
                (pres_id,))

            self.detail_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                if isinstance(row, dict):
                    data_list = [
                        row.get('medicine_name', ''),
                        row.get('quantity', ''),
                        row.get('price', ''),
                        row.get('amount', '')
                    ]
                else:
                    data_list = list(row)
                
                for j, data in enumerate(data_list):
                    item = QTableWidgetItem(str(data) if data else '')
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.detail_table.setItem(i, j, item)
        except Exception as e:
            logger.error(f"显示处方详情失败: {e}")

    def show_operation_logs(self):
        try:
            logs = self.db.fetchall(
                "SELECT operation_type, target_type, target_id, operator, created_at FROM operation_logs WHERE target_type = 'prescription' ORDER BY created_at DESC LIMIT 100"
            )
            
            dialog = OperationLogDialog(self, logs)
            dialog.exec_()
        except Exception as e:
            logger.error(f"显示操作日志失败: {e}")
            QMessageBox.critical(self, '错误', f'获取操作日志失败：{str(e)}')
