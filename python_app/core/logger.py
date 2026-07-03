# -*- coding: utf-8 -*-
"""
日志模块 - 操作日志记录
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
import json


def get_app_data_dir() -> str:
    if getattr(sys, 'frozen', False):
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(app_data, 'MedicineSystem')
    else:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    
    return app_dir


def get_log_dir() -> str:
    app_dir = get_app_data_dir()
    log_dir = os.path.join(app_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def get_logger(name: str = 'MedicineSystem', level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    log_dir = get_log_dir()
    log_file = os.path.join(log_dir, f'{name}.log')

    # 使用 RotatingFileHandler 防止日志文件无限增长
    # 单文件最大 10MB，保留 5 个备份
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class OperationLogger:
    def __init__(self, db=None):
        self.db = db
        self.logger = get_logger('OperationLogger')
    
    def log(self, operation_type: str, target_type: str, target_id: int, 
            details: str = '', operator: str = '', extra: dict = None):
        log_entry = {
            'operation_type': operation_type,
            'target_type': target_type,
            'target_id': target_id,
            'details': details,
            'operator': operator,
            'extra': extra or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        if self.db:
            try:
                query = '''
                    INSERT INTO operation_logs (operation_type, target_type, target_id, operator, details)
                    VALUES (?, ?, ?, ?, ?)
                '''
                self.db.execute(query, (operation_type, target_type, target_id, operator, details))
            except Exception as e:
                self.logger.error(f"写入操作日志到数据库失败: {e}")
    
    def log_medicine_create(self, medicine_id: int, medicine_name: str, operator: str = ''):
        self.log('CREATE', 'medicine', medicine_id, f"创建药材: {medicine_name}", operator)
    
    def log_medicine_update(self, medicine_id: int, medicine_name: str, changes: dict, operator: str = ''):
        details = f"更新药材: {medicine_name}, 变更: {json.dumps(changes, ensure_ascii=False)}"
        self.log('UPDATE', 'medicine', medicine_id, details, operator)
    
    def log_medicine_delete(self, medicine_id: int, medicine_name: str, operator: str = ''):
        self.log('DELETE', 'medicine', medicine_id, f"删除药材: {medicine_name}", operator)
    
    def log_prescription_create(self, prescription_id: int, patient_name: str, 
                                 total_amount: float, operator: str = ''):
        details = f"创建处方: 患者 {patient_name}, 金额 {total_amount:.2f}"
        self.log('CREATE', 'prescription', prescription_id, details, operator)
    
    def log_prescription_delete(self, prescription_id: int, patient_name: str, operator: str = ''):
        self.log('DELETE', 'prescription', prescription_id, f"删除处方: 患者 {patient_name}", operator)
    
    def log_inventory_change(self, medicine_id: int, medicine_name: str, 
                              change_type: str, quantity: float, operator: str = ''):
        details = f"库存{change_type}: {medicine_name}, 数量: {quantity}"
        self.log(change_type, 'inventory', medicine_id, details, operator)
    
    def log_data_import(self, count: int, source: str = 'builtin', operator: str = ''):
        details = f"导入数据: {count}条, 来源: {source}"
        self.log('IMPORT', 'data', 0, details, operator)
    
    def log_data_backup(self, backup_path: str, operator: str = ''):
        details = f"数据备份: {backup_path}"
        self.log('BACKUP', 'data', 0, details, operator)
    
    def log_error(self, error_type: str, error_message: str, context: dict = None):
        details = f"错误: {error_type} - {error_message}"
        extra = {'context': context} if context else None
        self.log('ERROR', 'system', 0, details, extra=extra)
        self.logger.error(f"{error_type}: {error_message}")


class DataLogger:
    def __init__(self):
        self.logger = get_logger('DataLogger')
    
    def log_data_load(self, source: str, count: int, duration: float = None):
        msg = f"数据加载: 来源={source}, 数量={count}"
        if duration:
            msg += f", 耗时={duration:.2f}秒"
        self.logger.info(msg)
    
    def log_data_save(self, target: str, count: int = None):
        msg = f"数据保存: 目标={target}"
        if count is not None:
            msg += f", 数量={count}"
        self.logger.info(msg)
    
    def log_data_validation(self, total: int, valid: int, invalid: int):
        self.logger.info(f"数据验证: 总数={total}, 有效={valid}, 无效={invalid}")
    
    def log_integrity_check(self, passed: bool, errors: list):
        if passed:
            self.logger.info("数据完整性检查通过")
        else:
            self.logger.warning(f"数据完整性检查失败: {len(errors)}个问题")
            for error in errors:
                self.logger.warning(f"  - {error}")


_app_logger = None
_operation_logger = None
_data_logger = None


def get_app_logger() -> logging.Logger:
    global _app_logger
    if _app_logger is None:
        _app_logger = get_logger('MedicineSystem')
    return _app_logger


def get_operation_logger(db=None) -> OperationLogger:
    global _operation_logger
    if _operation_logger is None or (_operation_logger.db is None and db is not None):
        _operation_logger = OperationLogger(db)
    return _operation_logger


def get_data_logger() -> DataLogger:
    global _data_logger
    if _data_logger is None:
        _data_logger = DataLogger()
    return _data_logger
