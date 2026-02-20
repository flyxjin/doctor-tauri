from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem,
                             QPushButton, QMessageBox, QTextEdit, QLabel, QComboBox,
                             QInputDialog)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from datetime import datetime


class PrescriptionView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cart = []  # 存储当前处方的药材列表
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # 左侧：患者信息与药材选择
        left_panel = QVBoxLayout()
        form_layout = QFormLayout()
        self.patient_name = QLineEdit()
        self.patient_age = QSpinBox()
        self.patient_age.setRange(0, 150)
        self.patient_gender = QComboBox()
        self.patient_gender.addItems(['男', '女'])
        self.diagnosis = QLineEdit()

        form_layout.addRow('姓名:', self.patient_name)
        form_layout.addRow('年龄:', self.patient_age)
        form_layout.addRow('性别:', self.patient_gender)
        form_layout.addRow('诊断:', self.diagnosis)

        # 药材选择区
        self.med_search = QLineEdit()
        self.med_search.setPlaceholderText('输入药材名称')
        self.med_search.textChanged.connect(self.search_medicine)
        self.med_list = QTableWidget()
        self.med_list.setColumnCount(2)
        self.med_list.setHorizontalHeaderLabels(['名称', '价格'])
        self.med_list.setColumnWidth(0, 150)
        self.med_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.med_list.verticalHeader().setVisible(False)

        add_btn = QPushButton('添加到处方')
        add_btn.clicked.connect(self.add_to_prescription)

        left_panel.addLayout(form_layout)
        left_panel.addWidget(QLabel('药材库:'))
        left_panel.addWidget(self.med_search)
        left_panel.addWidget(self.med_list)
        left_panel.addWidget(add_btn)

        # 右侧：当前处方列表
        right_panel = QVBoxLayout()
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(4)
        self.prescription_table.setHorizontalHeaderLabels(['药材', '数量', '单价', '小计'])

        self.total_label = QLabel('总计: ¥ 0.00')
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")

        save_btn = QPushButton('保存处方并扣减库存')
        save_btn.clicked.connect(self.save_prescription)
        print_btn = QPushButton('打印处方')
        print_btn.clicked.connect(self.print_prescription)
        clear_btn = QPushButton('清空')
        clear_btn.clicked.connect(self.clear_form)

        btn_row = QHBoxLayout()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(print_btn)
        btn_row.addWidget(clear_btn)

        right_panel.addWidget(QLabel('当前处方:'))
        right_panel.addWidget(self.prescription_table)
        right_panel.addWidget(self.total_label)
        right_panel.addLayout(btn_row)

        main_layout.addLayout(left_panel, 40)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        main_layout.addWidget(right_widget, 60)

    def search_medicine(self, text):
        rows = self.db.fetchall(
            "SELECT name, price FROM medicines m JOIN inventory i ON m.id = i.medicine_id WHERE name LIKE ?",
            (f'%{text}%',))
        self.med_list.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.med_list.setItem(i, 0, QTableWidgetItem(row[0]))
            self.med_list.setItem(i, 1, QTableWidgetItem(str(row[1])))

    def add_to_prescription(self):
        selected = self.med_list.selectedItems()
        if not selected:
            return

        name = selected[0].text()
        # 查询禁忌和库存
        med_info = self.db.fetchone(
            "SELECT m.id, i.price, i.quantity, m.contraindication FROM medicines m JOIN inventory i ON m.id = i.medicine_id WHERE m.name = ?",
            (name,))
        if not med_info:
            return

        med_id, price, stock, contraindication = med_info

        # 智能提醒逻辑：简单模拟检查当前处方药材是否在禁忌中
        # 实际开发中此处需要更复杂的配伍逻辑（如十八反、十九畏）
        for item in self.cart:
            if contraindication and item['name'] in contraindication:
                QMessageBox.warning(self, '⚠️ 配伍禁忌提醒',
                                    f'警告："{name}" 与 "{item["name"]}" 可能存在配伍禁忌！\n禁忌说明：{contraindication}')

        # 输入数量
        qty, ok = QInputDialog.getDouble(self, '输入数量', f'请输入{name}的克数:', 10, 0, stock, 0)
        if ok:
            amount = qty * price
            self.cart.append({
                'id': med_id,
                'name': name,
                'qty': qty,
                'price': price,
                'amount': amount
            })
            self.refresh_prescription_table()

    def refresh_prescription_table(self):
        self.prescription_table.setRowCount(len(self.cart))
        total_amount = 0
        for i, item in enumerate(self.cart):
            self.prescription_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.prescription_table.setItem(i, 1, QTableWidgetItem(f"{item['qty']}g"))
            self.prescription_table.setItem(i, 2, QTableWidgetItem(f"¥{item['price']}"))
            self.prescription_table.setItem(i, 3, QTableWidgetItem(f"¥{item['amount']:.2f}"))
            total_amount += item['amount']

        self.total_label.setText(f'总计: ¥ {total_amount:.2f}')

    def save_prescription(self):
        if not self.patient_name.text() or not self.cart:
            QMessageBox.warning(self, '提示', '请填写患者信息并添加药材')
            return

        # 开启事务逻辑
        try:
            # 1. 插入处方主表
            cursor = self.db.execute('''
                INSERT INTO prescriptions (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.patient_name.text(), self.patient_age.value(), self.patient_gender.currentText(),
                  self.diagnosis.text(), sum(i['amount'] for i in self.cart), '医生'))

            pres_id = cursor.lastrowid

            # 2. 插入处方详情并扣减库存
            for item in self.cart:
                self.db.execute('''
                    INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount)
                    VALUES (?, ?, ?, ?, 'g', ?, ?)
                ''', (pres_id, item['id'], item['name'], item['qty'], item['price'], item['amount']))

                # 扣减库存
                self.db.execute("UPDATE inventory SET quantity = quantity - ? WHERE medicine_id = ?",
                                (item['qty'], item['id']))

                # 记录出库历史
                self.db.execute('''
                    INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, total_amount, notes)
                    VALUES (?, ?, '出库', ?, ?, ?)
                ''', (item['id'], item['name'], item['qty'], item['amount'], f'处方销售-{pres_id}'))

            QMessageBox.information(self, '成功', f'处方保存成功，库存已更新。\n处方编号：{pres_id}')
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败：{str(e)}')

    def print_prescription(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            content = f"""
            <h2 align='center'>中药材处方单</h2>
            <hr>
            <p>患者姓名：{self.patient_name.text()} &nbsp;&nbsp;&nbsp; 年龄：{self.patient_age.value()} &nbsp;&nbsp;&nbsp; 性别：{self.patient_gender.currentText()}</p>
            <p>诊断：{self.diagnosis.text()}</p>
            <hr>
            <table width='100%' border='1' cellspacing='0' cellpadding='2'>
            <tr><th>药材</th><th>数量</th><th>单价</th><th>金额</th></tr>
            """
            for item in self.cart:
                content += f"<tr><td>{item['name']}</td><td>{item['qty']}g</td><td>¥{item['price']}</td><td>¥{item['amount']:.2f}</td></tr>"
            content += f"""
            </table>
            <hr>
            <p align='right'><b>总计：¥{sum(i['amount'] for i in self.cart):.2f}</b></p>
            <p align='right'>日期：{datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            """
            doc.setHtml(content)
            doc.print_(printer)

    def clear_form(self):
        self.patient_name.clear()
        self.diagnosis.clear()
        self.cart = []
        self.refresh_prescription_table()
