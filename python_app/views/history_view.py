import logging

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core import PrescriptionService
from core.theme import AppColors, get_button_style, get_dialog_style, get_secondary_button_style, get_table_style
from utils.responsive_font import get_font_manager
from views.base_view import BaseDataView

logger = logging.getLogger('MedicineSystem')

# 分页默认配置
DEFAULT_PAGE_SIZE = 20
PAGE_SIZE_OPTIONS = [10, 20, 50, 100]


class OperationLogDialog(QDialog):
    def __init__(self, parent=None, log_data=None):
        super().__init__(parent)
        self.setWindowTitle('操作日志')
        self.setMinimumSize(500, 400)
        self.log_data = log_data or []
        self.font_manager = get_font_manager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet(get_dialog_style())

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(['操作类型', '目标类型', '目标ID', '操作者', '操作时间'])
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.log_table.setAlternatingRowColors(True)
        base_size = self.font_manager.current_base_size
        self.log_table.setStyleSheet(get_table_style(base_size, int(base_size * 1.1), max(4, int(base_size * 0.5))))

        self.load_logs()

        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet(get_button_style(AppColors.INFO, padding='8px 24px'))
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


class HistoryView(BaseDataView):
    def __init__(self, db):
        super().__init__(db)
        self._prescription_service = PrescriptionService(db)
        # 分页状态
        self._page = 1
        self._page_size = DEFAULT_PAGE_SIZE
        self._total_count = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        self.record_count_label = QLabel('共 0 条记录')
        self.record_count_label.setStyleSheet(f'color: {AppColors.TEXT_MUTED}; font-size: 13px;')
        header_layout.addStretch()
        header_layout.addWidget(self.record_count_label)

        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)

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
        search_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))
        search_btn.clicked.connect(self._on_search)

        reset_btn = QPushButton('重置')
        reset_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))
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

        # 分页控件
        page_label = QLabel('每页:')
        page_label.setStyleSheet(f'color: {AppColors.TEXT_MUTED}; font-size: 13px;')
        self.page_size_combo = QComboBox()
        for size in PAGE_SIZE_OPTIONS:
            self.page_size_combo.addItem(f'{size} 条', size)
        self.page_size_combo.setCurrentIndex(PAGE_SIZE_OPTIONS.index(DEFAULT_PAGE_SIZE))
        self.page_size_combo.setFixedWidth(80)
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)

        self.prev_btn = QPushButton('上一页')
        self.prev_btn.setObjectName('page_btn')
        self.prev_btn.clicked.connect(self._prev_page)

        self.page_info_label = QLabel('1 / 1')
        self.page_info_label.setStyleSheet(
            f'color: {AppColors.TEXT_SECONDARY}; font-size: 13px; padding: 0 8px;'
        )

        self.next_btn = QPushButton('下一页')
        self.next_btn.setObjectName('page_btn')
        self.next_btn.clicked.connect(self._next_page)

        btn_layout.addWidget(page_label)
        btn_layout.addWidget(self.page_size_combo)
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.page_info_label)
        btn_layout.addWidget(self.next_btn)

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
        self._apply_responsive_table()

        self.list_table.itemSelectionChanged.connect(self.show_detail)

    def _apply_styles(self):
        self.setStyleSheet(f'''
            QPushButton#refresh_btn {{
                background-color: {AppColors.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
                font-weight: 500;
            }}
            QPushButton#refresh_btn:hover {{
                background-color: {AppColors.PRIMARY_HOVER};
            }}
            QPushButton#view_log_btn {{
                background-color: {AppColors.BG_CARD};
                color: {AppColors.TEXT_SECONDARY};
                border: 1px solid {AppColors.BORDER};
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 100px;
                font-weight: 500;
            }}
            QPushButton#view_log_btn:hover {{
                border-color: {AppColors.TEXT_MUTED};
                color: {AppColors.TEXT_PRIMARY};
            }}
            QPushButton#page_btn {{
                background-color: {AppColors.BG_CARD};
                color: {AppColors.TEXT_SECONDARY};
                border: 1px solid {AppColors.BORDER};
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton#page_btn:hover {{
                border-color: {AppColors.PRIMARY};
                color: {AppColors.PRIMARY};
            }}
            QPushButton#page_btn:disabled {{
                color: {AppColors.TEXT_MUTED};
                background-color: {AppColors.BG_SECONDARY};
            }}
            QGroupBox {{
                font-weight: 600;
                color: {AppColors.TEXT_PRIMARY};
                border: 1px solid {AppColors.BORDER};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: {AppColors.BG_CARD};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }}
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
        self._page = 1
        self.refresh_data()

    def _on_search(self):
        """搜索条件变更后回到第一页再刷新"""
        self._page = 1
        self.refresh_data()

    def _total_pages(self) -> int:
        if self._page_size <= 0:
            return 1
        return max(1, (self._total_count + self._page_size - 1) // self._page_size)

    def _update_page_controls(self) -> None:
        """根据当前页和总数更新分页控件状态"""
        total_pages = self._total_pages()
        if self._page > total_pages:
            self._page = total_pages
        self.page_info_label.setText(f'{self._page} / {total_pages}')
        self.prev_btn.setEnabled(self._page > 1)
        self.next_btn.setEnabled(self._page < total_pages)
        start = (self._page - 1) * self._page_size + 1 if self._total_count > 0 else 0
        end = min(self._page * self._page_size, self._total_count)
        self.record_count_label.setText(
            f'共 {self._total_count} 条记录（第 {start}-{end} 条）'
        )

    def _on_page_size_changed(self) -> None:
        self._page_size = self.page_size_combo.currentData()
        self._page = 1
        self.refresh_data()

    def _prev_page(self) -> None:
        if self._page > 1:
            self._page -= 1
            self.refresh_data()

    def _next_page(self) -> None:
        if self._page < self._total_pages():
            self._page += 1
            self.refresh_data()

    def refresh_data(self):
        try:
            name = self.name_search.text().strip() or None
            date_from = self.date_from.date().toString('yyyy-MM-dd')
            date_to = self.date_to.date().toString('yyyy-MM-dd')

            # 先统计总数（用于分页计算）
            self._total_count = self._prescription_service.count_all(
                start_date=date_from, end_date=date_to, patient_name=name
            )

            # 边界保护：当前页超出总页数时回到最后一页
            total_pages = self._total_pages()
            if self._page > total_pages:
                self._page = total_pages

            offset = (self._page - 1) * self._page_size
            prescriptions = self._prescription_service.get_all(
                start_date=date_from,
                end_date=date_to,
                patient_name=name,
                limit=self._page_size,
                offset=offset
            )

            self.list_table.setRowCount(len(prescriptions))
            for i, pres in enumerate(prescriptions):
                data_list = [
                    pres.id, pres.patient_name, pres.patient_age,
                    pres.diagnosis, pres.total_amount,
                    str(pres.created_at) if pres.created_at else ''
                ]

                for j, data in enumerate(data_list):
                    item = QTableWidgetItem(str(data) if data else '')
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.list_table.setItem(i, j, item)

                delete_btn = QPushButton('删除')
                delete_btn.setProperty('prescription_id', pres.id)
                delete_btn.setProperty('row_index', i)
                delete_btn.clicked.connect(self._on_delete_clicked)
                delete_btn.setStyleSheet(get_button_style(AppColors.DANGER, padding='4px 12px'))

                self.list_table.setCellWidget(i, 6, delete_btn)

            self._update_page_controls()
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
            f'<p style="color: {AppColors.DANGER}; font-weight: bold;">此操作不可撤销！</p>'
            f'<p>处方ID: {prescription_id}</p>'
            f'<p>患者姓名: {patient_name}</p>',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._delete_prescription(prescription_id, patient_name)

    def _delete_prescription(self, prescription_id, patient_name):
        try:
            self._prescription_service.delete(prescription_id, '系统管理员')

            logger.info(f"删除处方成功: ID={prescription_id}, 患者={patient_name}")
            QMessageBox.information(self, '删除成功', '处方记录已成功删除')
            self.refresh_data()

            self.detail_table.setRowCount(0)

        except Exception as e:
            logger.error(f"删除处方失败: {e}")
            QMessageBox.critical(self, '删除失败', f'删除处方记录时发生错误：\n{str(e)}')

    def show_detail(self):
        try:
            selected = self.list_table.selectedItems()
            if not selected:
                return

            id_item = self.list_table.item(selected[0].row(), 0)
            if not id_item:
                return
            try:
                pres_id = int(id_item.text())
            except (ValueError, TypeError):
                QMessageBox.warning(self, '错误', '无法解析处方编号')
                return

            # 通过 Service 层查询处方明细，遵循分层架构
            rows = self._prescription_service.get_items_by_id(pres_id)

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

    def _apply_responsive_table(self):
        for table in [self.list_table, self.detail_table]:
            self.apply_responsive_table(table)

    def update_fonts(self):
        self._apply_responsive_table()
        self.refresh_data()

    def show_operation_logs(self):
        try:
            # 通过 Service 层查询操作日志，遵循分层架构
            logs = self._prescription_service.get_operation_logs(
                target_type='prescription', limit=100
            )

            dialog = OperationLogDialog(self, logs)
            dialog.exec()
        except Exception as e:
            logger.error(f"显示操作日志失败: {e}")
            QMessageBox.critical(self, '错误', f'获取操作日志失败：{str(e)}')
