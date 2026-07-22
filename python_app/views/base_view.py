# -*- coding: utf-8 -*-
"""
基础视图模块 - 提取各 View 的公共逻辑
"""
from typing import Callable, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QPushButton, QTableWidget, QWidget

from core.theme import AppColors, get_button_style, get_secondary_button_style, get_table_style
from utils.responsive_font import ResponsiveWidget, get_font_manager

_BUTTON_ROLE_MAP = {
    'primary': (AppColors.PRIMARY, 'white'),
    'success': (AppColors.SUCCESS, 'white'),
    'warning': (AppColors.WARNING, 'white'),
    'danger': (AppColors.DANGER, 'white'),
    'info': (AppColors.INFO, 'white'),
    'secondary': None,
}


class BaseDataView(QWidget, ResponsiveWidget):
    """带响应式表格的基础数据视图"""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        # 显式初始化 ResponsiveWidget，建立 font_changed/size_changed 信号连接
        ResponsiveWidget.__init__(self)
        self.db = db
        self.font_manager = get_font_manager()

    def create_button(self, text: str, role: str = 'primary',
                      padding: str = '10px 20px') -> QPushButton:
        btn = QPushButton(text)
        if role == 'secondary':
            btn.setStyleSheet(get_secondary_button_style(padding=padding))
        else:
            bg, fg = _BUTTON_ROLE_MAP.get(role, (AppColors.PRIMARY, 'white'))
            btn.setStyleSheet(get_button_style(bg_color=bg, text_color=fg, padding=padding))
        return btn

    def apply_responsive_label(self, label, font_type: str = 'body',
                               color: str = None, bold: bool = False):
        font = self.font_manager.get_font(font_type)
        if bold:
            font.setBold(True)
        label.setFont(font)
        if color:
            label.setStyleSheet(f'color: {color};')

    def create_table(self, columns: int, headers: list, stretch: bool = True) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(columns)
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        if stretch:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.apply_responsive_table(table)
        return table

    def apply_responsive_table(self, table: QTableWidget,
                               base_column_widths: list = None,
                               stats_label: QLabel = None):
        config = self.font_manager.get_table_config()
        scale = config['scale']

        table.verticalHeader().setDefaultSectionSize(config['row_height'])
        table.verticalHeader().setMinimumSectionSize(config['row_height'])

        header = table.horizontalHeader()
        header.setMinimumSectionSize(config['cell_padding'] * 2)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        if base_column_widths:
            for col in range(len(base_column_widths)):
                if col == 0:
                    continue
                base_width = base_column_widths[col]
                scaled_width = int(base_width * scale)
                table.setColumnWidth(col, scaled_width)

        font = self.font_manager.get_font('table_cell')
        table.setFont(font)

        header_font = self.font_manager.get_font('table_header')
        header.setFont(header_font)

        table.setStyleSheet(get_table_style(config['font_size'], config['header_font_size'], config['cell_padding']))

        if stats_label:
            stats_label.setStyleSheet(f'color: {AppColors.TEXT_SECONDARY}; font-size: {self.font_manager.get_font_size("small")}px;')

    def get_selected_row(self, table: QTableWidget) -> Optional[int]:
        selected = table.selectedItems()
        if not selected:
            return None
        return selected[0].row()

    def setup_search_debounce(self, search_input, callback: Callable, delay: int = 200):
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(delay)
        timer.timeout.connect(lambda: callback(search_input.text()))
        search_input.textChanged.connect(timer.start)
        return timer

    def update_fonts(self):
        pass
