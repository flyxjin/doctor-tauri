from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QMessageBox, QLabel)
from PyQt5.QtCore import Qt


class HistoryView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.list_table = QTableWidget()
        self.list_table.setColumnCount(6)
        self.list_table.setHorizontalHeaderLabels(['处方ID', '患者姓名', '年龄', '诊断', '总金额', '开具时间'])
        self.list_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.list_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels(['药材名称', '数量', '单价', '金额'])

        self.refresh_btn = QPushButton('刷新处方列表')
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.list_table.itemSelectionChanged.connect(self.show_detail)

        layout.addWidget(QLabel('历史处方列表:'))
        layout.addWidget(self.list_table)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(QLabel('处方详情:'))
        layout.addWidget(self.detail_table)

    def refresh_data(self):
        rows = self.db.fetchall(
            "SELECT id, patient_name, patient_age, diagnosis, total_amount, created_at FROM prescriptions ORDER BY created_at DESC")
        self.list_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, data in enumerate(row):
                self.list_table.setItem(i, j, QTableWidgetItem(str(data) if data else ''))

    def show_detail(self):
        selected = self.list_table.selectedItems()
        if not selected:
            return

        pres_id = selected[0].text()
        rows = self.db.fetchall(
            "SELECT medicine_name, quantity, price, amount FROM prescription_items WHERE prescription_id = ?",
            (pres_id,))

        self.detail_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, data in enumerate(row):
                self.detail_table.setItem(i, j, QTableWidgetItem(str(data)))
