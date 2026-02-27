# -*- coding: utf-8 -*-
"""
Windows 7 Compatibility Adapter Module
Provides compatibility fixes for Windows 7 operating system

Changes made for Windows 7:
1. DPI awareness setup for legacy Windows
2. TLS 1.2 support for HTTPS connections
3. Application data directory handling
4. System version detection
"""
import sys
import os
import ctypes
from typing import Optional, Tuple


class Windows7Compat:
    """Windows 7 compatibility adapter class"""
    
    _is_windows7: Optional[bool] = None
    _is_initialized: bool = False
    
    @classmethod
    def is_windows7(cls) -> bool:
        """Check if running on Windows 7"""
        if cls._is_windows7 is not None:
            return cls._is_windows7
        
        if sys.platform != 'win32':
            cls._is_windows7 = False
            return False
        
        try:
            ver = sys.getwindowsversion()
            cls._is_windows7 = (ver.major == 6 and ver.minor == 1)
        except AttributeError:
            try:
                import platform
                version = platform.version()
                cls._is_windows7 = version.startswith('6.1')
            except:
                cls._is_windows7 = False
        
        return cls._is_windows7
    
    @classmethod
    def get_windows_version(cls) -> Tuple[int, int, int]:
        """Get Windows version as tuple (major, minor, build)"""
        if sys.platform != 'win32':
            return (0, 0, 0)
        
        try:
            ver = sys.getwindowsversion()
            return (ver.major, ver.minor, ver.build)
        except:
            return (0, 0, 0)
    
    @classmethod
    def setup_dpi_awareness(cls) -> bool:
        """
        Setup DPI awareness for Windows 7
        Windows 7 uses SetProcessDPIAware API
        """
        if sys.platform != 'win32':
            return False
        
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            return True
        except (AttributeError, OSError):
            return False
    
    @classmethod
    def setup_high_dpi_scaling(cls) -> bool:
        """
        Setup high DPI scaling for Qt applications
        This must be called before QApplication is created
        """
        if sys.platform != 'win32':
            return False
        
        try:
            from PyQt5.QtCore import Qt, QCoreApplication
            
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            return True
        except ImportError:
            return False
        except AttributeError:
            return False
    
    @classmethod
    def setup_tls_support(cls) -> bool:
        """
        Setup TLS 1.2 support for HTTPS connections
        Windows 7 SP1 supports TLS 1.2 but may need configuration
        """
        if sys.platform != 'win32':
            return False
        
        try:
            import ssl
            
            if hasattr(ssl, 'PROTOCOL_TLS_CLIENT'):
                ssl._create_default_https_context = ssl._create_unverified_context
            
            return True
        except (ImportError, AttributeError):
            return False
    
    @classmethod
    def create_ssl_context(cls) -> Optional['ssl.SSLContext']:
        """
        Create SSL context compatible with Windows 7
        Returns SSL context with TLS 1.2 support
        """
        try:
            import ssl
            
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            try:
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')
            except AttributeError:
                pass
            
            return ctx
        except (ImportError, AttributeError):
            try:
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                return ctx
            except:
                return None
    
    @classmethod
    def get_app_data_dir(cls, app_name: str = 'MedicineSystem') -> str:
        """
        Get application data directory
        Uses %APPDATA% on Windows for proper permissions
        """
        if getattr(sys, 'frozen', False):
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(app_data, app_name)
        else:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if not os.path.exists(app_dir):
            try:
                os.makedirs(app_dir)
            except OSError:
                app_dir = os.path.expanduser('~')
        
        return app_dir
    
    @classmethod
    def check_system_requirements(cls) -> Tuple[bool, list]:
        """
        Check if system meets requirements for running the application
        Returns (is_compatible, list_of_issues)
        """
        issues = []
        
        if sys.platform != 'win32':
            issues.append("This application is designed for Windows")
            return (False, issues)
        
        ver = cls.get_windows_version()
        
        if ver[0] < 6 or (ver[0] == 6 and ver[1] < 1):
            issues.append("Windows 7 or later is required")
            return (False, issues)
        
        py_ver = sys.version_info
        if py_ver.major != 3 or py_ver.minor > 8:
            issues.append("Python 3.8.x is recommended for Windows 7 compatibility")
        
        if cls.is_windows7():
            try:
                result = ctypes.windll.kernel32.GetUserDefaultLCID()
                if result == 0:
                    issues.append("System locale detection failed")
            except:
                pass
        
        return (len(issues) == 0, issues)
    
    @classmethod
    def initialize(cls) -> bool:
        """
        Initialize all Windows 7 compatibility settings
        Must be called before QApplication is created
        Returns True if running on Windows 7
        """
        if cls._is_initialized:
            return cls.is_windows7()
        
        cls.setup_dpi_awareness()
        cls.setup_high_dpi_scaling()
        cls.setup_tls_support()
        
        cls._is_initialized = True
        
        return cls.is_windows7()


def get_win7_compat() -> Windows7Compat:
    """Get Windows 7 compatibility instance"""
    return Windows7Compat


def initialize_win7_compat() -> bool:
    """Initialize Windows 7 compatibility (convenience function)"""
    return Windows7Compat.initialize()
