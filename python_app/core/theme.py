# -*- coding: utf-8 -*-
"""
主题模块 - 现代极简设计系统
设计原则：大留白、细边框、克制色彩、清晰层次
"""


class AppColors:
    # --- 主色 ---
    PRIMARY = '#111827'
    PRIMARY_HOVER = '#1F2937'
    PRIMARY_ACTIVE = '#030712'
    ACCENT = '#6366F1'
    ACCENT_HOVER = '#818CF8'
    ACCENT_LIGHT = '#EEF2FF'

    # --- 语义色 ---
    SUCCESS = '#10B981'
    SUCCESS_HOVER = '#34D399'
    SUCCESS_BG = '#ECFDF5'
    WARNING = '#F59E0B'
    WARNING_HOVER = '#FBBF24'
    WARNING_BG = '#FFFBEB'
    DANGER = '#EF4444'
    DANGER_HOVER = '#F87171'
    DANGER_BG = '#FEF2F2'
    INFO = '#6B7280'
    INFO_HOVER = '#9CA3AF'

    # --- 文本 ---
    TEXT_PRIMARY = '#111827'
    TEXT_SECONDARY = '#6B7280'
    TEXT_MUTED = '#9CA3AF'
    TEXT_PLACEHOLDER = '#D1D5DB'
    TEXT_HEADING = '#030712'
    TEXT_WHITE = '#FFFFFF'

    # --- 背景 ---
    BG_PAGE = '#F9FAFB'
    BG_CARD = '#FFFFFF'
    BG_SIDEBAR = '#FFFFFF'
    BG_MENUBAR = '#FFFFFF'
    BG_HEADER = '#F9FAFB'
    BG_HOVER = '#F3F4F6'
    BG_SELECTED = '#F0FDF4'
    BG_SECONDARY = '#F9FAFB'
    BG_INPUT = '#FFFFFF'
    # 库存状态背景：库存为 0（危险红）、低库存（警告黄）
    STOCK_ZERO_BG = '#FEE2E2'
    STOCK_LOW_BG = '#FEF3C7'

    # --- 边框 ---
    BORDER = '#E5E7EB'
    BORDER_LIGHT = '#F3F4F6'
    BORDER_FOCUS = '#6366F1'

    # --- 禁用 ---
    DISABLED_BG = '#F3F4F6'
    DISABLED_TEXT = '#9CA3AF'

    # --- 侧栏 ---
    SIDEBAR_WIDTH = 220
    SIDEBAR_BG = '#FFFFFF'
    SIDEBAR_BORDER = '#E5E7EB'
    SIDEBAR_TEXT = '#6B7280'
    SIDEBAR_TEXT_ACTIVE = '#111827'
    SIDEBAR_HOVER = '#F9FAFB'
    SIDEBAR_INDICATOR = '#111827'

    # --- 阴影 ---
    SHADOW_SM = '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
    SHADOW_MD = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)'
    SHADOW_LG = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)'

    # --- 圆角 ---
    RADIUS_SM = '4px'
    RADIUS_MD = '6px'
    RADIUS_LG = '8px'
    RADIUS_XL = '12px'


def get_button_style(bg_color=None, text_color='#FFFFFF',
                     padding='10px 20px', border_radius='6px',
                     font_size=None, min_width=None, min_height=None):
    if bg_color is None:
        bg_color = AppColors.PRIMARY
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
            border-radius: {border_radius};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {bg_color}ee;
        }}
        QPushButton:pressed {{
            background-color: {bg_color}dd;
        }}
        QPushButton:disabled {{
            background-color: {AppColors.DISABLED_BG};
            color: {AppColors.DISABLED_TEXT};
        }}
    """


def get_secondary_button_style(padding='10px 20px', border_radius='6px',
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
            color: {AppColors.TEXT_PRIMARY};
            border: 1px solid {AppColors.BORDER};
            padding: {padding};
            border-radius: {border_radius};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {AppColors.BG_HOVER};
            border-color: {AppColors.TEXT_MUTED};
        }}
        QPushButton:pressed {{
            background-color: {AppColors.BORDER_LIGHT};
        }}
        QPushButton:disabled {{
            background-color: {AppColors.DISABLED_BG};
            color: {AppColors.DISABLED_TEXT};
            border-color: {AppColors.BORDER};
        }}
    """


def get_table_style(font_size=13, header_font_size=12, padding=12):
    return f"""
        QTableWidget {{
            font-size: {font_size}px;
            gridline-color: {AppColors.BORDER_LIGHT};
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            selection-background-color: {AppColors.ACCENT_LIGHT};
        }}
        QTableWidget::item {{
            padding: {padding}px;
            border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QTableWidget::item:selected {{
            background-color: {AppColors.ACCENT_LIGHT};
            color: {AppColors.ACCENT};
        }}
        QHeaderView::section {{
            font-size: {header_font_size}px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: {padding}px {padding + 4}px;
            background-color: {AppColors.BG_PAGE};
            border: none;
            border-bottom: 2px solid {AppColors.BORDER};
            color: {AppColors.TEXT_SECONDARY};
        }}
    """


def get_input_style(font_size=14):
    return f"""
        QLineEdit {{
            font-size: {font_size}px;
            padding: 10px 14px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
            selection-background-color: {AppColors.ACCENT_LIGHT};
        }}
        QLineEdit:focus {{
            border-color: {AppColors.ACCENT};
            outline: none;
        }}
        QLineEdit:hover {{
            border-color: {AppColors.TEXT_MUTED};
        }}
        QLineEdit::placeholder {{
            color: {AppColors.TEXT_PLACEHOLDER};
        }}
        QComboBox {{
            font-size: {font_size}px;
            padding: 8px 12px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QComboBox:hover {{
            border-color: {AppColors.TEXT_MUTED};
        }}
        QComboBox:focus {{
            border-color: {AppColors.ACCENT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            selection-background-color: {AppColors.ACCENT_LIGHT};
            selection-color: {AppColors.ACCENT};
            padding: 4px;
        }}
    """


def get_dialog_style():
    return f"""
        QDialog {{
            background-color: {AppColors.BG_CARD};
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_LG};
        }}
        QDialog QLabel {{
            color: {AppColors.TEXT_PRIMARY};
            font-size: 13px;
        }}
        QDialog QPushButton {{
            padding: 8px 16px;
            border-radius: {AppColors.RADIUS_MD};
            font-weight: 500;
            min-width: 80px;
        }}
    """


def get_main_window_style(base_size=14):
    title_size = int(base_size * 1.5)
    subtitle_size = int(base_size * 1.2)
    body_size = base_size
    small_size = int(base_size * 0.9)
    tiny_size = int(base_size * 0.8)
    button_size = int(base_size * 1.0)

    return f'''
        QMainWindow {{
            background-color: {AppColors.BG_PAGE};
        }}
        QPushButton {{
            background-color: {AppColors.PRIMARY};
            color: {AppColors.TEXT_WHITE};
            border: none;
            padding: 10px 20px;
            border-radius: {AppColors.RADIUS_MD};
            font-size: {button_size}px;
            font-weight: 500;
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
            background-color: {AppColors.PRIMARY};
            font-weight: 600;
        }}
        QPushButton:disabled {{
            background-color: {AppColors.DISABLED_BG};
            color: {AppColors.DISABLED_TEXT};
        }}
        QLabel {{
            font-size: {body_size}px;
            color: {AppColors.TEXT_PRIMARY};
            background-color: transparent;
        }}
        QFrame {{
            background-color: {AppColors.BG_CARD};
            border: none;
        }}
        QFrame#sidebar {{
            background-color: {AppColors.SIDEBAR_BG};
            border-right: 1px solid {AppColors.SIDEBAR_BORDER};
        }}
        QWidget#brand_container {{
            background-color: transparent;
            border-bottom: 1px solid {AppColors.BORDER};
            padding-bottom: 16px;
            margin-bottom: 8px;
        }}
        QLabel#brand_title {{
            color: {AppColors.TEXT_HEADING};
            font-size: {int(base_size * 1.2)}px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        QLabel#brand_subtitle {{
            color: {AppColors.TEXT_MUTED};
            font-size: {int(base_size * 0.75)}px;
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
            padding: 12px 16px;
            border-radius: {AppColors.RADIUS_MD};
            margin: 2px 8px;
            min-width: 0;
            font-size: {button_size}px;
            min-height: 40px;
            border-left: 2px solid transparent;
        }}
        QPushButton#nav_btn:hover {{
            background-color: {AppColors.SIDEBAR_HOVER};
            color: {AppColors.SIDEBAR_TEXT_ACTIVE};
        }}
        QPushButton#nav_btn:checked {{
            background-color: {AppColors.ACCENT_LIGHT};
            color: {AppColors.ACCENT};
            border-left: 2px solid {AppColors.ACCENT};
            font-weight: 600;
        }}
        QPushButton#import_btn {{
            background-color: {AppColors.ACCENT};
            color: {AppColors.TEXT_WHITE};
            text-align: center;
            padding: 12px 20px;
            border-radius: {AppColors.RADIUS_MD};
            font-weight: 500;
            font-size: {button_size}px;
            min-height: 40px;
            margin: 8px;
        }}
        QPushButton#import_btn:hover {{
            background-color: {AppColors.ACCENT_HOVER};
        }}
        QLabel#version_label {{
            color: {AppColors.TEXT_MUTED};
            font-size: {tiny_size}px;
            padding: 8px;
        }}
        QFrame#content_area {{
            background-color: transparent;
            border: none;
        }}
        QGroupBox {{
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            margin-top: 16px;
            font-weight: 600;
            font-size: {subtitle_size}px;
            color: {AppColors.TEXT_PRIMARY};
            padding-top: 16px;
            background-color: {AppColors.BG_CARD};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: {AppColors.TEXT_PRIMARY};
        }}
        QTableWidget {{
            font-size: {body_size}px;
            gridline-color: {AppColors.BORDER_LIGHT};
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
        }}
        QTableWidget::item {{
            padding: 10px;
            border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QTableWidget::item:selected {{
            background-color: {AppColors.ACCENT_LIGHT};
            color: {AppColors.ACCENT};
        }}
        QHeaderView::section {{
            font-size: {small_size}px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 12px 10px;
            background-color: {AppColors.BG_PAGE};
            border: none;
            border-bottom: 2px solid {AppColors.BORDER};
            color: {AppColors.TEXT_SECONDARY};
        }}
        QLineEdit {{
            font-size: {body_size}px;
            padding: 10px 14px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            min-height: 28px;
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QLineEdit:focus {{
            border-color: {AppColors.ACCENT};
        }}
        QLineEdit:hover {{
            border-color: {AppColors.TEXT_MUTED};
        }}
        QComboBox {{
            font-size: {body_size}px;
            padding: 8px 12px;
            min-height: 28px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QComboBox:hover {{
            border-color: {AppColors.TEXT_MUTED};
        }}
        QComboBox:focus {{
            border-color: {AppColors.ACCENT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QTextEdit {{
            font-size: {body_size}px;
            padding: 10px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QTextEdit:focus {{
            border-color: {AppColors.ACCENT};
        }}
        QScrollBar:vertical {{
            width: 6px;
            background-color: transparent;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: {AppColors.BORDER};
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {AppColors.TEXT_MUTED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            height: 6px;
            background-color: transparent;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {AppColors.BORDER};
            border-radius: 3px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {AppColors.TEXT_MUTED};
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
            border-radius: {AppColors.RADIUS_MD};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 8px 16px;
            color: {AppColors.TEXT_PRIMARY};
            border-radius: {AppColors.RADIUS_SM};
        }}
        QMenu::item:selected {{
            background-color: {AppColors.ACCENT_LIGHT};
            color: {AppColors.ACCENT};
        }}
        QMenuBar {{
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
            padding: 0 10px;
            border-bottom: 1px solid {AppColors.BORDER};
        }}
        QMenuBar::item {{
            padding: 10px 16px;
            background-color: transparent;
            border-radius: 0;
        }}
        QMenuBar::item:selected {{
            background-color: {AppColors.BG_HOVER};
        }}
        QStatusBar {{
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_MUTED};
            border-top: 1px solid {AppColors.BORDER};
            padding: 4px 12px;
            font-size: {small_size}px;
        }}
        QProgressBar {{
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            height: 8px;
            background-color: {AppColors.BORDER_LIGHT};
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {AppColors.ACCENT};
            border-radius: 4px;
        }}
        QSpinBox, QDoubleSpinBox {{
            font-size: {body_size}px;
            padding: 8px 12px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {AppColors.ACCENT};
        }}
        QDateEdit {{
            font-size: {body_size}px;
            padding: 8px 12px;
            border: 1px solid {AppColors.BORDER};
            border-radius: {AppColors.RADIUS_MD};
            background-color: {AppColors.BG_CARD};
            color: {AppColors.TEXT_PRIMARY};
        }}
        QDateEdit:focus {{
            border-color: {AppColors.ACCENT};
        }}
    '''
