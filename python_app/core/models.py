# -*- coding: utf-8 -*-
"""
模型层 - 数据模型定义

基于 Pydantic v2 BaseModel，提供自动验证、序列化和 JSON Schema 支持。
所有模型保持与原 dataclass 版本兼容的属性访问、to_dict() / from_dict() 接口。
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Medicine(BaseModel):
    """药材数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    name: str = ""
    alias: str = ""
    category: str = ""
    nature: str = ""
    taste: str = ""
    meridian: str = ""
    efficacy: str = ""
    indications: str = ""
    usage: str = ""
    dosage: str = ""
    contraindication: str = ""
    notes: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'alias': self.alias,
            'category': self.category,
            'nature': self.nature,
            'taste': self.taste,
            'meridian': self.meridian,
            'efficacy': self.efficacy,
            'indications': self.indications,
            'usage': self.usage,
            'dosage': self.dosage,
            'contraindication': self.contraindication,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Medicine':
        return cls.model_validate(data)

    def validate_fields(self) -> List[str]:
        errors = []
        if not self.name or not self.name.strip():
            errors.append("药材名称不能为空")
        return errors


class Inventory(BaseModel):
    """库存数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    medicine_id: int = 0
    quantity: float = 0.0
    unit: str = "g"
    price: float = 0.0
    min_stock: float = 0.0
    notes: str = ""
    id: Optional[int] = None
    medicine_name: str = ""
    category: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'quantity': self.quantity,
            'unit': self.unit,
            'price': self.price,
            'min_stock': self.min_stock,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Inventory':
        return cls.model_validate(data)

    def is_low_stock(self) -> bool:
        return self.quantity <= self.min_stock

    def get_value(self) -> float:
        return self.quantity * self.price


class Prescription(BaseModel):
    """处方数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    patient_name: str = ""
    patient_age: Optional[int] = None
    patient_gender: str = ""
    diagnosis: str = ""
    total_amount: float = 0.0
    created_by: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    items: List['PrescriptionItem'] = Field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'patient_age': self.patient_age,
            'patient_gender': self.patient_gender,
            'diagnosis': self.diagnosis,
            'total_amount': self.total_amount,
            'created_by': self.created_by,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Prescription':
        return cls.model_validate(data)

    def calculate_total(self) -> float:
        return sum(item.amount for item in self.items)


class PrescriptionItem(BaseModel):
    """处方明细数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    prescription_id: int = 0
    medicine_id: int = 0
    medicine_name: str = ""
    quantity: float = 0.0
    unit: str = "g"
    price: float = 0.0
    amount: float = 0.0
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'prescription_id': self.prescription_id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'price': self.price,
            'amount': self.amount
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PrescriptionItem':
        return cls.model_validate(data)


class InventoryHistory(BaseModel):
    """库存变更历史数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    medicine_id: int = 0
    medicine_name: str = ""
    type: str = ""
    quantity: float = 0.0
    price: Optional[float] = None
    total_amount: Optional[float] = None
    operator: str = ""
    notes: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'InventoryHistory':
        return cls.model_validate(data)


class OperationLog(BaseModel):
    """操作日志数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    operation_type: str = ""
    target_type: str = ""
    target_id: int = 0
    operator: str = ""
    details: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'OperationLog':
        return cls.model_validate(data)


class Patient(BaseModel):
    """患者档案数据模型"""
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    id: Optional[int] = None
    name: str = ""
    gender: Optional[str] = ""
    age: Optional[int] = None
    phone: Optional[str] = ""
    address: Optional[str] = ""
    allergy: Optional[str] = ""
    medical_history: Optional[str] = ""
    notes: Optional[str] = ""
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender or "",
            'age': self.age,
            'phone': self.phone or "",
            'address': self.address or "",
            'allergy': self.allergy or "",
            'medical_history': self.medical_history or "",
            'notes': self.notes or "",
            'created_at': self.created_at or "",
            'updated_at': self.updated_at or "",
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Patient':
        # 旧库新增列的值为 NULL，统一转为空串避免 Pydantic 校验失败
        nullable_str_fields = ('gender', 'phone', 'address', 'allergy',
                               'medical_history', 'notes', 'created_at', 'updated_at')
        sanitized = dict(data)
        for field in nullable_str_fields:
            if sanitized.get(field) is None:
                sanitized[field] = ""
        return cls.model_validate(sanitized)

    def validate_fields(self) -> List[str]:
        errors = []
        if not self.name or not self.name.strip():
            errors.append("患者姓名不能为空")
        if self.age is not None and (self.age < 0 or self.age > 150):
            errors.append("患者年龄不合法")
        if self.gender and self.gender not in ('男', '女'):
            errors.append("性别只能为'男'或'女'")
        return errors


# 解析 Prescription.items 中的前向引用（PrescriptionItem 在 Prescription 之后定义）
Prescription.model_rebuild()
