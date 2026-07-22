# -*- coding: utf-8 -*-
"""
患者档案管理视图

提供医生管理患者档案的界面：
- 搜索栏（按姓名/电话搜索）
- 患者列表表格
- 新增/编辑/删除患者（QDialog 表单）
- 双击患者行 → 查看详情对话框（含处方历史和统计数据）
- 导出 CSV

参考 medicine_view.py 的代码风格和模式（分页、CRUD、导出）。
"""
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from core import Patient, PatientService
from core.theme import (
    AppColors,
    get_button_style,
    get_dialog_style,
    get_secondary_button_style,
)
from views.base_view import BaseDataView


class PatientDialog(QDialog):
    """患者档案新增/编辑对话框"""

    def __init__(self, parent=None, patient_data: Optional[dict] = None):
        super().__init__(parent)
        self._patient_data = patient_data
        self.setWindowTitle('患者档案')
        self.setFixedWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.setStyleSheet(get_dialog_style())

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入患者姓名')

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['', '男', '女'])

        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 150)
        self.age_spin.setSpecialValueText('')

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText('联系电话')

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText('地址')

        self.allergy_edit = QTextEdit()
        self.allergy_edit.setMaximumHeight(60)
        self.allergy_edit.setPlaceholderText('过敏史，如：青霉素过敏')

        self.medical_history_edit = QTextEdit()
        self.medical_history_edit.setMaximumHeight(80)
        self.medical_history_edit.setPlaceholderText('既往病史')

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText('备注')

        layout.addRow('姓名*:', self.name_edit)
        layout.addRow('性别:', self.gender_combo)
        layout.addRow('年龄:', self.age_spin)
        layout.addRow('电话:', self.phone_edit)
        layout.addRow('地址:', self.address_edit)
        layout.addRow('过敏史:', self.allergy_edit)
        layout.addRow('既往病史:', self.medical_history_edit)
        layout.addRow('备注:', self.notes_edit)

        btn_box = QHBoxLayout()
        self.ok_btn = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.ok_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addRow(btn_box)

        if self._patient_data:
            self._populate_fields(self._patient_data)

    def _populate_fields(self, data: dict):
        self.name_edit.setText(data.get('name', '') or '')
        gender = data.get('gender', '') or ''
        idx = self.gender_combo.findText(gender)
        if idx >= 0:
            self.gender_combo.setCurrentIndex(idx)
        age = data.get('age')
        if age is not None:
            self.age_spin.setValue(int(age))
        else:
            self.age_spin.setValue(0)
        self.phone_edit.setText(data.get('phone', '') or '')
        self.address_edit.setText(data.get('address', '') or '')
        self.allergy_edit.setText(data.get('allergy', '') or '')
        self.medical_history_edit.setText(data.get('medical_history', '') or '')
        self.notes_edit.setText(data.get('notes', '') or '')

    def get_data(self) -> dict:
        age_value = self.age_spin.value()
        return {
            'name': self.name_edit.text().strip(),
            'gender': self.gender_combo.currentText(),
            'age': age_value if age_value > 0 else None,
            'phone': self.phone_edit.text().strip(),
            'address': self.address_edit.text().strip(),
            'allergy': self.allergy_edit.toPlainText().strip(),
            'medical_history': self.medical_history_edit.toPlainText().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
        }


class PatientDetailDialog(QDialog):
    """患者详情对话框：基本信息 + 医疗信息 + 统计数据 + 处方历史"""

    def __init__(self, parent=None, patient: Optional[Patient] = None,
                 patient_service: Optional[PatientService] = None):
        super().__init__(parent)
        self._patient = patient
        self._service = patient_service
        self.setWindowTitle(f'患者详情 - {patient.name if patient else ""}')
        self.setMinimumSize(720, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet(get_dialog_style())

        if not self._patient:
            layout.addWidget(QLabel('未提供患者信息'))
            close_btn = QPushButton('关闭')
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)
            return

        # 1. 基本信息区
        basic_group = QGroupBox('基本信息')
        basic_grid = QGridLayout(basic_group)
        basic_grid.setHorizontalSpacing(20)
        basic_grid.setVerticalSpacing(8)
        basic_grid.addWidget(QLabel('姓名:'), 0, 0)
        basic_grid.addWidget(QLabel(self._patient.name or '-'), 0, 1)
        basic_grid.addWidget(QLabel('性别:'), 0, 2)
        basic_grid.addWidget(QLabel(self._patient.gender or '-'), 0, 3)
        basic_grid.addWidget(QLabel('年龄:'), 1, 0)
        age_text = str(self._patient.age) if self._patient.age is not None else '-'
        basic_grid.addWidget(QLabel(age_text), 1, 1)
        basic_grid.addWidget(QLabel('电话:'), 1, 2)
        basic_grid.addWidget(QLabel(self._patient.phone or '-'), 1, 3)
        basic_grid.addWidget(QLabel('地址:'), 2, 0)
        addr_label = QLabel(self._patient.address or '-')
        addr_label.setWordWrap(True)
        basic_grid.addWidget(addr_label, 2, 1, 1, 3)
        layout.addWidget(basic_group)

        # 2. 医疗信息区
        medical_group = QGroupBox('医疗信息')
        medical_layout = QFormLayout(medical_group)
        medical_layout.addRow('过敏史:', self._make_text_label(self._patient.allergy))
        medical_layout.addRow('既往病史:', self._make_text_label(self._patient.medical_history))
        medical_layout.addRow('备注:', self._make_text_label(self._patient.notes))
        layout.addWidget(medical_group)

        # 3. 统计数据区
        stats_group = QGroupBox('统计数据')
        stats_grid = QGridLayout(stats_group)
        stats_grid.setHorizontalSpacing(20)
        stats_grid.setVerticalSpacing(8)

        stats = {}
        if self._service is not None:
            try:
                stats = self._service.get_statistics(self._patient.id)
            except Exception:
                stats = {}

        stats_grid.addWidget(QLabel('处方数:'), 0, 0)
        stats_grid.addWidget(QLabel(str(stats.get('prescription_count', 0))), 0, 1)
        stats_grid.addWidget(QLabel('总消费:'), 0, 2)
        stats_grid.addWidget(QLabel(f"¥{stats.get('total_amount', 0):.2f}"), 0, 3)
        stats_grid.addWidget(QLabel('首次就诊:'), 1, 0)
        stats_grid.addWidget(QLabel(self._fmt_dt(stats.get('first_visit'))), 1, 1)
        stats_grid.addWidget(QLabel('最近就诊:'), 1, 2)
        stats_grid.addWidget(QLabel(self._fmt_dt(stats.get('last_visit'))), 1, 3)
        layout.addWidget(stats_group)

        # 4. 处方历史表格
        rx_group = QGroupBox('处方历史')
        rx_layout = QVBoxLayout(rx_group)

        self.rx_table = QTableWidget()
        self.rx_table.setColumnCount(4)
        self.rx_table.setHorizontalHeaderLabels(['日期', '诊断', '金额', '操作'])
        self.rx_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rx_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rx_table.setAlternatingRowColors(True)
        self.rx_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.rx_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.rx_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.rx_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.rx_table.verticalHeader().setVisible(False)

        prescriptions = []
        if self._service is not None:
            try:
                prescriptions = self._service.get_prescriptions(self._patient.id)
            except Exception:
                prescriptions = []

        self._prescriptions = prescriptions
        self.rx_table.setRowCount(len(prescriptions))
        for row_idx, rx in enumerate(prescriptions):
            date_item = QTableWidgetItem(self._fmt_dt(rx.get('created_at')))
            date_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.rx_table.setItem(row_idx, 0, date_item)

            diagnosis = rx.get('diagnosis') or '-'
            diag_item = QTableWidgetItem(str(diagnosis))
            diag_item.setToolTip(str(diagnosis))
            self.rx_table.setItem(row_idx, 1, diag_item)

            amount = rx.get('total_amount') or 0
            amount_item = QTableWidgetItem(f'¥{float(amount):.2f}')
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.rx_table.setItem(row_idx, 2, amount_item)

            view_btn = QPushButton('查看详情')
            view_btn.setStyleSheet(get_secondary_button_style(padding='4px 10px'))
            view_btn.clicked.connect(lambda checked, pid=rx.get('prescription_id'): self._view_prescription(pid))
            self.rx_table.setCellWidget(row_idx, 3, view_btn)

        rx_layout.addWidget(self.rx_table)
        layout.addWidget(rx_group, 1)

        # 关闭按钮
        btn_bar = QHBoxLayout()
        btn_bar.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet(get_secondary_button_style(padding='8px 24px'))
        close_btn.clicked.connect(self.accept)
        btn_bar.addWidget(close_btn)
        layout.addLayout(btn_bar)

    @staticmethod
    def _make_text_label(text: str) -> QLabel:
        label = QLabel(text or '无')
        label.setWordWrap(True)
        label.setMinimumHeight(28)
        return label

    @staticmethod
    def _fmt_dt(dt) -> str:
        if not dt:
            return '-'
        try:
            return str(dt)[:19]
        except Exception:
            return str(dt)

    def _view_prescription(self, prescription_id: Optional[int]):
        """查看处方详情（提示信息，实际处方详情在处方历史页查看）"""
        if prescription_id is None:
            return
        QMessageBox.information(
            self, '处方详情',
            f'处方编号: {prescription_id}\n\n可在「处方历史」页面查看完整明细。'
        )


class PatientView(BaseDataView):
    """患者档案管理页面"""
    # 前端分页配置（数据来自内存，无需数据库分页）
    DEFAULT_PAGE_SIZE = 50
    PAGE_SIZE_OPTIONS = [20, 50, 100, 200]

    def __init__(self, db, patient_service=None):
        super().__init__(db)
        self._patient_service = patient_service if patient_service is not None else PatientService(db)
        self._base_column_widths = [0, 100, 60, 60, 130, 150, 150]
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._delayed_search)
        self._full_data = []
        # 分页状态
        self._page = 1
        self._page_size = self.DEFAULT_PAGE_SIZE
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索患者姓名或电话...')
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self._on_search_text_changed)

        self.reset_btn = QPushButton('重置')
        self.reset_btn.setStyleSheet(get_secondary_button_style(padding='10px 16px'))
        self.reset_btn.clicked.connect(self.reset_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.reset_btn)
        search_layout.addStretch()

        # 按钮栏
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(12)

        self.add_btn = QPushButton('+ 新增患者')
        self.edit_btn = QPushButton('编辑')
        self.del_btn = QPushButton('删除')
        self.view_detail_btn = QPushButton('详情')
        self.export_btn = QPushButton('导出')

        self.add_btn.setStyleSheet(get_button_style(AppColors.SUCCESS, padding='10px 20px'))
        self.edit_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))
        self.del_btn.setStyleSheet(get_button_style(AppColors.DANGER, padding='10px 20px'))
        self.view_detail_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))
        self.export_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))

        self.add_btn.clicked.connect(self.add_patient)
        self.edit_btn.clicked.connect(self.edit_patient)
        self.del_btn.clicked.connect(self.del_patient)
        self.view_detail_btn.clicked.connect(self.view_detail)
        self.export_btn.clicked.connect(self.export_data)

        btn_bar.addWidget(self.add_btn)
        btn_bar.addWidget(self.edit_btn)
        btn_bar.addWidget(self.del_btn)
        btn_bar.addWidget(self.view_detail_btn)
        btn_bar.addWidget(self.export_btn)
        btn_bar.addStretch()

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', '姓名', '性别', '年龄', '电话', '过敏史', '创建日期'
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(48)
        # 双击行查看详情
        self.table.doubleClicked.connect(self._on_row_double_clicked)

        self._apply_responsive_table()

        self.stats_label = QLabel('共 0 名患者')
        self.stats_label.setStyleSheet(f'color: {AppColors.TEXT_MUTED}; font-size: 12px;')

        # 分页控件
        pager_layout = QHBoxLayout()
        pager_layout.setSpacing(8)
        pager_layout.addWidget(self.stats_label)
        pager_layout.addStretch()

        page_size_label = QLabel('每页:')
        page_size_label.setStyleSheet(f'color: {AppColors.TEXT_MUTED}; font-size: 12px;')
        self.page_size_combo = QComboBox()
        for size in self.PAGE_SIZE_OPTIONS:
            self.page_size_combo.addItem(f'{size} 条', size)
        self.page_size_combo.setCurrentIndex(self.PAGE_SIZE_OPTIONS.index(self.DEFAULT_PAGE_SIZE))
        self.page_size_combo.setFixedWidth(80)
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)

        self.prev_btn = QPushButton('上一页')
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn = QPushButton('下一页')
        self.next_btn.clicked.connect(self._next_page)
        self.page_info_label = QLabel('1 / 1')
        self.page_info_label.setStyleSheet(
            f'color: {AppColors.TEXT_SECONDARY}; font-size: 12px; padding: 0 8px;'
        )

        pager_layout.addWidget(page_size_label)
        pager_layout.addWidget(self.page_size_combo)
        pager_layout.addWidget(self.prev_btn)
        pager_layout.addWidget(self.page_info_label)
        pager_layout.addWidget(self.next_btn)

        layout.addLayout(search_layout)
        layout.addLayout(btn_bar)
        layout.addWidget(self.table)
        layout.addLayout(pager_layout)

    # ---- 搜索与分页 ----
    def _on_search_text_changed(self):
        self._search_timer.start(200)

    def _delayed_search(self):
        self._page = 1
        self.load_data()

    def reset_search(self):
        self.search_input.clear()
        self._page = 1
        self.load_data()

    def _total_pages(self) -> int:
        if self._page_size <= 0:
            return 1
        return max(1, (len(self._full_data) + self._page_size - 1) // self._page_size)

    def _update_page_controls(self):
        total = len(self._full_data)
        total_pages = self._total_pages()
        if self._page > total_pages:
            self._page = total_pages
        self.page_info_label.setText(f'{self._page} / {total_pages}')
        self.prev_btn.setEnabled(self._page > 1)
        self.next_btn.setEnabled(self._page < total_pages)
        start = (self._page - 1) * self._page_size + 1 if total > 0 else 0
        end = min(self._page * self._page_size, total)
        self.stats_label.setText(f'共 {total} 名患者（第 {start}-{end} 名）')

    def _on_page_size_changed(self):
        self._page_size = self.page_size_combo.currentData()
        self._page = 1
        self._populate_table()

    def _prev_page(self):
        if self._page > 1:
            self._page -= 1
            self._populate_table()

    def _next_page(self):
        if self._page < self._total_pages():
            self._page += 1
            self._populate_table()

    # ---- 数据加载 ----
    def load_data(self):
        keyword = self.search_input.text().strip()
        self._full_data = self._patient_service.search(keyword=keyword)
        self._populate_table()

    def _populate_table(self):
        self.table.setUpdatesEnabled(False)
        try:
            total_pages = self._total_pages()
            if self._page > total_pages:
                self._page = total_pages
            start = (self._page - 1) * self._page_size
            end = start + self._page_size
            page_data = self._full_data[start:end]
            self.table.setRowCount(len(page_data))
            for row_idx, patient in enumerate(page_data):
                self._set_table_row(row_idx, patient)
        finally:
            self.table.setUpdatesEnabled(True)
        self._update_page_controls()

    def _set_table_row(self, row_idx, patient: Patient):
        values = [
            patient.id if patient.id is not None else '',
            patient.name or '',
            patient.gender or '',
            patient.age if patient.age is not None else '',
            patient.phone or '',
            patient.allergy or '',
            (patient.created_at or '')[:19],
        ]
        for col_idx, value in enumerate(values):
            text = str(value) if value != '' else ''
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            if col_idx in (2, 3):  # 性别、年龄居中
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.table.setItem(row_idx, col_idx, item)

    def _get_patient_at_table_row(self, table_row: int) -> Optional[Patient]:
        """表格行号（页内）→ 对应的全量数据条目"""
        if not self._full_data or table_row < 0:
            return None
        start = (self._page - 1) * self._page_size
        full_idx = start + table_row
        if 0 <= full_idx < len(self._full_data):
            return self._full_data[full_idx]
        return None

    def _on_row_double_clicked(self, index):
        """双击行查看详情"""
        if not index.isValid():
            return
        patient = self._get_patient_at_table_row(index.row())
        if patient:
            self._show_detail_dialog(patient)

    # ---- CRUD ----
    def add_patient(self):
        dialog = PatientDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data.get('name'):
                QMessageBox.warning(self, '提示', '请输入患者姓名！')
                return

            try:
                patient = Patient(**data)
                self._patient_service.create(patient)
                QMessageBox.information(self, '成功', '患者档案添加成功！')
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')

    def edit_patient(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        patient = self._get_patient_at_table_row(row)
        if not patient:
            QMessageBox.warning(self, '提示', '无法定位患者数据')
            return

        dialog = PatientDialog(self, patient_data=patient.to_dict())
        if dialog.exec():
            data = dialog.get_data()
            if not data.get('name'):
                QMessageBox.warning(self, '提示', '请输入患者姓名！')
                return

            try:
                patient.name = data['name']
                patient.gender = data['gender']
                patient.age = data['age']
                patient.phone = data['phone']
                patient.address = data['address']
                patient.allergy = data['allergy']
                patient.medical_history = data['medical_history']
                patient.notes = data['notes']
                self._patient_service.update(patient)
                QMessageBox.information(self, '成功', '修改成功！')
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'修改失败: {str(e)}')

    def del_patient(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        patient = self._get_patient_at_table_row(row)
        if not patient:
            QMessageBox.warning(self, '提示', '无法定位患者数据')
            return

        reply = QMessageBox.question(
            self, '确认',
            f'确定要删除患者 "{patient.name}" 吗？\n注意：历史处方记录将保留。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self._patient_service.delete(patient.id)
                QMessageBox.information(self, '成功', '删除成功！')
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败：{str(e)}')

    def view_detail(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        patient = self._get_patient_at_table_row(row)
        if not patient:
            QMessageBox.warning(self, '提示', '无法定位患者数据')
            return
        self._show_detail_dialog(patient)

    def _show_detail_dialog(self, patient: Patient):
        dialog = PatientDetailDialog(self, patient=patient, patient_service=self._patient_service)
        dialog.exec()

    def export_data(self):
        try:
            import csv

            from PySide6.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(
                self, '导出患者数据', 'patients_export.csv', 'CSV文件 (*.csv)'
            )
            if not filename:
                return

            # 导出当前搜索结果全集（非当前页）
            rows = [p.to_dict() for p in self._full_data]
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', '姓名', '性别', '年龄', '电话', '地址',
                    '过敏史', '既往病史', '备注', '创建日期', '更新日期'
                ])
                for row in rows:
                    writer.writerow([
                        row.get('id', ''),
                        row.get('name', ''),
                        row.get('gender', ''),
                        row.get('age', ''),
                        row.get('phone', ''),
                        row.get('address', ''),
                        row.get('allergy', ''),
                        row.get('medical_history', ''),
                        row.get('notes', ''),
                        row.get('created_at', ''),
                        row.get('updated_at', ''),
                    ])
            QMessageBox.information(self, '成功', '数据导出成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'导出失败: {str(e)}')

    # ---- 响应式 ----
    def _apply_responsive_table(self):
        if hasattr(self, 'table'):
            self.apply_responsive_table(
                self.table, self._base_column_widths,
                getattr(self, 'stats_label', None)
            )

    def update_fonts(self):
        self._apply_responsive_table()
        self.load_data()
