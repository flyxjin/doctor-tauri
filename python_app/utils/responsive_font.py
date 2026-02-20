from PyQt5.QtCore import QObject, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QApplication, QWidget


class ResponsiveFontManager(QObject):
    font_changed = pyqtSignal(str, int)
    
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
            'xs': {'min_width': 0, 'max_width': 768, 'base_size': 14, 'name': '移动设备'},
            'sm': {'min_width': 769, 'max_width': 1024, 'base_size': 15, 'name': '平板设备'},
            'md': {'min_width': 1025, 'max_width': 1366, 'base_size': 16, 'name': '小型桌面'},
            'lg': {'min_width': 1367, 'max_width': 1600, 'base_size': 17, 'name': '标准桌面'},
            'xl': {'min_width': 1601, 'max_width': 99999, 'base_size': 18, 'name': '大型桌面'},
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
        
        self.current_preset = 'lg'
        self.current_base_size = 17
        self._cached_fonts = {}
        
    def update_for_window_size(self, width, height=None):
        if height is None:
            height = width
            
        new_preset = self._get_preset_for_width(width)
        
        if new_preset != self.current_preset:
            old_preset = self.current_preset
            self.current_preset = new_preset
            self.current_base_size = self.size_presets[new_preset]['base_size']
            self._cached_fonts.clear()
            self.font_changed.emit(new_preset, self.current_base_size)
            
        return self.current_preset
    
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
            'width_range': f"{preset['min_width']}-{preset['max_width']}px"
        }


class ResponsiveWidget:
    def __init__(self):
        self._font_manager = ResponsiveFontManager()
        self._font_manager.font_changed.connect(self._on_font_changed)
        
    def _on_font_changed(self, preset, base_size):
        if hasattr(self, '_apply_responsive_fonts'):
            self._apply_responsive_fonts()
            
    def _apply_responsive_fonts(self):
        pass
    
    def _update_fonts_for_size(self, width):
        return self._font_manager.update_for_window_size(width)
    
    def _get_font(self, font_type='body'):
        return self._font_manager.get_font(font_type)
    
    def _get_font_size(self, font_type='body'):
        return self._font_manager.get_font_size(font_type)


def get_font_manager():
    return ResponsiveFontManager()
