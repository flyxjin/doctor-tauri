from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem,
                             QPushButton, QMessageBox, QTextEdit, QLabel, QComboBox,
                             QInputDialog, QHeaderView)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import logging
import re
import html as html_mod

logger = logging.getLogger('MedicineSystem')


class PrescriptionView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cart = []
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

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

        self.med_search = QLineEdit()
        self.med_search.setPlaceholderText('输入药材名称')
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)
        self._search_timer.timeout.connect(self._do_search)
        self.med_search.textChanged.connect(self._search_timer.start)
        self.med_list = QTableWidget()
        self.med_list.setColumnCount(3)
        self.med_list.setHorizontalHeaderLabels(['名称', '价格', '库存'])
        self.med_list.setColumnWidth(0, 150)
        self.med_list.setColumnWidth(1, 80)
        self.med_list.setColumnWidth(2, 80)
        self.med_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.med_list.verticalHeader().setVisible(False)
        self.med_list.setEditTriggers(QTableWidget.NoEditTriggers)

        add_btn = QPushButton('添加到处方')
        add_btn.setStyleSheet('background-color: #67c23a; color: white;')
        add_btn.clicked.connect(self.add_to_prescription)

        left_panel.addLayout(form_layout)
        left_panel.addWidget(QLabel('药材库:'))
        left_panel.addWidget(self.med_search)
        left_panel.addWidget(self.med_list)
        left_panel.addWidget(add_btn)

        right_panel = QVBoxLayout()
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(5)
        self.prescription_table.setHorizontalHeaderLabels(['药材', '数量', '单价', '小计', '操作'])
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prescription_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.total_label = QLabel('总计: ¥ 0.00')
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")

        save_btn = QPushButton('保存处方')
        save_btn.setStyleSheet('background-color: #67c23a; color: white; padding: 10px 20px;')
        save_btn.clicked.connect(self.save_prescription)
        print_btn = QPushButton('打印处方')
        print_btn.setStyleSheet('background-color: #409eff; color: white; padding: 10px 20px;')
        print_btn.clicked.connect(self.print_prescription)
        clear_btn = QPushButton('清空')
        clear_btn.setStyleSheet('background-color: #909399; color: white; padding: 10px 20px;')
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

    def _do_search(self):
        text = self.med_search.text()
        self.search_medicine(text)

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
                self.med_list.setItem(i, 0, QTableWidgetItem(str(name)))
                self.med_list.setItem(i, 1, QTableWidgetItem(f'¥{price}'))
                self.med_list.setItem(i, 2, QTableWidgetItem(f'{qty}g'))
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

            if contraindication:
                contraindication_set = set(re.split(r'[、,，\s；;]+', str(contraindication).strip()))
                contraindication_set.discard('')
                for item in self.cart:
                    if item['name'] in contraindication_set:
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
                self.prescription_table.setItem(i, 0, QTableWidgetItem(item['name']))
                self.prescription_table.setItem(i, 1, QTableWidgetItem(f"{item['qty']}g"))
                self.prescription_table.setItem(i, 2, QTableWidgetItem(f"¥{item['price']}"))
                self.prescription_table.setItem(i, 3, QTableWidgetItem(f"¥{item['amount']:.2f}"))
                
                remove_btn = QPushButton('删除')
                remove_btn.setStyleSheet('background-color: #f56c6c; color: white;')
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
            diagnosis = self.diagnosis.text().strip()
            total_amount = sum(item['amount'] for item in self.cart)

            self.db.begin_transaction()

            cursor = self.db.execute('''
                INSERT INTO prescriptions (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_name, patient_age, patient_gender, diagnosis, total_amount, '医生'))

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

            self.db.commit()

            logger.info(f"处方保存成功, 处方ID: {pres_id}, 患者: {patient_name}, 总金额: {total_amount}")
            QMessageBox.information(self, '成功', f'处方保存成功，库存已更新。\n处方编号：{pres_id}')
            self.clear_form()

        except Exception as e:
            self.db.rollback()
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
                <p>患者姓名：{html_mod.escape(self.patient_name.text())} &nbsp;&nbsp;&nbsp; 年龄：{self.patient_age.value()} &nbsp;&nbsp;&nbsp; 性别：{self.patient_gender.currentText()}</p>
                <p>诊断：{html_mod.escape(self.diagnosis.text())}</p>
                <hr>
                <table width='100%' border='1' cellspacing='0' cellpadding='2'>
                <tr><th>药材</th><th>数量</th><th>单价</th><th>金额</th></tr>
                """
                for item in self.cart:
                    content += f"<tr><td>{html_mod.escape(item['name'])}</td><td>{item['qty']}g</td><td>¥{item['price']}</td><td>¥{item['amount']:.2f}</td></tr>"
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
        self.patient_name.clear()
        self.patient_age.setValue(0)
        self.patient_gender.setCurrentIndex(0)
        self.diagnosis.clear()
        self.cart = []
        self.refresh_prescription_table()
