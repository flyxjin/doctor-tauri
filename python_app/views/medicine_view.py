# -*- coding: utf-8 -*-
import html
import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from core import Medicine, MedicineService, Timer, get_medicine_cache, measure
from core.theme import AppColors, get_button_style, get_dialog_style, get_secondary_button_style
from views.base_view import BaseDataView


class MedicineDialog(QDialog):
    """药材信息对话框"""

    # 标准药材分类（作为数据库无数据时的兜底，保证可用性）
    DEFAULT_CATEGORIES = [
        '补虚药', '解表药', '清热药', '泻下药', '祛风湿药', '化湿药',
        '利水渗湿药', '温里药', '理气药', '消食药', '驱虫药', '止血药',
        '活血化瘀药', '化痰止咳平喘药', '安神药', '平肝息风药', '开窍药',
        '收涩药', '攻毒杀虫止痒药', '拔毒化腐生肌药',
    ]

    def __init__(self, parent=None, medicine_data=None, medicine_service=None):
        super().__init__(parent)
        self.medicine_data = medicine_data
        self._medicine_service = medicine_service
        self.setWindowTitle('药材信息')
        self.setFixedWidth(500)
        self.init_ui()

    def _load_categories(self) -> list:
        """从数据库加载分类列表；为空时回退到 DEFAULT_CATEGORIES 兜底"""
        if self._medicine_service is not None:
            try:
                db_categories = self._medicine_service.get_categories()
                if db_categories:
                    return db_categories
            except Exception as e:
                logging.getLogger('MedicineSystem').warning(f"加载分类列表失败，使用默认分类: {e}")
        return self.DEFAULT_CATEGORIES

    def init_ui(self):
        layout = QFormLayout(self)
        self.setStyleSheet(get_dialog_style())

        self.name_edit = QLineEdit()
        self.alias_edit = QLineEdit()
        self.category_combo = QComboBox()
        # 第一项为空（未分类），其余从数据库动态加载，回退到默认分类
        categories = self._load_categories()
        self.category_combo.addItems([''] + categories)
        self.nature_combo = QComboBox()
        self.nature_combo.addItems(['', '寒', '热', '温', '凉', '平', '微寒', '微温', '大寒'])
        self.taste_edit = QLineEdit()
        self.meridian_edit = QLineEdit()
        self.efficacy_edit = QTextEdit()
        self.efficacy_edit.setMaximumHeight(60)
        self.indications_edit = QTextEdit()
        self.indications_edit.setMaximumHeight(60)
        self.usage_edit = QLineEdit()
        self.dosage_edit = QLineEdit()
        self.contraindication_edit = QTextEdit()
        self.contraindication_edit.setMaximumHeight(60)
        self.notes_edit = QLineEdit()

        layout.addRow('药材名称*:', self.name_edit)
        layout.addRow('别名:', self.alias_edit)
        layout.addRow('分类:', self.category_combo)
        layout.addRow('药性:', self.nature_combo)
        layout.addRow('药味:', self.taste_edit)
        layout.addRow('归经:', self.meridian_edit)
        layout.addRow('功效:', self.efficacy_edit)
        layout.addRow('主治:', self.indications_edit)
        layout.addRow('用法:', self.usage_edit)
        layout.addRow('用量:', self.dosage_edit)
        layout.addRow('禁忌:', self.contraindication_edit)
        layout.addRow('备注:', self.notes_edit)

        btn_box = QHBoxLayout()
        self.ok_btn = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.ok_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addRow(btn_box)

        if self.medicine_data:
            self._populate_fields(self.medicine_data)

    def _populate_fields(self, data):
        if not isinstance(data, dict):
            return
        self.name_edit.setText(data.get('name', ''))
        self.alias_edit.setText(data.get('alias', ''))
        index = self.category_combo.findText(data.get('category', ''))
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        index = self.nature_combo.findText(data.get('nature', ''))
        if index >= 0:
            self.nature_combo.setCurrentIndex(index)
        self.taste_edit.setText(data.get('taste', ''))
        self.meridian_edit.setText(data.get('meridian', ''))
        self.efficacy_edit.setText(data.get('efficacy', ''))
        self.indications_edit.setText(data.get('indications', ''))
        self.usage_edit.setText(data.get('usage', ''))
        self.dosage_edit.setText(data.get('dosage', ''))
        self.contraindication_edit.setText(data.get('contraindication', ''))
        self.notes_edit.setText(data.get('notes', ''))

    def get_data(self):
        return (
            self.name_edit.text(),
            self.alias_edit.text(),
            self.category_combo.currentText(),
            self.nature_combo.currentText(),
            self.taste_edit.text(),
            self.meridian_edit.text(),
            self.efficacy_edit.toPlainText(),
            self.indications_edit.toPlainText(),
            self.usage_edit.text(),
            self.dosage_edit.text(),
            self.contraindication_edit.toPlainText(),
            self.notes_edit.text()
        )


class MedicineView(BaseDataView):
    # 前端分页配置（数据来自内存缓存，无需数据库分页）
    DEFAULT_PAGE_SIZE = 50
    PAGE_SIZE_OPTIONS = [20, 50, 100, 200]

    def __init__(self, db):
        super().__init__(db)
        self._medicine_service = MedicineService(db)
        self._base_column_widths = [0, 120, 100, 100, 80, 100, 150]
        self._cache = get_medicine_cache()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._delayed_search)
        self._full_data = []
        # 分页状态
        self._page = 1
        self._page_size = self.DEFAULT_PAGE_SIZE
        self.init_ui()
        self._init_cache()

    def _init_cache(self):
        # 重新获取缓存引用（invalidate_medicine_cache 会将全局变量置为 None）
        self._cache = get_medicine_cache()
        if not self._cache.is_initialized():
            with Timer('cache_initialization'):
                med_list = self._medicine_service.get_all_as_dicts()
                self._cache.initialize(med_list)
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索药材名称、别名或功效...')
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self._on_search_text_changed)

        self.category_filter = QComboBox()
        self.category_filter.addItems(['全部分类'])
        self.category_filter.currentIndexChanged.connect(self._on_filter_changed)

        self.nature_filter = QComboBox()
        self.nature_filter.addItems(['全部药性', '寒', '热', '温', '凉', '平', '微寒', '微温', '大寒'])
        self.nature_filter.currentIndexChanged.connect(self._on_filter_changed)

        self.reset_btn = QPushButton('重置')
        self.reset_btn.setStyleSheet(get_secondary_button_style(padding='10px 16px'))
        self.reset_btn.clicked.connect(self.reset_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(self.nature_filter)
        search_layout.addWidget(self.reset_btn)
        search_layout.addStretch()

        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(12)

        self.add_btn = QPushButton('+ 添加药材')
        self.edit_btn = QPushButton('编辑')
        self.del_btn = QPushButton('删除')
        self.view_detail_btn = QPushButton('详情')
        self.export_btn = QPushButton('导出')

        self.add_btn.setStyleSheet(get_button_style(AppColors.SUCCESS, padding='10px 20px'))
        self.edit_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))
        self.del_btn.setStyleSheet(get_button_style(AppColors.DANGER, padding='10px 20px'))
        self.view_detail_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))
        self.export_btn.setStyleSheet(get_secondary_button_style(padding='10px 20px'))

        self.add_btn.clicked.connect(self.add_medicine)
        self.edit_btn.clicked.connect(self.edit_medicine)
        self.del_btn.clicked.connect(self.del_medicine)
        self.view_detail_btn.clicked.connect(self.view_detail)
        self.export_btn.clicked.connect(self.export_data)

        btn_bar.addWidget(self.add_btn)
        btn_bar.addWidget(self.edit_btn)
        btn_bar.addWidget(self.del_btn)
        btn_bar.addWidget(self.view_detail_btn)
        btn_bar.addWidget(self.export_btn)
        btn_bar.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID', '名称', '别名', '分类', '药性', '药味', '归经'
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(48)

        self._apply_responsive_table()

        self.stats_label = QLabel('共 0 味药材')
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

    def _on_search_text_changed(self):
        self._search_timer.start(200)

    def _on_filter_changed(self):
        self._search_timer.start(100)

    def _delayed_search(self):
        # 搜索/筛选变更后回到第一页
        self._page = 1
        self.load_data()

    def reset_search(self):
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.nature_filter.setCurrentIndex(0)
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
        self.stats_label.setText(f'共 {total} 味药材（第 {start}-{end} 味）')

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

    @measure('MedicineView.load_data')
    def load_data(self):
        keyword = self.search_input.text()
        category = self.category_filter.currentText()
        nature = self.nature_filter.currentText()

        if category == '全部分类':
            category = None
        if nature == '全部药性':
            nature = None

        with Timer('cache_search'):
            self._full_data = self._cache.search(keyword, category, nature)

        self._populate_table()

    def _populate_table(self):
        self.table.setUpdatesEnabled(False)
        try:
            # 前端分页：切片显示当前页数据
            total_pages = self._total_pages()
            if self._page > total_pages:
                self._page = total_pages
            start = (self._page - 1) * self._page_size
            end = start + self._page_size
            page_data = self._full_data[start:end]
            self.table.setRowCount(len(page_data))
            for row_idx, med in enumerate(page_data):
                self._set_table_row(row_idx, med)
        finally:
            self.table.setUpdatesEnabled(True)
        self._update_page_controls()

    def _set_table_row(self, row_idx, med):
        fields = ['id', 'name', 'alias', 'category', 'nature', 'taste', 'meridian']
        for col_idx, field in enumerate(fields):
            value = med.get(field, '')
            item = QTableWidgetItem(str(value) if value else '')
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, col_idx, item)

    def _get_med_at_table_row(self, table_row: int) -> Optional[dict]:
        """表格行号（页内）→ 对应的全量数据条目。

        分页后表格行号是页内索引，需加上当前页起始偏移才能定位到 _full_data。
        """
        if not self._full_data or table_row < 0:
            return None
        start = (self._page - 1) * self._page_size
        full_idx = start + table_row
        if 0 <= full_idx < len(self._full_data):
            return self._full_data[full_idx]
        return None

    def add_medicine(self):
        dialog = MedicineDialog(self, medicine_service=self._medicine_service)
        if dialog.exec():
            data = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, '提示', '请输入药材名称！')
                return

            from core import MedicineValidator
            medicine_dict = {
                'name': data[0], 'alias': data[1], 'category': data[2], 'nature': data[3],
                'taste': data[4], 'meridian': data[5], 'efficacy': data[6], 'indications': data[7],
                'usage': data[8], 'dosage': data[9], 'contraindication': data[10], 'notes': data[11]
            }
            is_valid, errors = MedicineValidator.validate(medicine_dict)
            if not is_valid:
                QMessageBox.warning(self, '验证失败', '\n'.join(errors))
                return

            try:
                medicine = Medicine(**medicine_dict)
                self._medicine_service.create(medicine)
                # 缓存由 Service 层 _sync_cache_add 自动同步，无需手动操作
                QMessageBox.information(self, '成功', '药材添加成功！')
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')

    def edit_medicine(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        medicine_data = self._get_med_at_table_row(row)
        if not medicine_data:
            QMessageBox.warning(self, '提示', '无法定位药材数据')
            return

        dialog = MedicineDialog(self, medicine_data, medicine_service=self._medicine_service)
        if dialog.exec():
            data = dialog.get_data()
            if not data[0]:
                QMessageBox.warning(self, '提示', '请输入药材名称！')
                return

            from core import MedicineValidator
            medicine_dict = {
                'name': data[0], 'alias': data[1], 'category': data[2], 'nature': data[3],
                'taste': data[4], 'meridian': data[5], 'efficacy': data[6], 'indications': data[7],
                'usage': data[8], 'dosage': data[9], 'contraindication': data[10], 'notes': data[11]
            }
            is_valid, errors = MedicineValidator.validate(medicine_dict)
            if not is_valid:
                QMessageBox.warning(self, '验证失败', '\n'.join(errors))
                return

            med_id = medicine_data['id']
            medicine = Medicine(id=med_id, **medicine_dict)
            try:
                self._medicine_service.update(medicine)
                # 缓存由 Service 层 _sync_cache_update 自动同步（含库存字段）
                QMessageBox.information(self, '成功', '修改成功！')
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'修改失败: {str(e)}')

    def del_medicine(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一行数据')
            return

        row = selected[0].row()
        med = self._get_med_at_table_row(row)
        if not med:
            QMessageBox.warning(self, '提示', '无法定位药材数据')
            return
        med_id = med['id']
        med_name = med['name']

        reply = QMessageBox.question(self, '确认', f'确定要删除药材 "{med_name}" 吗？\n此操作将同时删除库存记录！',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self._medicine_service.delete(med_id)
                # 缓存由 Service 层 _sync_cache_delete 自动同步
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
        medicine_data = self._get_med_at_table_row(row)
        if not medicine_data:
            QMessageBox.warning(self, '提示', '无法定位药材数据')
            return

        def e(key, fallback=''):
            return html.escape(str(medicine_data.get(key) or fallback))

        detail_text = f'''
        <div style="font-family: 'Segoe UI', Arial, sans-serif; color: {AppColors.TEXT_PRIMARY};">
            <h2 style="margin: 0 0 16px 0; font-weight: 700; color: {AppColors.TEXT_HEADING};">{e('name')}</h2>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                <div style="padding: 12px; background: {AppColors.BG_PAGE}; border-radius: 6px;">
                    <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">分类</div>
                    <div style="font-weight: 500;">{e('category', '未分类')}</div>
                </div>
                <div style="padding: 12px; background: {AppColors.BG_PAGE}; border-radius: 6px;">
                    <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">药性</div>
                    <div style="font-weight: 500;">{e('nature', '未知')}</div>
                </div>
                <div style="padding: 12px; background: {AppColors.BG_PAGE}; border-radius: 6px;">
                    <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">药味</div>
                    <div style="font-weight: 500;">{e('taste', '未知')}</div>
                </div>
                <div style="padding: 12px; background: {AppColors.BG_PAGE}; border-radius: 6px;">
                    <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">归经</div>
                    <div style="font-weight: 500;">{e('meridian', '未知')}</div>
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">功效</div>
                <div style="padding: 12px; background: {AppColors.SUCCESS_BG}; border-radius: 6px; border-left: 3px solid {AppColors.SUCCESS};">{e('efficacy', '暂无')}</div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">主治</div>
                <div style="padding: 12px; background: {AppColors.ACCENT_LIGHT}; border-radius: 6px; border-left: 3px solid {AppColors.ACCENT};">{e('indications', '暂无')}</div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">用法用量</div>
                <div style="padding: 12px; background: {AppColors.WARNING_BG}; border-radius: 6px; border-left: 3px solid {AppColors.WARNING};">{e('usage', '暂无')} | {e('dosage', '暂无')}</div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">禁忌</div>
                <div style="padding: 12px; background: {AppColors.DANGER_BG}; border-radius: 6px; border-left: 3px solid {AppColors.DANGER};">{e('contraindication', '暂无')}</div>
            </div>

            <div>
                <div style="font-size: 11px; color: {AppColors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">备注</div>
                <div style="padding: 12px; background: {AppColors.BG_PAGE}; border-radius: 6px;">{e('notes', '无')}</div>
            </div>
        </div>
        '''

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('药材详情')
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(detail_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setMinimumWidth(560)
        msg_box.exec()

    def export_data(self):
        try:
            import csv

            from PySide6.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(self, '导出药材数据', '', 'CSV文件 (*.csv)')
            if filename:
                rows = self._cache.get_all()
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '名称', '别名', '分类', '药性', '药味', '归经',
                                    '功效', '主治', '用法', '用量', '禁忌', '备注'])
                    for row in rows:
                        writer.writerow([
                            row['id'], row['name'], row['alias'], row['category'],
                            row['nature'], row['taste'], row['meridian'],
                            row['efficacy'], row['indications'], row['usage'],
                            row['dosage'], row['contraindication'], row['notes']
                        ])
                QMessageBox.information(self, '成功', '数据导出成功！')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'导出失败: {str(e)}')

    def _apply_responsive_table(self):
        if hasattr(self, 'table'):
            self.apply_responsive_table(self.table, self._base_column_widths,
                                        getattr(self, 'stats_label', None))

    def update_fonts(self):
        self._apply_responsive_table()
        self.load_data()
