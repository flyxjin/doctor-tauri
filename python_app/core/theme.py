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


def get_main_window_style(base_size=14):
    title_size = int(base_size * 1.6)
    subtitle_size = int(base_size * 1.3)
    body_size = base_size
    small_size = int(base_size * 0.9)
    tiny_size = int(base_size * 0.85)
    button_size = int(base_size * 1.1)

    return f'''
        QMainWindow {{
            background-color: {AppColors.BG_PAGE};
        }}
        QPushButton {{
            background-color: {AppColors.PRIMARY};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: {button_size}px;
            text-align: left;
            min-width: 120px;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {AppColors.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {AppColors.PRIMARY_ACTIVE};
        }}
        QPushButton:checked {{
            background-color: {AppColors.PRIMARY_ACTIVE};
            font-weight: bold;
        }}
        QPushButton:disabled {{
            background-color: #d9d9d9;
            color: #8c8c8c;
        }}
        QLabel {{
            font-size: {body_size}px;
            color: {AppColors.TEXT_PRIMARY};
        }}
        QFrame {{
            background-color: {AppColors.BG_CARD};
            border-radius: 4px;
        }}
        QFrame#sidebar {{
            background-color: {AppColors.BG_SIDEBAR};
            border-radius: 0;
        }}
        QWidget#brand_container {{
            background-color: transparent;
            border-bottom: 1px solid #1f3a5f;
            margin-bottom: 8px;
        }}
        QLabel#brand_title {{
            color: #ffffff;
            font-size: {int(base_size * 1.35)}px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        QLabel#brand_subtitle {{
            color: #8c8c8c;
            font-size: {int(base_size * 0.8)}px;
            margin-top: 2px;
        }}
        QFrame#sidebar_separator {{
            background-color: transparent;
            border: none;
        }}
        QPushButton#nav_btn {{
            background-color: transparent;
            color: rgba(255, 255, 255, 0.65);
            text-align: left;
            padding: 12px 20px;
            border-radius: 4px;
            margin: 2px 8px;
            min-width: 0;
            font-size: {button_size}px;
            min-height: 40px;
            border-left: 3px solid transparent;
        }}
        QPushButton#nav_btn:hover {{
            background-color: rgba(255, 255, 255, 0.08);
            color: #ffffff;
        }}
        QPushButton#nav_btn:checked {{
            background-color: {AppColors.PRIMARY};
            color: #ffffff;
            border-left: 3px solid {AppColors.PRIMARY};
        }}
        QPushButton#import_btn {{
            background-color: #52c41a;
            color: white;
            text-align: center;
            padding: 12px 20px;
            border-radius: 4px;
            font-weight: 500;
            font-size: {button_size}px;
            min-height: 40px;
            margin: 8px;
        }}
        QPushButton#import_btn:hover {{
            background-color: #73d13d;
        }}
        QLabel#version_label {{
            color: #595959;
            font-size: {tiny_size}px;
            padding: 8px;
        }}
        QFrame#content_area {{
            background-color: transparent;
        }}
        QGroupBox {{
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            margin-top: 12px;
            font-weight: 500;
            font-size: {subtitle_size}px;
            color: {AppColors.TEXT_PRIMARY};
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: {AppColors.PRIMARY};
        }}
        QTableWidget {{
            font-size: {body_size}px;
            gridline-color: {AppColors.BORDER_LIGHTER};
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
        }}
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {AppColors.BORDER_LIGHTER};
        }}
        QTableWidget::item:selected {{
            background-color: {AppColors.BG_ROW_SELECTED};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            font-size: {button_size}px;
            font-weight: 500;
            padding: 12px 8px;
            background-color: {AppColors.BG_HEADER};
            border: none;
            border-bottom: 1px solid {AppColors.BORDER};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QLineEdit {{
            font-size: {body_size}px;
            padding: 8px 12px;
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            min-height: 28px;
            background-color: {AppColors.BG_CARD};
        }}
        QLineEdit:focus {{
            border-color: {AppColors.PRIMARY_HOVER};
        }}
        QLineEdit:hover {{
            border-color: {AppColors.PRIMARY_HOVER};
        }}
        QComboBox {{
            font-size: {body_size}px;
            padding: 6px 10px;
            min-height: 28px;
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            background-color: {AppColors.BG_CARD};
        }}
        QComboBox:hover {{
            border-color: {AppColors.PRIMARY_HOVER};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QTextEdit {{
            font-size: {body_size}px;
            padding: 8px;
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            background-color: {AppColors.BG_CARD};
        }}
        QTextEdit:focus {{
            border-color: {AppColors.PRIMARY_HOVER};
        }}
        QScrollBar:vertical {{
            width: 8px;
            background-color: transparent;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: #d9d9d9;
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: #8c8c8c;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            height: 8px;
            background-color: transparent;
        }}
        QScrollBar::handle:horizontal {{
            background-color: #d9d9d9;
            border-radius: 4px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: #8c8c8c;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QMessageBox {{
            font-size: {body_size}px;
        }}
        QMessageBox QLabel {{
            color: {AppColors.TEXT_PRIMARY};
        }}
        QMenu {{
            background-color: {AppColors.BG_CARD};
            border: 1px solid {AppColors.BORDER};
            border-radius: 4px;
            padding: 4px 0;
        }}
        QMenu::item {{
            padding: 8px 16px;
            color: {AppColors.TEXT_PRIMARY};
        }}
        QMenu::item:selected {{
            background-color: {AppColors.BG_ROW_SELECTED};
            color: {AppColors.PRIMARY};
        }}
        QMenuBar {{
            background-color: {AppColors.BG_SIDEBAR};
            color: rgba(255, 255, 255, 0.85);
            padding: 0 10px;
            border-bottom: 1px solid #1f3a5f;
        }}
        QMenuBar::item {{
            padding: 10px 16px;
            background-color: transparent;
            border-radius: 0;
        }}
        QMenuBar::item:selected {{
            background-color: rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }}
        QStatusBar {{
            background-color: {AppColors.BG_PAGE};
            color: #595959;
            border-top: 1px solid {AppColors.BORDER};
            padding: 4px 12px;
        }}
    '''
