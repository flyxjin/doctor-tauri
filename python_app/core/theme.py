# -*- coding: utf-8 -*-
"""
主题模块 - 集中管理样式常量和工具函数
配色标准：Ant Design
"""


class AppColors:
    # --- 主色 ---
    PRIMARY = '#1890ff'
    PRIMARY_HOVER = '#40a9ff'
    PRIMARY_ACTIVE = '#096dd9'

    # --- 语义色 ---
    SUCCESS = '#52c41a'
    SUCCESS_HOVER = '#73d13d'
    SUCCESS_ACTIVE = '#389e0d'
    WARNING = '#faad14'
    WARNING_HOVER = '#ffc53d'
    WARNING_ACTIVE = '#d48806'
    DANGER = '#ff4d4f'
    DANGER_HOVER = '#ff7875'
    DANGER_ACTIVE = '#cf1322'
    INFO = '#8c8c8c'
    INFO_HOVER = '#a6a6a6'

    # --- 文本 ---
    TEXT_PRIMARY = '#303133'
    TEXT_REGULAR = '#606266'
    TEXT_SECONDARY = '#909399'
    TEXT_PLACEHOLDER = '#c0c4cc'
    TEXT_HEADING = '#262626'
    TEXT_CAPTION = '#595959'

    # --- 背景 ---
    BG_PAGE = '#f0f2f5'
    BG_CARD = '#ffffff'
    BG_SIDEBAR = '#001529'
    BG_MENUBAR = '#001529'
    BG_HEADER = '#fafafa'
    BG_ROW_HOVER = '#f5f7fa'
    BG_ROW_SELECTED = '#e6f7ff'
    BG_SECONDARY = '#f5f7fa'
    BG_PROGRESS = '#f5f5f5'
    BG_SUCCESS_LIGHT = '#f6ffed'
    BG_DANGER_LIGHT = '#fff2f0'
    BG_WARNING_LIGHT = '#fffbe6'
    BG_PRIMARY_LIGHT = '#e6f7ff'

    # --- 边框 ---
    BORDER = '#dcdfe6'
    BORDER_LIGHT = '#e4e7ed'
    BORDER_LIGHTER = '#ebeef5'
    BORDER_DARK = '#d9d9d9'

    # --- 禁用 ---
    DISABLED_BG = '#d9d9d9'
    DISABLED_TEXT = '#8c8c8c'

    # --- 侧栏 ---
    SIDEBAR_SEPARATOR = '#1f3a5f'
    SIDEBAR_TEXT = 'rgba(255, 255, 255, 0.65)'
    SIDEBAR_TEXT_ACTIVE = '#ffffff'
    SIDEBAR_HOVER_BG = 'rgba(255, 255, 255, 0.08)'

    # --- 库存预警 ---
    STOCK_ZERO = '#ff4d4f'
    STOCK_ZERO_BG = '#fff2f0'
    STOCK_LOW = '#faad14'
    STOCK_LOW_BG = '#fffbe6'


def get_button_style(bg_color=AppColors.PRIMARY, text_color='white',
                     padding='10px 20px', border_radius='4px',
                     font_size=None, min_width=None, min_height=None):
    parts = [f'font-size: {font_size}px'] if font_size else []
    if min_width:
        parts.append(f'min-width: {min_width}px')
    if min_height:
        parts.append(f'min-height: {min_height}px')
    extra = '; '.join(parts)
    if extra:
        extra = '; ' + extra
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            padding: {padding};
            border-radius: {border_radius}{extra};
        }}
        QPushButton:hover {{
            background-color: {bg_color}dd;
        }}
        QPushButton:pressed {{
            background-color: {bg_color}bb;
        }}
        QPushButton:disabled {{
            background-color: {AppColors.DISABLED_BG};
            color: {AppColors.DISABLED_TEXT};
        }}
    """


def get_secondary_button_style(padding='10px 20px', border_radius='4px',
                               font_size=None, min_width=None, min_height=None):
    parts = [f'font-size: {font_size}px'] if font_size else []
    if min_width:
        parts.append(f'min-width: {min_width}px')
    if min_height:
        parts.append(f'min-height: {min_height}px')
    extra = '; '.join(parts)
    if extra:
        extra = '; ' + extra
    return f"""
        QPushButton {{
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_CAPTION};
            border: 1px solid {AppColors.BORDER_DARK};
            padding: {padding};
            border-radius: {border_radius}{extra};
        }}
        QPushButton:hover {{
            border-color: {AppColors.PRIMARY};
            color: {AppColors.PRIMARY};
        }}
        QPushButton:pressed {{
            border-color: {AppColors.PRIMARY_ACTIVE};
            color: {AppColors.PRIMARY_ACTIVE};
        }}
        QPushButton:disabled {{
            background-color: {AppColors.DISABLED_BG};
            color: {AppColors.DISABLED_TEXT};
            border-color: {AppColors.BORDER_DARK};
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


def get_dialog_style():
    return f"""
        QDialog {{
            background-color: {AppColors.BG_CARD};
        }}
        QDialog QLabel {{
            color: {AppColors.TEXT_PRIMARY};
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
            background-color: {AppColors.DISABLED_BG};
            color: {AppColors.DISABLED_TEXT};
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
            border-bottom: 1px solid {AppColors.SIDEBAR_SEPARATOR};
            margin-bottom: 8px;
        }}
        QLabel#brand_title {{
            color: {AppColors.SIDEBAR_TEXT_ACTIVE};
            font-size: {int(base_size * 1.35)}px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        QLabel#brand_subtitle {{
            color: {AppColors.INFO};
            font-size: {int(base_size * 0.8)}px;
            margin-top: 2px;
        }}
        QFrame#sidebar_separator {{
            background-color: transparent;
            border: none;
        }}
        QPushButton#nav_btn {{
            background-color: transparent;
            color: {AppColors.SIDEBAR_TEXT};
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
            background-color: {AppColors.SIDEBAR_HOVER_BG};
            color: {AppColors.SIDEBAR_TEXT_ACTIVE};
        }}
        QPushButton#nav_btn:checked {{
            background-color: {AppColors.PRIMARY};
            color: {AppColors.SIDEBAR_TEXT_ACTIVE};
            border-left: 3px solid {AppColors.PRIMARY};
        }}
        QPushButton#import_btn {{
            background-color: {AppColors.SUCCESS};
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
            background-color: {AppColors.SUCCESS_HOVER};
        }}
        QLabel#version_label {{
            color: {AppColors.TEXT_CAPTION};
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
            background-color: {AppColors.DISABLED_BG};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {AppColors.DISABLED_TEXT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            height: 8px;
            background-color: transparent;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {AppColors.DISABLED_BG};
            border-radius: 4px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {AppColors.DISABLED_TEXT};
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
            background-color: {AppColors.BG_MENUBAR};
            color: rgba(255, 255, 255, 0.85);
            padding: 0 10px;
            border-bottom: 1px solid {AppColors.SIDEBAR_SEPARATOR};
        }}
        QMenuBar::item {{
            padding: 10px 16px;
            background-color: transparent;
            border-radius: 0;
        }}
        QMenuBar::item:selected {{
            background-color: {AppColors.SIDEBAR_HOVER_BG};
            color: {AppColors.SIDEBAR_TEXT_ACTIVE};
        }}
        QStatusBar {{
            background-color: {AppColors.BG_PAGE};
            color: {AppColors.TEXT_CAPTION};
            border-top: 1px solid {AppColors.BORDER};
            padding: 4px 12px;
        }}
        QProgressBar {{
            border: 1px solid {AppColors.BORDER_DARK};
            border-radius: 4px;
            height: 20px;
            background-color: {AppColors.BG_PROGRESS};
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {AppColors.PRIMARY};
            border-radius: 3px;
        }}
    '''
