# -*- coding: utf-8 -*-
"""
基础视图模块 - 提取各 View 的公共逻辑
"""
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QTimer
from typing import Optional, Callable
from utils.responsive_font import ResponsiveWidget, get_font_manager
from core.theme import get_table_style


class BaseDataView(QWidget, ResponsiveWidget):
    """带响应式表格的基础数据视图"""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.font_manager = get_font_manager()

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
        return table

    def apply_responsive_table(self, table: QTableWidget):
        base_size = self.font_manager.current_base_size
        header_size = int(base_size * 1.1)
        padding = max(4, int(base_size * 0.5))
        table.setStyleSheet(get_table_style(base_size, header_size, padding))

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
