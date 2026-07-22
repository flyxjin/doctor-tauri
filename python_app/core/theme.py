# -*- coding: utf-8 -*-
"""
主题模块 - 新极简主义 + 东方雅致设计系统
设计原则：宣纸温润、本草清雅、墨色沉稳、触觉质感
配色灵感：宣纸米白 / 本草青 / 墨黑 / 朱砂红
"""


class AppColors:
    # --- 主色（本草青 - 沉稳专业，呼应中医药属性） ---
    PRIMARY = '#3D6B52'        # 本草青深
    PRIMARY_HOVER = '#4D7E63'  # 悬停稍亮
    PRIMARY_ACTIVE = '#2E5240' # 按下更深
    ACCENT = '#5A8A6A'         # 本草青主色
    ACCENT_HOVER = '#6B9B7B'   # 强调悬停
    ACCENT_LIGHT = '#EDF5F0'   # 本草青浅底

    # --- 语义色 ---
    SUCCESS = '#3D6B52'
    SUCCESS_HOVER = '#4D7E63'
    SUCCESS_BG = '#EDF5F0'
    WARNING = '#C8902E'        # 古铜黄（替代刺眼橙黄）
    WARNING_HOVER = '#D9A346'
    WARNING_BG = '#FBF5E8'
    DANGER = '#C8443A'         # 朱砂红（传统标记色）
    DANGER_HOVER = '#D85A50'
    DANGER_BG = '#FBEEEC'
    INFO = '#6B7280'
    INFO_HOVER = '#9CA3AF'

    # --- 文本（墨色系，中式书写感） ---
    TEXT_PRIMARY = '#2C2C2C'   # 墨黑
    TEXT_SECONDARY = '#6B6B6B' # 次级墨灰
    TEXT_MUTED = '#9C9C9C'
    TEXT_PLACEHOLDER = '#C8C8C8'
    TEXT_HEADING = '#1A1A1A'   # 标题深墨
    TEXT_WHITE = '#FFFFFF'

    # --- 背景（宣纸温润，长时间使用舒适） ---
    BG_PAGE = '#FAF8F3'        # 宣纸米白
    BG_CARD = '#FFFFFF'
    BG_SIDEBAR = '#FFFFFF'
    BG_MENUBAR = '#FFFFFF'
    BG_HEADER = '#FAF8F3'
    BG_HOVER = '#F3EFE6'       # 宣纸悬停
    BG_SELECTED = '#EDF5F0'    # 本草青浅底
    BG_SECONDARY = '#FAF8F3'
    BG_INPUT = '#FFFFFF'
    # 库存状态背景：库存为 0（朱砂红）、低库存（古铜黄）
    STOCK_ZERO_BG = '#FBEEEC'
    STOCK_LOW_BG = '#FBF5E8'

    # --- 边框 ---
    BORDER = '#E5DFD3'         # 宣纸边框
    BORDER_LIGHT = '#F0EBE0'
    BORDER_FOCUS = '#5A8A6A'

    # --- 禁用 ---
    DISABLED_BG = '#F0EBE0'
    DISABLED_TEXT = '#B8B8B8'

    # --- 侧栏 ---
    SIDEBAR_WIDTH = 220
    SIDEBAR_BG = '#FFFFFF'
    SIDEBAR_BORDER = '#E5DFD3'
    SIDEBAR_TEXT = '#6B6B6B'
    SIDEBAR_TEXT_ACTIVE = '#2C2C2C'
    SIDEBAR_HOVER = '#FAF8F3'
    SIDEBAR_INDICATOR = '#3D6B52'

    # --- 阴影（柔和漫射，营造纵深） ---
    SHADOW_SM = '0 1px 2px 0 rgba(60, 50, 40, 0.06)'
    SHADOW_MD = '0 4px 8px -2px rgba(60, 50, 40, 0.08), 0 2px 4px -2px rgba(60, 50, 40, 0.06)'
    SHADOW_LG = '0 12px 20px -4px rgba(60, 50, 40, 0.10), 0 4px 8px -4px rgba(60, 50, 40, 0.06)'
    SHADOW_HOVER = '0 6px 12px -2px rgba(61, 107, 82, 0.18)'

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
        QTableWidget::item:hover {{
            background-color: {AppColors.BG_HOVER};
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
            background-color: {AppColors.BG_HEADER};
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
            letter-spacing: -0.3px;
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
            padding: 10px 12px;
            border-radius: {AppColors.RADIUS_MD};
            margin: 2px 4px;
            min-width: 0;
            font-size: {button_size}px;
            min-height: 38px;
            border-left: 2px solid transparent;
        }}
        QPushButton#nav_btn:hover {{
            background-color: {AppColors.SIDEBAR_HOVER};
            color: {AppColors.SIDEBAR_TEXT_ACTIVE};
        }}
        QPushButton#nav_btn:checked {{
            background-color: {AppColors.ACCENT_LIGHT};
            color: {AppColors.PRIMARY};
            border-left: 2px solid {AppColors.PRIMARY};
            font-weight: 600;
        }}
        QPushButton#import_btn {{
            background-color: {AppColors.ACCENT};
            color: {AppColors.TEXT_WHITE};
            text-align: center;
            padding: 10px 14px;
            border-radius: {AppColors.RADIUS_MD};
            font-weight: 500;
            font-size: {button_size}px;
            min-height: 38px;
            margin: 4px;
        }}
        QPushButton#import_btn:hover {{
            background-color: {AppColors.ACCENT_HOVER};
        }}
        QLabel#version_label {{
            color: {AppColors.TEXT_MUTED};
            font-size: {tiny_size}px;
            padding: 4px 6px;
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
        QTableWidget::item:hover {{
            background-color: {AppColors.BG_HOVER};
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
            background-color: {AppColors.BG_HEADER};
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
