import html as html_mod
import logging
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core import (
    MedicineService,
    PatientService,
    Prescription,
    PrescriptionItem,
    PrescriptionService,
)
from core.compatibility import check_against_existing, check_compatibility
from core.template_service import PrescriptionTemplateService
from core.theme import AppColors, get_button_style, get_dialog_style, get_secondary_button_style
from core.validators import PrescriptionValidator
from views.base_view import BaseDataView

logger = logging.getLogger('MedicineSystem')


class PrescriptionView(BaseDataView):
    def __init__(self, db, patient_service=None):
        super().__init__(db)
        self._prescription_service = PrescriptionService(db)
        self._medicine_service = MedicineService(db)
        self._template_service = PrescriptionTemplateService()
        # 患者档案服务：优先使用外部传入的实例；未提供时基于 db 内部实例化，
        # 保证患者联动功能在旧调用点（仅传 db）下仍可用。
        self._patient_service = patient_service if patient_service is not None else PatientService(db)
        # 当前通过「选择患者」对话框选中的患者档案（None 表示未选中已有患者，可能为新患者）
        self._current_selected_patient = None
        self.cart = []
        # 缓存删除按钮样式字符串，避免每行重复生成
        self._remove_btn_style = get_button_style(AppColors.DANGER, padding='4px 12px')
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.patient_name = QLineEdit()
        self.patient_name.setPlaceholderText('输入患者姓名自动匹配档案，或点击「选择患者」')
        # 患者姓名输入 debounce 定时器：300ms 延迟，避免每次按键都查询数据库
        self._patient_search_timer = QTimer()
        self._patient_search_timer.setSingleShot(True)
        self._patient_search_timer.setInterval(300)
        self._patient_search_timer.timeout.connect(self._do_patient_search)
        self.patient_name.textChanged.connect(self._on_patient_name_changed)

        self.patient_age = QSpinBox()
        self.patient_age.setRange(0, 150)
        self.patient_gender = QComboBox()
        self.patient_gender.addItems(['男', '女'])
        self.diagnosis = QLineEdit()

        # 姓名行：QLineEdit + 「选择患者」按钮
        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        name_row.addWidget(self.patient_name, 1)
        self.select_patient_btn = QPushButton('选择患者')
        self.select_patient_btn.setStyleSheet(
            get_secondary_button_style(padding='8px 16px')
        )
        self.select_patient_btn.clicked.connect(self._open_patient_select_dialog)
        name_row.addWidget(self.select_patient_btn)
        form_layout.addRow('姓名:', name_row)

        # 患者匹配提示标签（输入时显示「⚠ 该患者有过敏史：xxx」之类的提示）
        self._patient_hint_label = QLabel('')
        self._patient_hint_label.setStyleSheet(
            f"color: {AppColors.TEXT_MUTED}; font-size: 12px; padding: 2px 4px;"
        )
        self._patient_hint_label.setWordWrap(True)
        form_layout.addRow('', self._patient_hint_label)

        # 过敏史提醒条（QFrame + 黄色背景，选中已有患者后显示）
        self._allergy_reminder_frame = QFrame()
        self._allergy_reminder_frame.setStyleSheet(
            f"QFrame {{ background-color: {AppColors.WARNING_BG}; "
            f"border: 1px solid {AppColors.WARNING}; border-radius: 4px; }}"
        )
        allergy_layout = QHBoxLayout(self._allergy_reminder_frame)
        allergy_layout.setContentsMargins(10, 6, 10, 6)
        self._allergy_reminder_label = QLabel('')
        self._allergy_reminder_label.setStyleSheet(
            f"color: {AppColors.WARNING}; font-weight: 600; "
            f"border: none; background: transparent;"
        )
        self._allergy_reminder_label.setWordWrap(True)
        allergy_layout.addWidget(self._allergy_reminder_label)
        self._allergy_reminder_frame.setVisible(False)
        form_layout.addRow('', self._allergy_reminder_frame)

        # 既往病史提醒条（QFrame + 浅灰色背景，选中已有患者后显示）
        self._medical_history_reminder_frame = QFrame()
        self._medical_history_reminder_frame.setStyleSheet(
            f"QFrame {{ background-color: {AppColors.BG_SECONDARY}; "
            f"border: 1px solid {AppColors.BORDER}; border-radius: 4px; }}"
        )
        mh_layout = QHBoxLayout(self._medical_history_reminder_frame)
        mh_layout.setContentsMargins(10, 6, 10, 6)
        self._medical_history_reminder_label = QLabel('')
        self._medical_history_reminder_label.setStyleSheet(
            f"color: {AppColors.TEXT_SECONDARY}; "
            f"border: none; background: transparent;"
        )
        self._medical_history_reminder_label.setWordWrap(True)
        mh_layout.addWidget(self._medical_history_reminder_label)
        self._medical_history_reminder_frame.setVisible(False)
        form_layout.addRow('', self._medical_history_reminder_frame)

        form_layout.addRow('年龄:', self.patient_age)
        form_layout.addRow('性别:', self.patient_gender)
        form_layout.addRow('诊断:', self.diagnosis)

        # 方剂模板快捷选择行：下拉框 + 应用模板 + 选择方剂（对话框） + 清空处方
        template_row = QHBoxLayout()
        template_row.setSpacing(8)
        template_label = QLabel('方剂模板:')
        template_label.setStyleSheet(
            f"font-weight: 600; color: {AppColors.TEXT_HEADING};"
        )
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(220)
        self._populate_template_combo()

        apply_template_btn = QPushButton('应用模板')
        apply_template_btn.setStyleSheet(
            get_button_style(AppColors.PRIMARY, padding='8px 16px')
        )
        apply_template_btn.clicked.connect(self.apply_selected_template)

        select_template_btn = QPushButton('选择方剂...')
        select_template_btn.setStyleSheet(
            get_secondary_button_style(padding='8px 16px')
        )
        select_template_btn.clicked.connect(self.open_template_dialog)

        clear_prescription_btn = QPushButton('清空处方')
        clear_prescription_btn.setStyleSheet(
            get_secondary_button_style(padding='8px 16px')
        )
        clear_prescription_btn.clicked.connect(self.clear_prescription)

        template_row.addWidget(template_label)
        template_row.addWidget(self.template_combo, 1)
        template_row.addWidget(apply_template_btn)
        template_row.addWidget(select_template_btn)
        template_row.addWidget(clear_prescription_btn)

        self.med_search = QLineEdit()
        self.med_search.setPlaceholderText('输入药材名称搜索...')
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
        self.med_list.verticalHeader().setDefaultSectionSize(40)

        add_btn = QPushButton('+ 添加到处方')
        add_btn.setStyleSheet(get_button_style(AppColors.SUCCESS, padding='10px 20px'))
        add_btn.clicked.connect(self.add_to_prescription)

        left_panel.addLayout(form_layout)
        left_panel.addLayout(template_row)
        left_panel.addWidget(self.med_search)
        left_panel.addWidget(self.med_list)
        left_panel.addWidget(add_btn)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(16)

        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(5)
        self.prescription_table.setHorizontalHeaderLabels(['药材', '数量', '单价', '小计', '操作'])
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prescription_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.prescription_table.verticalHeader().setDefaultSectionSize(44)

        self.total_label = QLabel('总计: ¥ 0.00')
        self.total_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {AppColors.TEXT_HEADING};")

        save_btn = QPushButton('保存处方')
        save_btn.setStyleSheet(get_button_style(AppColors.SUCCESS, padding='12px 24px'))
        save_btn.clicked.connect(self.save_prescription)
        print_btn = QPushButton('打印处方')
        print_btn.setStyleSheet(get_secondary_button_style(padding='12px 24px'))
        print_btn.clicked.connect(self.print_prescription)
        clear_btn = QPushButton('清空')
        clear_btn.setStyleSheet(get_secondary_button_style(padding='12px 24px'))
        clear_btn.clicked.connect(self.clear_form)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(print_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        right_panel.addWidget(self.prescription_table)
        right_panel.addWidget(self.total_label)
        right_panel.addLayout(btn_row)

        main_layout.addLayout(left_panel, 40)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        main_layout.addWidget(right_widget, 60)

        self._apply_responsive_table()

    def _do_search(self):
        text = self.med_search.text()
        self.search_medicine(text)

    def search_medicine(self, text):
        try:
            # 通过 Service 层搜索药材，避免 N+1 查询，遵循分层架构
            keyword = text if text else None
            rows = self._medicine_service.search_with_stock(keyword=keyword, limit=200)

            self.med_list.setRowCount(len(rows))
            for i, row in enumerate(rows):
                name = row['name'] if isinstance(row, dict) else row[0]
                price = (row['price'] if isinstance(row, dict) else row[1]) or 0
                qty = (row['quantity'] if isinstance(row, dict) else row[2]) or 0
                self.med_list.setItem(i, 0, QTableWidgetItem(str(name)))
                self.med_list.setItem(i, 1, QTableWidgetItem(f'¥{price}'))
                self.med_list.setItem(i, 2, QTableWidgetItem(f'{qty}g'))
        except Exception as e:
            logger.error(f"搜索药材失败: {e}")
            self.med_list.setRowCount(0)

    # ====================================================================
    # 患者档案联动：姓名输入搜索 / 选择患者对话框 / 过敏史与既往病史提醒
    # ====================================================================
    def _on_patient_name_changed(self):
        """姓名输入框文本变化：启动 debounce 定时器，并清空旧提示。
        若用户手动修改姓名，视为可能切换了患者，清空已选患者状态与提醒条。
        """
        text = self.patient_name.text().strip()
        if not text:
            # 输入清空时立即清空提示，无需等待 debounce
            self._patient_hint_label.setText('')
            self._patient_search_timer.stop()
            self._current_selected_patient = None
            self._update_patient_reminders(None)
            return
        self._patient_search_timer.start()

    def _do_patient_search(self):
        """debounce 触发后执行的患者搜索：根据姓名匹配档案并显示提示。
        - 优先精确匹配（姓名完全相等）
        - 其次单条模糊匹配
        - 多条匹配时提示用户点击「选择患者」查看
        """
        if self._patient_service is None:
            return
        text = self.patient_name.text().strip()
        if not text:
            self._patient_hint_label.setText('')
            return
        try:
            patients = self._patient_service.search(keyword=text)
        except Exception as e:
            logger.error(f"搜索患者失败: {e}")
            self._patient_hint_label.setText('')
            return

        if not patients:
            self._patient_hint_label.setText('')
            return

        # 优先精确匹配
        exact = next((p for p in patients if (p.name or '') == text), None)
        if exact:
            self._show_patient_hint(exact)
            return

        if len(patients) == 1:
            self._show_patient_hint(patients[0])
        else:
            self._patient_hint_label.setText(
                f'找到 {len(patients)} 名匹配患者，可点击「选择患者」从列表选择'
            )
            self._patient_hint_label.setStyleSheet(
                f"color: {AppColors.TEXT_SECONDARY}; font-size: 12px; padding: 2px 4px;"
            )

    def _show_patient_hint(self, patient):
        """输入匹配时在姓名输入框下方显示提示信息（过敏史/既往病史/已匹配）"""
        name = patient.name or ''
        if patient.allergy:
            self._patient_hint_label.setText(f'⚠ 该患者有过敏史：{patient.allergy}')
            self._patient_hint_label.setStyleSheet(
                f"color: {AppColors.WARNING}; font-size: 12px; padding: 2px 4px;"
            )
        elif patient.medical_history:
            self._patient_hint_label.setText(f'既往病史：{patient.medical_history}')
            self._patient_hint_label.setStyleSheet(
                f"color: {AppColors.TEXT_SECONDARY}; font-size: 12px; padding: 2px 4px;"
            )
        else:
            self._patient_hint_label.setText(f'已匹配患者：{name}')
            self._patient_hint_label.setStyleSheet(
                f"color: {AppColors.TEXT_MUTED}; font-size: 12px; padding: 2px 4px;"
            )

    def _open_patient_select_dialog(self):
        """打开患者选择对话框，选择后自动填充姓名/性别/年龄并显示提醒条"""
        if self._patient_service is None:
            QMessageBox.information(self, '提示', '患者档案服务未启用')
            return
        dialog = PatientSelectDialog(self._patient_service, self)
        if dialog.exec() == QDialog.Accepted:
            patient = dialog.selected_patient
            if patient:
                self._apply_selected_patient(patient)

    def _apply_selected_patient(self, patient):
        """将对话框选中的患者信息填充到处方表单，并刷新提醒条"""
        self.patient_name.blockSignals(True)
        self.patient_name.setText(patient.name or '')
        self.patient_name.blockSignals(False)

        if patient.gender:
            idx = self.patient_gender.findText(patient.gender)
            if idx >= 0:
                self.patient_gender.setCurrentIndex(idx)
        if patient.age is not None:
            try:
                self.patient_age.setValue(int(patient.age))
            except (TypeError, ValueError):
                pass

        self._current_selected_patient = patient
        # 同步更新输入提示标签（与对话框选择保持一致）
        self._show_patient_hint(patient)
        self._update_patient_reminders(patient)
        logger.info(f"已选择患者档案: {patient.name} (id={patient.id})")

    def _update_patient_reminders(self, patient):
        """根据选中患者更新过敏史/既往病史提醒条的显隐与文字"""
        allergy = (patient.allergy or '').strip() if patient else ''
        medical_history = (patient.medical_history or '').strip() if patient else ''

        if allergy:
            self._allergy_reminder_label.setText(f'⚠ 过敏史提醒：{allergy}')
            self._allergy_reminder_frame.setVisible(True)
        else:
            self._allergy_reminder_label.setText('')
            self._allergy_reminder_frame.setVisible(False)

        if medical_history:
            self._medical_history_reminder_label.setText(f'既往病史：{medical_history}')
            self._medical_history_reminder_frame.setVisible(True)
        else:
            self._medical_history_reminder_label.setText('')
            self._medical_history_reminder_frame.setVisible(False)

    def add_to_prescription(self):
        try:
            selected = self.med_list.selectedItems()
            if not selected:
                QMessageBox.warning(self, '提示', '请先选择要添加的药材')
                return

            name = selected[0].text()
            # 通过 Service 层查询药材详情，遵循分层架构
            med_info = self._medicine_service.get_detail_for_prescription(name)

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

            # 十八反、十九畏配伍禁忌检查
            existing_names = [item['name'] for item in self.cart]
            compat_conflicts = check_against_existing(name, existing_names)
            if compat_conflicts:
                conflict_msgs = '\n'.join(c['description'] for c in compat_conflicts)
                QMessageBox.warning(self, '配伍禁忌预警',
                                    f'检测到配伍禁忌：\n{conflict_msgs}\n\n请确认是否继续添加。')

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
        if getattr(self, '_removing', False):
            return
        try:
            self._removing = True
            if 0 <= row < len(self.cart):
                removed = self.cart.pop(row)
                logger.info(f"从处方移除药材: {removed['name']}")
                self.refresh_prescription_table()
        except Exception as e:
            logger.error(f"移除药材失败: {e}")
        finally:
            self._removing = False

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
                remove_btn.setStyleSheet(self._remove_btn_style)
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

        # 保存前最终配伍禁忌检查
        all_names = [item['name'] for item in self.cart]
        final_conflicts = check_compatibility(all_names)
        if final_conflicts:
            conflict_msgs = '\n'.join(c['description'] for c in final_conflicts)
            reply = QMessageBox.warning(
                self, '配伍禁忌确认',
                f'处方中存在 {len(final_conflicts)} 处配伍禁忌：\n{conflict_msgs}\n\n是否仍要保存？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        try:
            patient_name = self.patient_name.text().strip()
            patient_age = self.patient_age.value()
            patient_gender = self.patient_gender.currentText()
            diagnosis = self.diagnosis.text().strip()
            total_amount = sum(item['amount'] for item in self.cart)

            # 调用 PrescriptionValidator 校验
            prescription_dict = {
                'patient_name': patient_name,
                'patient_age': patient_age,
                'patient_gender': patient_gender,
                'diagnosis': diagnosis,
                'items': [
                    {'medicine_id': item['id'], 'medicine_name': item['name'],
                     'quantity': item['qty'], 'price': item['price']}
                    for item in self.cart
                ]
            }
            is_valid, val_errors = PrescriptionValidator.validate(prescription_dict)
            if not is_valid:
                QMessageBox.warning(self, '验证失败', '\n'.join(val_errors))
                return

            prescription = Prescription(
                patient_name=patient_name,
                patient_age=patient_age,
                patient_gender=patient_gender,
                diagnosis=diagnosis,
                total_amount=total_amount,
                created_by='医生'
            )

            items = [
                PrescriptionItem(
                    prescription_id=0,
                    medicine_id=item['id'],
                    medicine_name=item['name'],
                    quantity=item['qty'],
                    unit='g',
                    price=item['price'],
                    amount=item['amount']
                )
                for item in self.cart
            ]

            pres_id = self._prescription_service.create(prescription, items)

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
            if dialog.exec() == QPrintDialog.Accepted:
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
                doc.print(printer)
                logger.info("打印处方成功")
        except Exception as e:
            logger.error(f"打印处方失败: {e}")
            QMessageBox.critical(self, '错误', f'打印失败：{str(e)}')

    def clear_form(self):
        self.patient_name.clear()
        self.patient_age.setValue(0)
        self.patient_gender.setCurrentIndex(0)
        self.diagnosis.clear()
        self.cart = []
        # 重置患者联动状态：已选患者、提示标签、提醒条
        self._current_selected_patient = None
        self._patient_hint_label.setText('')
        self._allergy_reminder_label.setText('')
        self._allergy_reminder_frame.setVisible(False)
        self._medical_history_reminder_label.setText('')
        self._medical_history_reminder_frame.setVisible(False)
        self.refresh_prescription_table()

    def clear_prescription(self):
        """仅清空处方药材列表，保留患者信息"""
        self.cart = []
        self.refresh_prescription_table()

    def _populate_template_combo(self):
        """填充方剂模板下拉框（按分类分组展示）"""
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem('— 选择方剂 —', None)
        templates = self._template_service.load_templates()
        # 按 category 分组，保证下拉框中方剂按类别聚集
        categories = self._template_service.get_categories()
        for cat in categories:
            cat_templates = [t for t in templates if t.get('category') == cat]
            if not cat_templates:
                continue
            for t in cat_templates:
                label = f"【{cat}】{t.get('name', '')}"
                self.template_combo.addItem(label, t)
        self.template_combo.blockSignals(False)

    def apply_selected_template(self):
        """应用下拉框中当前选中的方剂模板"""
        template = self.template_combo.currentData()
        if not template:
            QMessageBox.information(self, '提示', '请先在下拉框中选择方剂模板')
            return
        self._apply_template(template)

    def open_template_dialog(self):
        """打开方剂模板选择对话框（支持搜索 + 按分类浏览）"""
        dialog = TemplateSelectionDialog(self._template_service, self)
        if dialog.exec() == QDialog.Accepted:
            template = dialog.selected_template
            if template:
                self._apply_template(template)

    def _apply_template(self, template):
        """将方剂模板应用到当前处方：
        1. 设置诊断字段为方剂的 indication
        2. 遍历方剂 items，按名称在数据库查找药材（精确匹配 → 反向包含匹配）
        3. 找到的药材按方剂指定数量添加到 cart
        4. 未找到的药材在状态栏提示
        """
        if not template or not isinstance(template, dict):
            return

        items = template.get('items') or []
        if not items:
            QMessageBox.information(self, '提示', '该方剂模板没有药材')
            return

        template_name = template.get('name', '')

        # 设置诊断字段为方剂主治
        indication = template.get('indication', '')
        if indication:
            self.diagnosis.setText(indication)

        # 一次性加载全部药材（含库存），用于反向包含匹配
        try:
            all_meds = self._medicine_service.search_with_stock(keyword=None, limit=9999)
        except Exception as e:
            logger.error(f"加载药材列表失败: {e}")
            all_meds = []

        # 提取药材名集合，用于反向匹配（如「炙甘草」→「甘草」、「杏仁」→「苦杏仁」）
        all_med_names = []
        for row in all_meds:
            name = row.get('name') if isinstance(row, dict) else row[0]
            if name:
                all_med_names.append(name)
        # 按名称长度降序，保证优先匹配更长的药材名（避免「甘草」抢占「炙甘草」位置，
        # 反过来「炙甘草」找不到时再退回「甘草」）
        all_med_names.sort(key=len, reverse=True)

        added_count = 0
        not_found_names = []

        for item in items:
            orig_name = item.get('name', '') or ''
            qty = item.get('quantity', 0) or 0
            if not orig_name or qty <= 0:
                continue

            # 1) 精确匹配
            med_info = self._medicine_service.get_detail_for_prescription(orig_name)
            used_name = orig_name

            # 2) 反向包含匹配：找到药材名是 orig_name 的子串
            if not med_info:
                for med_name in all_med_names:
                    if med_name != orig_name and med_name in orig_name and len(med_name) >= 2:
                        candidate = self._medicine_service.get_detail_for_prescription(med_name)
                        if candidate:
                            med_info = candidate
                            used_name = med_name
                            break

            if not med_info:
                not_found_names.append(orig_name)
                continue

            if isinstance(med_info, dict):
                med_id = med_info.get('id')
                price = med_info.get('price', 0) or 0
                stock = med_info.get('quantity', 0) or 0
            else:
                med_id, price, stock = med_info[0], med_info[1] or 0, med_info[2] or 0

            if stock <= 0:
                not_found_names.append(f"{orig_name}(库存不足)")
                continue

            # 实际数量取方剂指定值；若超过库存则截断到库存上限
            actual_qty = min(qty, stock)

            existing_item = next((c for c in self.cart if c['id'] == med_id), None)
            if existing_item:
                new_qty = existing_item['qty'] + actual_qty
                if new_qty > stock:
                    new_qty = stock
                existing_item['qty'] = new_qty
                existing_item['amount'] = new_qty * existing_item['price']
            else:
                amount = actual_qty * price
                self.cart.append({
                    'id': med_id,
                    'name': used_name,
                    'qty': actual_qty,
                    'price': price,
                    'amount': amount
                })
            added_count += 1

        self.refresh_prescription_table()

        # 在主窗口状态栏提示应用结果
        status_bar = getattr(self.window(), 'status_bar', None)
        if status_bar is not None:
            if not_found_names:
                status_bar.showMessage(
                    f"方剂「{template_name}」已应用：添加 {added_count} 味药材，"
                    f"方剂中 {len(not_found_names)} 味药材未在库存中找到："
                    f"{', '.join(not_found_names)}",
                    8000
                )
            else:
                status_bar.showMessage(
                    f"方剂「{template_name}」已应用：添加 {added_count} 味药材",
                    5000
                )

        logger.info(
            f"应用方剂模板: {template_name}, 添加 {added_count} 味, "
            f"未找到 {len(not_found_names)} 味"
        )

    def _apply_responsive_table(self):
        for table in [self.med_list, self.prescription_table]:
            self.apply_responsive_table(table)

    def update_fonts(self):
        self._apply_responsive_table()


class PatientSelectDialog(QDialog):
    """患者选择对话框：搜索框 + 患者列表表格，支持双击选择"""

    def __init__(self, patient_service, parent=None):
        super().__init__(parent)
        self.patient_service = patient_service
        self.selected_patient = None
        # 当次搜索结果缓存（Patient 对象列表）
        self._patients = []
        self._init_ui()
        self._load_patients()

    def _init_ui(self):
        self.setWindowTitle('选择患者')
        self.setFixedSize(600, 400)
        self.setStyleSheet(get_dialog_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 顶部搜索栏
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        search_label = QLabel('搜索:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入姓名或电话搜索（回车刷新）...')
        # 输入变化时实时刷新（数据量通常不大，无需 debounce）
        self.search_input.textChanged.connect(self._load_patients)
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input, 1)
        layout.addLayout(search_row)

        # 患者列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', '姓名', '性别', '年龄', '电话', '过敏史'])
        # 隐藏 ID 列，仅供内部定位
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(36)
        # 双击选择患者
        self.table.doubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.table, 1)

        # 底部按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet(get_secondary_button_style(padding='8px 24px'))
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton('确定')
        ok_btn.setStyleSheet(get_button_style(AppColors.SUCCESS, padding='8px 24px'))
        ok_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _load_patients(self):
        """根据搜索关键词加载患者列表"""
        keyword = self.search_input.text().strip()
        try:
            self._patients = self.patient_service.search(keyword=keyword)
        except Exception as e:
            logger.error(f"加载患者列表失败: {e}")
            self._patients = []
        self._populate_table()

    def _populate_table(self):
        self.table.setRowCount(len(self._patients))
        for i, p in enumerate(self._patients):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id or '')))
            self.table.setItem(i, 1, QTableWidgetItem(p.name or ''))
            self.table.setItem(i, 2, QTableWidgetItem(p.gender or ''))
            age_text = str(p.age) if p.age is not None else ''
            self.table.setItem(i, 3, QTableWidgetItem(age_text))
            self.table.setItem(i, 4, QTableWidgetItem(p.phone or ''))
            self.table.setItem(i, 5, QTableWidgetItem(p.allergy or ''))

    def _on_double_clicked(self, index):
        """双击行直接选择并确认"""
        if not index.isValid():
            return
        if 0 <= index.row() < len(self._patients):
            self.selected_patient = self._patients[index.row()]
            self.accept()

    def _on_confirm(self):
        """点击「确定」按钮：基于当前选中行确认患者"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一位患者')
            return
        row = selected[0].row()
        if 0 <= row < len(self._patients):
            self.selected_patient = self._patients[row]
            self.accept()


class TemplateSelectionDialog(QDialog):
    """方剂模板选择对话框：支持搜索、按分类浏览、查看方剂详情"""

    def __init__(self, template_service: PrescriptionTemplateService, parent=None):
        super().__init__(parent)
        self.setWindowTitle('选择方剂模板')
        self.setMinimumSize(720, 560)
        self._template_service = template_service
        self._all_templates = template_service.load_templates()
        self.selected_template = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 顶部搜索栏
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        search_label = QLabel('搜索:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入方剂名称/功效/主治关键词...')
        self.search_input.textChanged.connect(self._refresh_list)

        cat_label = QLabel('分类:')
        self.cat_combo = QComboBox()
        self.cat_combo.addItem('全部', '')
        for cat in self._template_service.get_categories():
            self.cat_combo.addItem(cat, cat)
        self.cat_combo.currentIndexChanged.connect(self._refresh_list)

        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input, 3)
        search_row.addWidget(cat_label)
        search_row.addWidget(self.cat_combo, 2)
        layout.addLayout(search_row)

        # 方剂列表（QTreeWidget 按分类分组）
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['方剂名', '组成', '主治'])
        self.tree.setColumnWidth(0, 180)
        self.tree.setColumnWidth(1, 320)
        self.tree.setColumnWidth(2, 400)
        self.tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.tree, 3)

        # 详情区
        self.detail_label = QLabel('请选择方剂查看详情')
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.detail_label.setStyleSheet(
            f"padding: 10px; background: {AppColors.BG_SECONDARY}; "
            f"border: 1px solid {AppColors.BORDER}; border-radius: 4px; "
            f"color: {AppColors.TEXT_PRIMARY};"
        )
        self.detail_label.setMinimumHeight(80)
        layout.addWidget(self.detail_label, 1)

        # 底部按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet(get_secondary_button_style(padding='8px 24px'))
        cancel_btn.clicked.connect(self.reject)
        self.ok_btn = QPushButton('应用模板')
        self.ok_btn.setStyleSheet(get_button_style(AppColors.SUCCESS, padding='8px 24px'))
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.ok_btn)
        layout.addLayout(btn_row)

        self._refresh_list()

    def _refresh_list(self):
        """根据搜索关键词和分类筛选刷新方剂列表"""
        keyword = self.search_input.text().strip()
        category = self.cat_combo.currentData()

        if category:
            templates = self._template_service.get_by_category(category)
        else:
            templates = list(self._all_templates)

        if keyword:
            kw = keyword.lower()
            templates = [
                t for t in templates
                if kw in (t.get('name') or '').lower()
                or kw in (t.get('indication') or '').lower()
                or kw in (t.get('description') or '').lower()
            ]

        self.tree.clear()
        # 按分类分组
        cat_groups = {}
        for t in templates:
            cat = t.get('category', '其他')
            cat_groups.setdefault(cat, []).append(t)

        # 按 service 给出的分类顺序输出，保证稳定性
        ordered_cats = self._template_service.get_categories()
        for cat in ordered_cats:
            group = cat_groups.pop(cat, None)
            if not group:
                continue
            cat_item = QTreeWidgetItem([f'【{cat}】', '', ''])
            cat_item.setFlags(
                (cat_item.flags() & ~Qt.ItemIsSelectable) | Qt.ItemIsEnabled
            )
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            cat_item.setForeground(0, QBrush(QColor(AppColors.PRIMARY)))
            for t in group:
                composition = '、'.join(
                    f"{it.get('name', '')}{it.get('quantity', '')}{it.get('unit', '')}"
                    for it in t.get('items', [])
                )
                child = QTreeWidgetItem([
                    t.get('name', ''),
                    composition,
                    t.get('indication', '')
                ])
                child.setData(0, Qt.UserRole, t)
                cat_item.addChild(child)
            self.tree.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)

        # 兜底：剩余未归入已知分类的方剂
        for cat, group in cat_groups.items():
            cat_item = QTreeWidgetItem([f'【{cat}】', '', ''])
            cat_item.setFlags(
                (cat_item.flags() & ~Qt.ItemIsSelectable) | Qt.ItemIsEnabled
            )
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            for t in group:
                composition = '、'.join(
                    f"{it.get('name', '')}{it.get('quantity', '')}{it.get('unit', '')}"
                    for it in t.get('items', [])
                )
                child = QTreeWidgetItem([
                    t.get('name', ''),
                    composition,
                    t.get('indication', '')
                ])
                child.setData(0, Qt.UserRole, t)
                cat_item.addChild(child)
            self.tree.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)

    def _on_selection_changed(self):
        items = self.tree.selectedItems()
        if not items:
            self.selected_template = None
            self.ok_btn.setEnabled(False)
            self.detail_label.setText('请选择方剂查看详情')
            return

        item = items[0]
        t = item.data(0, Qt.UserRole)
        if not t:
            # 选中了分类节点，忽略
            self.tree.clearSelection()
            self.selected_template = None
            self.ok_btn.setEnabled(False)
            self.detail_label.setText('请选择具体的方剂（非分类节点）')
            return

        self.selected_template = t
        self.ok_btn.setEnabled(True)
        composition = '、'.join(
            f"{it.get('name', '')}{it.get('quantity', '')}{it.get('unit', '')}"
            for it in t.get('items', [])
        )
        self.detail_label.setText(
            f"<b style='font-size:14px;color:{AppColors.TEXT_HEADING};'>"
            f"{t.get('name', '')}</b>"
            f"&nbsp;&nbsp;<span style='color:{AppColors.TEXT_SECONDARY};'>"
            f"（{t.get('category', '')}）</span><br>"
            f"<b>组成：</b>{composition}<br>"
            f"<b>功效：</b>{t.get('description', '')}<br>"
            f"<b>主治：</b>{t.get('indication', '')}"
        )

    def _on_confirm(self):
        if self.selected_template:
            self.accept()
