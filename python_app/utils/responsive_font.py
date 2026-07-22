from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont


class ResponsiveFontManager(QObject):
    font_changed = Signal(str, int)
    size_changed = Signal(int, int)

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = QObject.__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if ResponsiveFontManager._initialized:
            return
        super().__init__(parent)
        ResponsiveFontManager._initialized = True

        self.base_font_family = "Microsoft YaHei"

        self.size_presets = {
            'xs': {'min_width': 0, 'max_width': 768, 'base_size': 14, 'scale': 0.8, 'name': '移动设备'},
            'sm': {'min_width': 769, 'max_width': 1024, 'base_size': 15, 'scale': 0.85, 'name': '平板设备'},
            'md': {'min_width': 1025, 'max_width': 1366, 'base_size': 16, 'scale': 0.9, 'name': '小型桌面'},
            'lg': {'min_width': 1367, 'max_width': 1600, 'base_size': 17, 'scale': 1.0, 'name': '标准桌面'},
            'xl': {'min_width': 1601, 'max_width': 1920, 'base_size': 18, 'scale': 1.1, 'name': '大型桌面'},
            'fullscreen': {'min_width': 1921, 'max_width': 99999, 'base_size': 20, 'scale': 1.2, 'name': '全屏模式'},
        }

        self.font_scales = {
            'title': 1.6,
            'subtitle': 1.3,
            'body': 1.0,
            'small': 0.9,
            'tiny': 0.85,
            'button': 1.1,
            'table_header': 1.1,
            'table_cell': 1.0,
            'label': 1.0,
            'input': 1.0,
        }

        self.base_table_config = {
            'row_height': 32,
            'header_height': 36,
            'cell_padding': 8,
            'column_padding': 12,
            'min_column_width': 60,
            'max_column_width': 300,
        }

        self.current_preset = 'lg'
        self.current_base_size = 17
        self.current_width = 1400
        self.current_scale = 1.0
        self._cached_fonts = {}

    def update_for_window_size(self, width, height=None):
        if height is None:
            height = width

        new_preset = self._get_preset_for_width(width)
        width_changed = abs(width - self.current_width) > 10

        if new_preset != self.current_preset or width_changed:
            self.current_preset = new_preset
            self.current_width = width
            self.current_base_size = self._calculate_base_size(width)
            self.current_scale = self._calculate_scale(width)
            self._cached_fonts.clear()
            self.font_changed.emit(new_preset, self.current_base_size)
            self.size_changed.emit(width, self.current_base_size)

        return self.current_preset

    def _calculate_base_size(self, width) -> int:
        preset = self._get_preset_for_width(width)
        preset_base: Any = self.size_presets[preset]['base_size']

        if width >= 2560:
            return int(preset_base) + 2
        elif width >= 1920:
            return int(preset_base) + 1
        else:
            return int(preset_base)

    def _calculate_scale(self, width) -> float:
        preset = self._get_preset_for_width(width)
        base_scale: Any = self.size_presets[preset]['scale']

        if width >= 2560:
            return float(base_scale) + 0.1
        elif width >= 1920:
            return float(base_scale) + 0.05
        else:
            return float(base_scale)

    def _get_preset_for_width(self, width):
        for preset_name, preset_config in self.size_presets.items():
            if preset_config['min_width'] <= width <= preset_config['max_width']:
                return preset_name
        return 'lg'

    def get_font(self, font_type='body'):
        cache_key = f"{self.current_preset}_{font_type}"

        if cache_key in self._cached_fonts:
            return self._cached_fonts[cache_key]

        scale = self.font_scales.get(font_type, 1.0)
        size = max(8, int(self.current_base_size * scale))

        font = QFont(self.base_font_family, size)

        if font_type in ['title', 'subtitle']:
            font.setBold(True)

        self._cached_fonts[cache_key] = font
        return font

    def get_font_size(self, font_type='body'):
        scale = self.font_scales.get(font_type, 1.0)
        return max(8, int(self.current_base_size * scale))

    def get_scale(self):
        return self.current_scale

    def get_table_row_height(self):
        return int(self.base_table_config['row_height'] * self.current_scale)

    def get_table_header_height(self):
        return int(self.base_table_config['header_height'] * self.current_scale)

    def get_table_cell_padding(self):
        return int(self.base_table_config['cell_padding'] * self.current_scale)

    def get_table_column_width(self, base_width):
        scaled = int(base_width * self.current_scale)
        return max(self.base_table_config['min_column_width'],
                   min(scaled, self.base_table_config['max_column_width']))

    def get_table_config(self):
        return {
            'row_height': self.get_table_row_height(),
            'header_height': self.get_table_header_height(),
            'cell_padding': self.get_table_cell_padding(),
            'font_size': self.get_font_size('table_cell'),
            'header_font_size': self.get_font_size('table_header'),
            'scale': self.current_scale,
        }

    def get_stylesheet_font_size(self, font_type='body'):
        size = self.get_font_size(font_type)
        return f"font-size: {size}px;"

    def get_responsive_stylesheet(self):
        base = self.current_base_size
        title = int(base * self.font_scales['title'])
        subtitle = int(base * self.font_scales['subtitle'])
        body = int(base * self.font_scales['body'])
        small = int(base * self.font_scales['small'])
        tiny = int(base * self.font_scales['tiny'])

        return f"""
            QLabel {{
                font-size: {body}px;
            }}
            QPushButton {{
                font-size: {body}px;
            }}
            QLineEdit {{
                font-size: {body}px;
            }}
            QTableWidget {{
                font-size: {small}px;
            }}
            QHeaderView::section {{
                font-size: {body}px;
                font-weight: bold;
            }}
            QComboBox {{
                font-size: {body}px;
            }}
            QTextEdit {{
                font-size: {body}px;
            }}
            QGroupBox {{
                font-size: {subtitle}px;
                font-weight: bold;
            }}
            .title {{
                font-size: {title}px;
                font-weight: bold;
            }}
            .subtitle {{
                font-size: {subtitle}px;
            }}
            .small {{
                font-size: {small}px;
            }}
            .tiny {{
                font-size: {tiny}px;
            }}
        """

    def get_current_preset_info(self):
        preset = self.size_presets[self.current_preset]
        return {
            'name': preset['name'],
            'base_size': preset['base_size'],
            'scale': self.current_scale,
            'width_range': f"{preset['min_width']}-{preset['max_width']}px"
        }


class ResponsiveWidget:
    def __init__(self):
        # 使用全局单例，确保所有组件监听同一个信号
        self._font_manager = get_font_manager()
        self._font_manager.font_changed.connect(self._on_font_changed)
        self._font_manager.size_changed.connect(self._on_size_changed)

    def _on_font_changed(self, preset, base_size):
        if hasattr(self, '_apply_responsive_fonts'):
            self._apply_responsive_fonts()

    def _on_size_changed(self, width, base_size):
        if hasattr(self, '_apply_responsive_table'):
            self._apply_responsive_table()

    def _apply_responsive_fonts(self):
        pass

    def _apply_responsive_table(self):
        pass

    def _update_fonts_for_size(self, width):
        return self._font_manager.update_for_window_size(width)

    def _get_font(self, font_type='body'):
        return self._font_manager.get_font(font_type)

    def _get_font_size(self, font_type='body'):
        return self._font_manager.get_font_size(font_type)

    def _get_scale(self):
        return self._font_manager.get_scale()

    def _get_table_config(self):
        return self._font_manager.get_table_config()


_font_manager_instance = None


def get_font_manager():
    """全局单例，确保所有组件监听同一个 font_changed 信号。"""
    global _font_manager_instance
    if _font_manager_instance is None:
        _font_manager_instance = ResponsiveFontManager()
    return _font_manager_instance
