# -*- coding: utf-8 -*-
"""
数据统计仪表盘视图 - Windows 7兼容版本
提供销售统计、库存预警、热门药材排行等功能
Microsoft Fluent Design System风格
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QGridLayout, QFrame, QProgressBar,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QPushButton, QScrollArea, QSizePolicy,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPalette, QBrush
from datetime import datetime, timedelta
import logging

from utils.style import UIStyles

logger = logging.getLogger('MedicineSystem')


class StatCard(QFrame):
    """统计卡片组件"""
    
    def __init__(self, title: str, value: str, subtitle: str = '', color: str = None, icon: str = '', accent: str = None):
        super().__init__()
        self.setObjectName('stat_card')
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._title = title
        self._value_label = None
        self._sub_label = None
        self._accent = accent
        self._init_ui(title, value, subtitle, color, icon)
        self._apply_style()
    
    def _apply_style(self):
        c = UIStyles.COLORS
        
        styles = {
            'warning': f'background-color: {c["warning"]}15; border: 1px solid {c["warning"]};',
            'success': f'background-color: {c["success"]}15; border: 1px solid {c["success"]};',
            'error': f'background-color: {c["error"]}15; border: 1px solid {c["error"]};',
            'info': f'background-color: {c["primary"]}10; border: 1px solid {c["primary"]};',
        }
        
        style = styles.get(self._accent, 'background-color: #ffffff; border: 1px solid #e2e8f0;')
        
        self.setStyleSheet(f'''
            QFrame#stat_card {{
                {style}
                border-radius: 8px;
            }}
        ''')
    
    def _init_ui(self, title: str, value: str, subtitle: str, color: str, icon: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet('color: rgba(0,0,0,0.65); font-size: 14px; border: none; background: transparent;')
        title_label.setWordWrap(False)
        
        value_layout = QHBoxLayout()
        value_layout.setSpacing(8)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet('font-size: 24px; border: none; background: transparent;')
            value_layout.addWidget(icon_label)
        
        display_color = color if color else UIStyles.COLORS['primary']
        self._value_label = QLabel(value)
        self._value_label.setStyleSheet(f'color: {display_color}; font-size: 24px; font-weight: bold; border: none; background: transparent;')
        self._value_label.setWordWrap(False)
        value_layout.addWidget(self._value_label)
        value_layout.addStretch()
        
        layout.addWidget(title_label)
        layout.addLayout(value_layout)
        
        if subtitle:
            self._sub_label = QLabel(subtitle)
            self._sub_label.setStyleSheet('color: rgba(0,0,0,0.45); font-size: 12px; border: none; background: transparent;')
            self._sub_label.setWordWrap(False)
            layout.addWidget(self._sub_label)
    
    def update_value(self, value: str, subtitle: str = ''):
        if self._value_label:
            self._value_label.setText(value)
        if self._sub_label and subtitle:
            self._sub_label.setText(subtitle)
    
    def update_color(self, color: str):
        if self._value_label:
            self._value_label.setStyleSheet(f'color: {color}; font-size: 24px; font-weight: bold; border: none; background: transparent;')
    
    def update_accent(self, accent: str):
        self._accent = accent
        self._apply_style()


class DashboardView(QWidget):
    """数据统计仪表盘主视图 - 现代设计风格"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._refresh_timer = None
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(12, 12, 12, 12)
        
        header_layout = QHBoxLayout()
        title_label = QLabel('数据统计仪表盘')
        title_label.setStyleSheet('font-size: 18px; font-weight: 600; color: rgba(0,0,0,0.88);')
        
        self.time_filter = QComboBox()
        self.time_filter.addItems(['今日', '本周', '本月', '全部'])
        self.time_filter.currentIndexChanged.connect(self._on_time_filter_changed)
        self.time_filter.setMinimumWidth(100)
        
        refresh_btn = QPushButton('刷新数据')
        refresh_btn.clicked.connect(self.load_statistics)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel('时间范围:'))
        header_layout.addWidget(self.time_filter)
        header_layout.addSpacing(12)
        header_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(header_layout)
        self._create_overview_section(content_layout)
        
        content_split = QHBoxLayout()
        content_split.setSpacing(12)
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)
        self._create_sales_section(left_panel)
        self._create_ranking_section(left_panel)
        
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)
        self._create_inventory_section(right_panel)
        
        content_split.addLayout(left_panel, 55)
        content_split.addLayout(right_panel, 45)
        content_layout.addLayout(content_split, 1)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def _create_overview_section(self, parent_layout):
        overview_group = QGroupBox('数据概览')
        overview_layout = QGridLayout(overview_group)
        overview_layout.setSpacing(12)
        overview_layout.setContentsMargins(12, 20, 12, 12)
        
        self.total_medicines_card = StatCard('药材总数', '0', '种药材在库', None, '', 'info')
        self.total_prescriptions_card = StatCard('处方总数', '0', '累计开具', None, '', 'info')
        self.total_sales_card = StatCard('销售总额', '¥0.00', '累计销售额', None, '', 'success')
        self.low_stock_card = StatCard('库存预警', '0', '种药材库存不足', UIStyles.COLORS['error'], '', 'warning')
        
        overview_layout.addWidget(self.total_medicines_card, 0, 0)
        overview_layout.addWidget(self.total_prescriptions_card, 0, 1)
        overview_layout.addWidget(self.total_sales_card, 0, 2)
        overview_layout.addWidget(self.low_stock_card, 0, 3)
        
        for i in range(4):
            overview_layout.setColumnStretch(i, 1)
        
        parent_layout.addWidget(overview_group)
    
    def _create_sales_section(self, parent_layout):
        sales_group = QGroupBox('销售趋势')
        sales_layout = QVBoxLayout(sales_group)
        sales_layout.setContentsMargins(8, 12, 8, 8)
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(['日期', '处方数', '销售金额', '药材种类'])
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setMinimumHeight(150)
        
        sales_layout.addWidget(self.sales_table)
        parent_layout.addWidget(sales_group)
    
    def _create_inventory_section(self, parent_layout):
        inventory_group = QGroupBox('库存预警列表')
        inventory_layout = QVBoxLayout(inventory_group)
        inventory_layout.setContentsMargins(8, 12, 8, 8)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(['药材名称', '当前库存', '最低库存', '状态', '建议'])
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.setAlternatingRowColors(True)
        
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.inventory_table.setColumnWidth(1, 80)
        self.inventory_table.setColumnWidth(2, 80)
        self.inventory_table.setColumnWidth(3, 80)
        self.inventory_table.setColumnWidth(4, 80)
        
        inventory_layout.addWidget(self.inventory_table)
        parent_layout.addWidget(inventory_group)
    
    def _create_ranking_section(self, parent_layout):
        ranking_group = QGroupBox('热门药材排行 TOP 10')
        ranking_layout = QVBoxLayout(ranking_group)
        ranking_layout.setContentsMargins(8, 12, 8, 8)
        
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(4)
        self.ranking_table.setHorizontalHeaderLabels(['排名', '药材名称', '使用次数', '销售金额'])
        self.ranking_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ranking_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ranking_table.verticalHeader().setVisible(False)
        self.ranking_table.setAlternatingRowColors(True)
        
        header = self.ranking_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.ranking_table.setColumnWidth(0, 50)
        self.ranking_table.setColumnWidth(2, 100)
        self.ranking_table.setColumnWidth(3, 100)
        
        ranking_layout.addWidget(self.ranking_table)
        parent_layout.addWidget(ranking_group)
    
    def _get_time_range(self) -> tuple:
        time_filter = self.time_filter.currentText()
        now = datetime.now()
        
        if time_filter == '今日':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_filter == '本周':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_filter == '本月':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            start = None
            end = None
        
        return start, end
    
    def _on_time_filter_changed(self):
        self.load_statistics()
    
    def load_statistics(self):
        try:
            self._load_overview_data()
            self._load_sales_data()
            self._load_inventory_warning()
            self._load_ranking_data()
        except Exception as e:
            logger.error(f"加载统计数据失败: {e}")
    
    def _load_overview_data(self):
        medicines_count = self.db.fetchone("SELECT COUNT(*) as count FROM medicines")
        total_medicines = medicines_count['count'] if medicines_count else 0
        
        prescriptions_count = self.db.fetchone("SELECT COUNT(*) as count FROM prescriptions")
        total_prescriptions = prescriptions_count['count'] if prescriptions_count else 0
        
        sales_sum = self.db.fetchone("SELECT COALESCE(SUM(total_amount), 0) as total FROM prescriptions")
        total_sales = sales_sum['total'] if sales_sum else 0
        
        low_stock = self.db.fetchall(
            "SELECT COUNT(*) as count FROM inventory WHERE quantity <= min_stock"
        )
        low_stock_count = low_stock[0]['count'] if low_stock else 0
        
        self.total_medicines_card.update_value(str(total_medicines), '种药材在库')
        self.total_prescriptions_card.update_value(str(total_prescriptions), '累计开具')
        self.total_sales_card.update_value(f'¥{total_sales:.2f}', '累计销售额')
        self.low_stock_card.update_value(str(low_stock_count), '种药材库存不足')
        
        if low_stock_count > 0:
            self.low_stock_card.update_accent('warning')
            self.low_stock_card.update_color(UIStyles.COLORS['error'])
        else:
            self.low_stock_card.update_accent('success')
            self.low_stock_card.update_color(UIStyles.COLORS['success'])
    
    def _load_sales_data(self):
        start, end = self._get_time_range()
        
        if start and end:
            rows = self.db.fetchall('''
                SELECT DATE(created_at) as date, 
                       COUNT(*) as prescription_count,
                       SUM(total_amount) as total_amount,
                       (SELECT COUNT(DISTINCT medicine_id) FROM prescription_items pi 
                        JOIN prescriptions p2 ON pi.prescription_id = p2.id 
                        WHERE DATE(p2.created_at) = DATE(p.created_at)) as medicine_types
                FROM prescriptions p
                WHERE created_at BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            ''', (start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S')))
        else:
            rows = self.db.fetchall('''
                SELECT DATE(created_at) as date, 
                       COUNT(*) as prescription_count,
                       SUM(total_amount) as total_amount,
                       (SELECT COUNT(DISTINCT medicine_id) FROM prescription_items pi 
                        WHERE DATE(pi.prescription_id) = DATE(p.created_at)) as medicine_types
                FROM prescriptions p
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            ''')
        
        self.sales_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            date = row.get('date', '')
            pres_count = row.get('prescription_count', 0)
            total = row.get('total_amount', 0) or 0
            med_types = row.get('medicine_types', 0) or 0
            
            self.sales_table.setItem(i, 0, QTableWidgetItem(str(date) if date else '-'))
            self.sales_table.setItem(i, 1, QTableWidgetItem(str(pres_count)))
            self.sales_table.setItem(i, 2, QTableWidgetItem(f'¥{total:.2f}'))
            self.sales_table.setItem(i, 3, QTableWidgetItem(str(med_types)))
    
    def _load_inventory_warning(self):
        rows = self.db.fetchall('''
            SELECT m.name, i.quantity, i.min_stock, i.unit
            FROM inventory i
            JOIN medicines m ON i.medicine_id = m.id
            WHERE i.quantity <= i.min_stock
            ORDER BY i.quantity ASC
            LIMIT 10
        ''')
        
        self.inventory_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            name = row.get('name', '')
            quantity = row.get('quantity', 0)
            min_stock = row.get('min_stock', 0)
            unit = row.get('unit', 'g')
            
            self.inventory_table.setItem(i, 0, QTableWidgetItem(name))
            self.inventory_table.setItem(i, 1, QTableWidgetItem(f'{quantity}{unit}'))
            self.inventory_table.setItem(i, 2, QTableWidgetItem(f'{min_stock}{unit}'))
            
            if quantity <= 0:
                status = '缺货'
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#ff4d4f'))
            elif quantity <= min_stock * 0.5:
                status = '严重不足'
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#fa8c16'))
            else:
                status = '库存不足'
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#faad14'))
            
            self.inventory_table.setItem(i, 3, status_item)
            self.inventory_table.setItem(i, 4, QTableWidgetItem('采购'))
    
    def _load_ranking_data(self):
        start, end = self._get_time_range()
        
        if start and end:
            rows = self.db.fetchall('''
                SELECT pi.medicine_name, 
                       SUM(pi.quantity) as total_quantity,
                       SUM(pi.amount) as total_amount
                FROM prescription_items pi
                JOIN prescriptions p ON pi.prescription_id = p.id
                WHERE p.created_at BETWEEN ? AND ?
                GROUP BY pi.medicine_name
                ORDER BY total_quantity DESC
                LIMIT 10
            ''', (start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S')))
        else:
            rows = self.db.fetchall('''
                SELECT medicine_name, 
                       SUM(quantity) as total_quantity,
                       SUM(amount) as total_amount
                FROM prescription_items
                GROUP BY medicine_name
                ORDER BY total_quantity DESC
                LIMIT 10
            ''')
        
        self.ranking_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            name = row.get('medicine_name', '')
            quantity = row.get('total_quantity', 0) or 0
            amount = row.get('total_amount', 0) or 0
            
            rank_item = QTableWidgetItem(str(i + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            
            if i < 3:
                rank_item.setForeground(QColor('#fa8c16'))
                rank_item.setFont(QFont('', -1, QFont.Bold))
            
            self.ranking_table.setItem(i, 0, rank_item)
            self.ranking_table.setItem(i, 1, QTableWidgetItem(name))
            self.ranking_table.setItem(i, 2, QTableWidgetItem(f'{quantity}g'))
            self.ranking_table.setItem(i, 3, QTableWidgetItem(f'¥{amount:.2f}'))
    
    def refresh_data(self):
        self.load_statistics()
