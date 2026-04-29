# -*- coding: utf-8 -*-
"""
主题模块 - 集中管理样式常量和工具函数
"""


class AppColors:
    PRIMARY = '#1890ff'
    PRIMARY_HOVER = '#40a9ff'
    PRIMARY_ACTIVE = '#096dd9'

    SUCCESS = '#67c23a'
    SUCCESS_HOVER = '#85ce61'
    WARNING = '#e6a23c'
    DANGER = '#f56c6c'
    DANGER_HOVER = '#f78989'
    INFO = '#909399'

    TEXT_PRIMARY = '#303133'
    TEXT_REGULAR = '#606266'
    TEXT_SECONDARY = '#909399'
    TEXT_PLACEHOLDER = '#c0c4cc'

    BG_PAGE = '#f0f2f5'
    BG_CARD = '#ffffff'
    BG_SIDEBAR = '#001529'
    BG_HEADER = '#fafafa'
    BG_ROW_HOVER = '#f5f7fa'
    BG_ROW_SELECTED = '#e6f7ff'

    BORDER = '#dcdfe6'
    BORDER_LIGHT = '#e4e7ed'
    BORDER_LIGHTER = '#ebeef5'

    STOCK_ZERO = '#f56c6c'
    STOCK_LOW = '#e6a23c'


def get_button_style(bg_color=AppColors.PRIMARY, text_color='white', padding='10px 20px'):
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            padding: {padding};
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {bg_color}dd;
        }}
        QPushButton:pressed {{
            background-color: {bg_color}bb;
        }}
        QPushButton:disabled {{
            background-color: #d9d9d9;
            color: #8c8c8c;
        }}
    """


def get_table_style(font_size=14, header_font_size=15, padding=8):
    return f"""
        QTableWidget {{
            font-size: {font_size}px;
            gridline-color: {AppColors.BORDER_LIGHTER};
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
        }}
        QTableWidget::item {{
            padding: {padding}px;
            border-bottom: 1px solid {AppColors.BORDER_LIGHTER};
        }}
        QTableWidget::item:selected {{
            background-color: {AppColors.BG_ROW_SELECTED};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            font-size: {header_font_size}px;
            font-weight: 500;
            padding: {padding + 4}px {padding}px;
            background-color: {AppColors.BG_HEADER};
            border: none;
            border-bottom: 1px solid {AppColors.BORDER};
            color: {AppColors.TEXT_PRIMARY};
        }}
    """


def get_input_style(font_size=14):
    return f"""
        QLineEdit {{
            font-size: {font_size}px;
            padding: 8px 12px;
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            background-color: {AppColors.BG_CARD};
        }}
        QLineEdit:focus {{
            border-color: {AppColors.PRIMARY_HOVER};
        }}
        QComboBox {{
            font-size: {font_size}px;
            padding: 6px 10px;
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            background-color: {AppColors.BG_CARD};
        }}
        QComboBox:hover {{
            border-color: {AppColors.PRIMARY_HOVER};
        }}
    """
