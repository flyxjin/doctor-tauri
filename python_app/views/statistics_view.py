# -*- coding: utf-8 -*-
"""
销售统计报表视图
提供营收汇总、热销药材排行、营收趋势等数据分析功能。
"""
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core import StatisticsService
from core.theme import AppColors
from views.base_view import BaseDataView


class _StatCard(QFrame):
    """汇总卡片控件"""

    def __init__(self, title: str, value: str, color: str = AppColors.ACCENT, parent=None):
        super().__init__(parent)
        self.setObjectName('stat_card')
        self.setStyleSheet(f'''
            QFrame#stat_card {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: {AppColors.RADIUS_LG};
                padding: 16px;
            }}
        ''')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f'color: {AppColors.TEXT_MUTED}; font-size: 13px;')
        self.title_label.setMinimumHeight(18)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f'color: {color}; font-size: 24px; font-weight: 700;'
        )
        self.value_label.setMinimumHeight(32)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        self.value_label.setText(value)


class StatisticsView(BaseDataView):
    """销售统计报表视图"""

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self._stats_service = StatisticsService(db)
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 顶部工具栏：时间范围选择 + 刷新按钮
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        range_label = QLabel('时间范围:')
        range_label.setStyleSheet(f'color: {AppColors.TEXT_SECONDARY}; font-size: 14px;')

        self.range_combo = QComboBox()
        self.range_combo.addItems(['今日', '本周', '本月', '本年', '全部'])
        self.range_combo.setCurrentIndex(2)
        self.range_combo.setStyleSheet(f'''
            QComboBox {{
                padding: 6px 12px;
                border: 1px solid {AppColors.BORDER};
                border-radius: {AppColors.RADIUS_MD};
                background-color: {AppColors.BG_CARD};
                min-width: 100px;
            }}
        ''')
        self.range_combo.currentIndexChanged.connect(self.refresh_data)

        refresh_btn = self.create_button('刷新', role='secondary', padding='8px 16px')
        refresh_btn.clicked.connect(self.refresh_data)

        toolbar.addWidget(range_label)
        toolbar.addWidget(self.range_combo)
        toolbar.addStretch()
        toolbar.addWidget(refresh_btn)
        main_layout.addLayout(toolbar)

        # 汇总卡片区域
        self.card_today_pres = _StatCard('处方数', '0', AppColors.ACCENT)
        self.card_today_revenue = _StatCard('总营收', '¥0.00', AppColors.SUCCESS)
        self.card_med_count = _StatCard('药材种类', '0', AppColors.INFO)
        self.card_low_stock = _StatCard('低库存预警', '0', AppColors.WARNING)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        cards_layout.addWidget(self.card_today_pres)
        cards_layout.addWidget(self.card_today_revenue)
        cards_layout.addWidget(self.card_med_count)
        cards_layout.addWidget(self.card_low_stock)
        main_layout.addLayout(cards_layout)

        # 下方：热销药材 + 营收趋势
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        # 热销药材 TOP 10
        top_meds_frame = QFrame()
        top_meds_layout = QVBoxLayout(top_meds_frame)
        top_meds_layout.setContentsMargins(0, 0, 0, 0)
        top_meds_layout.setSpacing(10)

        top_meds_title = QLabel('热销药材 TOP 10')
        top_meds_title.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 16px; font-weight: 600;'
        )
        self.top_meds_table = QTableWidget()
        self.top_meds_table.setColumnCount(4)
        self.top_meds_table.setHorizontalHeaderLabels(['排名', '药材', '出现次数', '总用量(g)'])
        self.top_meds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_meds_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_meds_table.verticalHeader().setVisible(False)
        self.top_meds_table.verticalHeader().setDefaultSectionSize(40)

        top_meds_layout.addWidget(top_meds_title)
        top_meds_layout.addWidget(self.top_meds_table)

        # 营收趋势
        trend_frame = QFrame()
        trend_layout = QVBoxLayout(trend_frame)
        trend_layout.setContentsMargins(0, 0, 0, 0)
        trend_layout.setSpacing(10)

        trend_title = QLabel('营收趋势')
        trend_title.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 16px; font-weight: 600;'
        )
        self.trend_table = QTableWidget()
        self.trend_table.setColumnCount(3)
        self.trend_table.setHorizontalHeaderLabels(['日期', '处方数', '营收'])
        self.trend_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trend_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trend_table.verticalHeader().setVisible(False)
        self.trend_table.verticalHeader().setDefaultSectionSize(40)

        trend_layout.addWidget(trend_title)
        trend_layout.addWidget(self.trend_table)

        bottom_layout.addWidget(top_meds_frame, 1)
        bottom_layout.addWidget(trend_frame, 1)
        main_layout.addLayout(bottom_layout, 1)

    def _apply_responsive_table(self):
        for table in [self.top_meds_table, self.trend_table]:
            self.apply_responsive_table(table)

    def _get_date_range(self):
        """根据选择获取日期范围 (start, end)"""
        now = datetime.now()
        idx = self.range_combo.currentIndex()

        if idx == 0:  # 今日
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif idx == 1:  # 本周
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif idx == 2:  # 本月
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif idx == 3:  # 本年
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:  # 全部
            start = datetime(2000, 1, 1)
            end = now

        return start, end

    def refresh_data(self):
        """刷新统计数据（通过 StatisticsService 访问数据，遵循分层架构）"""
        try:
            start, end = self._get_date_range()
            start_str = start.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end.strftime('%Y-%m-%d %H:%M:%S')

            # 汇总：处方数和营收
            summary = self._stats_service.get_summary(start_str, end_str)
            pres_count = summary['cnt'] or 0
            revenue = summary['revenue'] or 0

            self.card_today_pres.set_value(str(pres_count))
            self.card_today_revenue.set_value(f'¥{revenue:.2f}')

            # 药材种类数
            self.card_med_count.set_value(str(self._stats_service.get_medicine_count()))

            # 低库存预警数
            self.card_low_stock.set_value(str(self._stats_service.get_low_stock_count()))

            # 热销药材 TOP 10
            top_meds = self._stats_service.get_top_medicines(start_str, end_str, limit=10)
            self._populate_top_meds(top_meds)

            # 营收趋势（按天分组，最多 30 天）
            trend = self._stats_service.get_revenue_trend(start_str, end_str, limit=30)
            self._populate_trend(trend)

        except Exception as e:
            import logging
            logging.getLogger('MedicineSystem').error(f"刷新统计数据失败: {e}")

    def _populate_top_meds(self, data):
        self.top_meds_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.top_meds_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.top_meds_table.setItem(i, 1, QTableWidgetItem(str(row.get('name', ''))))
            self.top_meds_table.setItem(i, 2, QTableWidgetItem(str(row.get('freq', 0))))
            self.top_meds_table.setItem(i, 3, QTableWidgetItem(f"{row.get('total_qty', 0):.1f}"))

    def _populate_trend(self, data):
        self.trend_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.trend_table.setItem(i, 0, QTableWidgetItem(str(row.get('date', ''))))
            self.trend_table.setItem(i, 1, QTableWidgetItem(str(row.get('cnt', 0))))
            self.trend_table.setItem(i, 2, QTableWidgetItem(f"¥{row.get('revenue', 0):.2f}"))

    def update_fonts(self):
        self._apply_responsive_table()
