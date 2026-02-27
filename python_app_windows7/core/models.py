# -*- coding: utf-8 -*-
"""
模型层 - 数据模型定义
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Medicine:
    name: str
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
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            alias=data.get('alias', ''),
            category=data.get('category', ''),
            nature=data.get('nature', ''),
            taste=data.get('taste', ''),
            meridian=data.get('meridian', ''),
            efficacy=data.get('efficacy', ''),
            indications=data.get('indications', ''),
            usage=data.get('usage', ''),
            dosage=data.get('dosage', ''),
            contraindication=data.get('contraindication', ''),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def validate(self) -> List[str]:
        errors = []
        if not self.name:
            errors.append("药材名称不能为空")
        if not self.category:
            errors.append("药材分类不能为空")
        if not self.nature:
            errors.append("药性不能为空")
        if not self.taste:
            errors.append("药味不能为空")
        if not self.meridian:
            errors.append("归经不能为空")
        if not self.efficacy:
            errors.append("功效不能为空")
        if not self.indications:
            errors.append("主治不能为空")
        return errors


@dataclass
class Inventory:
    medicine_id: int
    quantity: float = 0.0
    unit: str = "g"
    price: float = 0.0
    min_stock: float = 0.0
    notes: str = ""
    id: Optional[int] = None
    medicine_name: str = ""
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
        return cls(
            id=data.get('id'),
            medicine_id=data.get('medicine_id', 0),
            quantity=data.get('quantity', 0.0),
            unit=data.get('unit', 'g'),
            price=data.get('price', 0.0),
            min_stock=data.get('min_stock', 0.0),
            notes=data.get('notes', ''),
            medicine_name=data.get('medicine_name', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def is_low_stock(self) -> bool:
        return self.quantity <= self.min_stock
    
    def get_value(self) -> float:
        return self.quantity * self.price


@dataclass
class Prescription:
    patient_name: str = ""
    patient_age: Optional[int] = None
    patient_gender: str = ""
    diagnosis: str = ""
    total_amount: float = 0.0
    created_by: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    items: List['PrescriptionItem'] = field(default_factory=list)
    
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
        return cls(
            id=data.get('id'),
            patient_name=data.get('patient_name', ''),
            patient_age=data.get('patient_age'),
            patient_gender=data.get('patient_gender', ''),
            diagnosis=data.get('diagnosis', ''),
            total_amount=data.get('total_amount', 0.0),
            created_by=data.get('created_by', ''),
            created_at=data.get('created_at')
        )
    
    def calculate_total(self) -> float:
        return sum(item.amount for item in self.items)


@dataclass
class PrescriptionItem:
    prescription_id: int
    medicine_id: int
    medicine_name: str
    quantity: float
    unit: str
    price: float
    amount: float
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
        return cls(
            id=data.get('id'),
            prescription_id=data.get('prescription_id', 0),
            medicine_id=data.get('medicine_id', 0),
            medicine_name=data.get('medicine_name', ''),
            quantity=data.get('quantity', 0.0),
            unit=data.get('unit', 'g'),
            price=data.get('price', 0.0),
            amount=data.get('amount', 0.0)
        )


@dataclass
class InventoryHistory:
    medicine_id: int
    medicine_name: str
    type: str
    quantity: float
    price: Optional[float] = None
    total_amount: Optional[float] = None
    operator: str = ""
    notes: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InventoryHistory':
        return cls(
            id=data.get('id'),
            medicine_id=data.get('medicine_id', 0),
            medicine_name=data.get('medicine_name', ''),
            type=data.get('type', ''),
            quantity=data.get('quantity', 0.0),
            price=data.get('price'),
            total_amount=data.get('total_amount'),
            operator=data.get('operator', ''),
            notes=data.get('notes', ''),
            created_at=data.get('created_at')
        )


@dataclass
class OperationLog:
    operation_type: str
    target_type: str
    target_id: int
    operator: str = ""
    details: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OperationLog':
        return cls(
            id=data.get('id'),
            operation_type=data.get('operation_type', ''),
            target_type=data.get('target_type', ''),
            target_id=data.get('target_id', 0),
            operator=data.get('operator', ''),
            details=data.get('details', ''),
            created_at=data.get('created_at')
        )
