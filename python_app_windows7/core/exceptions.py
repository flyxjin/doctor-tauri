# -*- coding: utf-8 -*-
"""
异常处理模块 - 统一的异常定义和处理
"""
from typing import Optional, List, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    DATABASE_ERROR = 100
    DATABASE_CONNECTION_FAILED = 101
    DATABASE_QUERY_FAILED = 102
    DATABASE_INTEGRITY_ERROR = 103
    VALIDATION_ERROR = 200
    VALIDATION_REQUIRED_FIELD = 201
    VALIDATION_INVALID_FORMAT = 202
    VALIDATION_OUT_OF_RANGE = 203
    VALIDATION_DUPLICATE = 204
    SERVICE_ERROR = 300
    SERVICE_NOT_FOUND = 301
    SERVICE_ALREADY_EXISTS = 302
    SERVICE_OPERATION_FAILED = 303
    INVENTORY_ERROR = 400
    INVENTORY_INSUFFICIENT = 401
    INVENTORY_NOT_FOUND = 402
    CACHE_ERROR = 500
    CACHE_NOT_INITIALIZED = 501
    CACHE_INVALID_DATA = 502


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': False,
            'error': {
                'code': self.code.value,
                'message': self.message,
                'details': self.details
            }
        }
    
    def __str__(self) -> str:
        return f"[{self.code.name}] {self.message}"


class DatabaseException(AppException):
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.DATABASE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        if original_error and details is None:
            details = {'original_error': str(original_error)}
        elif original_error:
            details['original_error'] = str(original_error)
        super().__init__(message, code, details)


class ValidationException(AppException):
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        errors: Optional[List[str]] = None
    ):
        details = {}
        if field:
            details['field'] = field
        if errors:
            details['errors'] = errors
        super().__init__(message, code, details)


class ServiceException(AppException):
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)


class InventoryException(AppException):
    def __init__(
        self,
        message: str,
        medicine_id: Optional[int] = None,
        current_quantity: Optional[float] = None,
        required_quantity: Optional[float] = None,
        code: ErrorCode = ErrorCode.INVENTORY_ERROR
    ):
        details = {}
        if medicine_id is not None:
            details['medicine_id'] = medicine_id
        if current_quantity is not None:
            details['current_quantity'] = current_quantity
        if required_quantity is not None:
            details['required_quantity'] = required_quantity
        super().__init__(message, code, details)


class CacheException(AppException):
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.CACHE_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)


class Result:
    __slots__ = ('_success', '_data', '_error', '_message')
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[AppException] = None,
        message: str = ""
    ):
        self._success = success
        self._data = data
        self._error = error
        self._message = message
    
    @classmethod
    def ok(cls, data: Any = None, message: str = "") -> 'Result':
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def fail(cls, error: AppException, message: str = "") -> 'Result':
        return cls(success=False, error=error, message=message)
    
    @classmethod
    def fail_from_exception(cls, exc: Exception) -> 'Result':
        if isinstance(exc, AppException):
            return cls(success=False, error=exc, message=exc.message)
        return cls(success=False, error=AppException(str(exc)), message=str(exc))
    
    @property
    def is_success(self) -> bool:
        return self._success
    
    @property
    def is_failure(self) -> bool:
        return not self._success
    
    @property
    def data(self) -> Any:
        return self._data
    
    @property
    def error(self) -> Optional[AppException]:
        return self._error
    
    @property
    def message(self) -> str:
        return self._message
    
    def unwrap(self) -> Any:
        if self._success:
            return self._data
        raise self._error if self._error else AppException("Unknown error")
    
    def unwrap_or(self, default: Any) -> Any:
        return self._data if self._success else default
    
    def to_dict(self) -> Dict[str, Any]:
        if self._success:
            return {
                'success': True,
                'data': self._data,
                'message': self._message
            }
        return self._error.to_dict() if self._error else {'success': False}


def handle_exception(exc: Exception) -> AppException:
    if isinstance(exc, AppException):
        return exc
    
    exc_name = type(exc).__name__
    exc_message = str(exc)
    
    if 'sqlite' in exc_name.lower() or 'database' in exc_message.lower():
        return DatabaseException(
            message=exc_message,
            original_error=exc
        )
    
    return AppException(message=exc_message, details={'type': exc_name})


def safe_execute(func, *args, **kwargs) -> Result:
    try:
        result = func(*args, **kwargs)
        return Result.ok(result)
    except Exception as e:
        return Result.fail_from_exception(e)
