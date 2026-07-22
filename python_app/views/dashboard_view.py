# -*- coding: utf-8 -*-
"""
仪表盘首页视图
应用启动后默认显示的概览页面，包含关键指标卡片、低库存预警、最近处方和营收简报。
"""
from datetime import datetime, timedelta

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core import DashboardService
from core.theme import AppColors
from views.base_view import BaseDataView


class _MetricCard(QFrame):
    """关键指标卡片"""

    def __init__(self, title: str, value: str, subtitle: str = '',
                 color: str = AppColors.ACCENT, parent=None):
        super().__init__(parent)
        self.setObjectName('metric_card')
        self.setStyleSheet(f'''
            QFrame#metric_card {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: {AppColors.RADIUS_LG};
                padding: 18px;
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
            f'color: {color}; font-size: 28px; font-weight: 700;'
        )
        self.value_label.setMinimumHeight(36)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f'color: {AppColors.TEXT_MUTED}; font-size: 12px;')
        self.subtitle_label.setMinimumHeight(16)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)

    def set_value(self, value: str, subtitle: str = ''):
        self.value_label.setText(value)
        if subtitle:
            self.subtitle_label.setText(subtitle)


class _RevenueBar(QFrame):
    """营收条形图（用 QProgressBar 模拟）。

    支持通过 update_data 复用实例，避免每次刷新都重建 7 个 widget 造成内存抖动。
    """

    def __init__(self, date: str = '', revenue: float = 0, max_revenue: float = 1, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.date_label = QLabel(date)
        self.date_label.setFixedWidth(80)
        self.date_label.setStyleSheet(f'color: {AppColors.TEXT_SECONDARY}; font-size: 12px;')

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(16)
        self.bar.setStyleSheet(f'''
            QProgressBar {{
                background-color: {AppColors.BG_SECONDARY};
                border: none;
                border-radius: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {AppColors.ACCENT};
                border-radius: 8px;
            }}
        ''')

        self.amount_label = QLabel(f'¥{revenue:.0f}')
        self.amount_label.setFixedWidth(70)
        self.amount_label.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 12px; font-weight: 600;'
        )

        layout.addWidget(self.date_label)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.amount_label)

        # 初始填充一次数据
        self.update_data(date, revenue, max_revenue)

    def update_data(self, date: str, revenue: float, max_revenue: float) -> None:
        """复用实例，仅更新显示数据，避免 widget 重建"""
        self.date_label.setText(date)
        pct = int((revenue / max_revenue * 100)) if max_revenue > 0 else 0
        self.bar.setValue(min(pct, 100))
        self.amount_label.setText(f'¥{revenue:.0f}')


class DashboardView(BaseDataView):
    """仪表盘首页视图"""

    def __init__(self, db, parent=None):
        super().__init__(db, parent)
        self._dashboard_service = DashboardService(db)
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 欢迎语
        welcome = QLabel(self._get_welcome_text())
        welcome.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 20px; font-weight: 700;'
        )
        main_layout.addWidget(welcome)

        # 关键指标卡片
        self.card_revenue = _MetricCard('今日营收', '¥0.00', '', AppColors.SUCCESS)
        self.card_prescriptions = _MetricCard('今日处方', '0', '张', AppColors.ACCENT)
        self.card_medicines = _MetricCard('药材总数', '0', '味', AppColors.INFO)
        self.card_low_stock = _MetricCard('低库存预警', '0', '种', AppColors.WARNING)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        cards_layout.addWidget(self.card_revenue)
        cards_layout.addWidget(self.card_prescriptions)
        cards_layout.addWidget(self.card_medicines)
        cards_layout.addWidget(self.card_low_stock)
        main_layout.addLayout(cards_layout)

        # 下方：低库存预警 + 最近处方
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        # 低库存预警
        alert_frame = QFrame()
        alert_layout = QVBoxLayout(alert_frame)
        alert_layout.setContentsMargins(0, 0, 0, 0)
        alert_layout.setSpacing(10)

        alert_title = QLabel('低库存预警')
        alert_title.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 16px; font-weight: 600;'
        )
        self.alert_table = QTableWidget()
        self.alert_table.setColumnCount(3)
        self.alert_table.setHorizontalHeaderLabels(['药材', '当前库存', '最低库存'])
        self.alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alert_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alert_table.verticalHeader().setVisible(False)
        self.alert_table.verticalHeader().setDefaultSectionSize(38)

        alert_layout.addWidget(alert_title)
        alert_layout.addWidget(self.alert_table)

        # 最近处方
        recent_frame = QFrame()
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(10)

        recent_title = QLabel('最近处方')
        recent_title.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 16px; font-weight: 600;'
        )
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(['编号', '患者', '金额', '日期'])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.verticalHeader().setDefaultSectionSize(38)

        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(self.recent_table)

        bottom_layout.addWidget(alert_frame, 1)
        bottom_layout.addWidget(recent_frame, 1)
        main_layout.addLayout(bottom_layout, 1)

        # 营收简报（近 7 天）
        revenue_frame = QFrame()
        revenue_layout = QVBoxLayout(revenue_frame)
        revenue_layout.setContentsMargins(0, 0, 0, 0)
        revenue_layout.setSpacing(10)

        revenue_title = QLabel('近 7 天营收趋势')
        revenue_title.setStyleSheet(
            f'color: {AppColors.TEXT_HEADING}; font-size: 16px; font-weight: 600;'
        )
        self.revenue_bars_container = QVBoxLayout()
        self.revenue_bars_container.setSpacing(6)

        # 预创建 7 个 _RevenueBar 实例复用，避免每次刷新重建 widget 造成内存抖动
        self._revenue_bars: list = []
        for _ in range(7):
            bar = _RevenueBar()
            self._revenue_bars.append(bar)
            self.revenue_bars_container.addWidget(bar)

        revenue_layout.addWidget(revenue_title)
        revenue_layout.addLayout(self.revenue_bars_container)

        main_layout.addWidget(revenue_frame)

    def _apply_responsive_table(self):
        for table in [self.alert_table, self.recent_table]:
            self.apply_responsive_table(table)

    def _get_welcome_text(self) -> str:
        """根据时间返回欢迎语"""
        hour = datetime.now().hour
        if hour < 6:
            return '凌晨好'
        elif hour < 12:
            return '上午好'
        elif hour < 14:
            return '中午好'
        elif hour < 18:
            return '下午好'
        else:
            return '晚上好'

    def refresh_data(self):
        """刷新仪表盘数据（通过 DashboardService 访问数据，遵循分层架构）"""
        try:
            # 今日营收和处方数
            today_data = self._dashboard_service.get_today_summary()
            self.card_revenue.set_value(f"¥{today_data['revenue'] or 0:.2f}")
            self.card_prescriptions.set_value(str(today_data['cnt'] or 0), '张')

            # 药材总数
            med_count = self._dashboard_service.get_medicine_count()
            self.card_medicines.set_value(str(med_count), '味')

            # 低库存预警
            low_rows = self._dashboard_service.get_low_stock_alerts(limit=10)
            self.card_low_stock.set_value(str(len(low_rows)), '种')
            self._populate_alerts(low_rows)

            # 最近处方
            recent = self._dashboard_service.get_recent_prescriptions(limit=5)
            self._populate_recent(recent)

            # 近 7 天营收趋势
            self._refresh_revenue_trend()

        except Exception as e:
            import logging
            logging.getLogger('MedicineSystem').error(f"刷新仪表盘失败: {e}")

    def _populate_alerts(self, rows):
        self.alert_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            name = str(row.get('name', ''))
            qty = row.get('quantity', 0)
            min_stock = row.get('min_stock', 0)

            name_item = QTableWidgetItem(name)
            qty_item = QTableWidgetItem(f"{qty}")
            min_item = QTableWidgetItem(f"{min_stock}")

            # 库存为 0 标朱砂红，低库存标古铜黄
            if qty <= 0:
                qty_item.setForeground(QColor(AppColors.DANGER))
            elif qty <= min_stock:
                qty_item.setForeground(QColor(AppColors.WARNING))

            self.alert_table.setItem(i, 0, name_item)
            self.alert_table.setItem(i, 1, qty_item)
            self.alert_table.setItem(i, 2, min_item)

    def _populate_recent(self, rows):
        self.recent_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.recent_table.setItem(i, 0, QTableWidgetItem(str(row.get('id', ''))))
            self.recent_table.setItem(i, 1, QTableWidgetItem(str(row.get('patient_name', '') or '未填写')))
            self.recent_table.setItem(i, 2, QTableWidgetItem(f"¥{(row.get('total_amount') or 0):.2f}"))
            created = str(row.get('created_at', ''))
            # 只显示日期部分
            if ' ' in created:
                created = created.split(' ')[0]
            self.recent_table.setItem(i, 3, QTableWidgetItem(created))

    def _refresh_revenue_trend(self):
        """刷新近 7 天营收趋势条形图（复用 widget 实例，仅更新数据）"""
        now = datetime.now()
        seven_days_ago = now - timedelta(days=6)

        rows = self._dashboard_service.get_revenue_trend_7_days()

        # 构建日期到营收的映射
        revenue_map = {row['date']: row['revenue'] for row in rows}
        max_revenue = max(revenue_map.values()) if revenue_map else 0
        scale = max_revenue if max_revenue > 0 else 1

        # 复用预创建的 7 个 _RevenueBar，仅更新数据
        for i, bar in enumerate(self._revenue_bars):
            date = (seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d')
            revenue = revenue_map.get(date, 0)
            bar.update_data(date, revenue, scale)

    def update_fonts(self):
        self._apply_responsive_table()
