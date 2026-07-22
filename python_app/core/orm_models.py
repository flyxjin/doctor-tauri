# -*- coding: utf-8 -*-
"""
SQLAlchemy ORM 模型层

与现有 SQLite schema 一一映射，作为 Repository 层的持久化目标。
与 core/models.py 中的 dataclass（DTO）解耦：
  - dataclass 用于业务层传递（带验证/序列化）
  - ORM 模型用于数据库交互（带关系映射）

注意：
  - 表结构由 Database._create_tables() 负责创建与迁移，ORM 层仅做映射，
    不通过 Base.metadata.create_all() 自动建表，避免重复/冲突。
  - SQLite 的 TIMESTAMP 列实际存储为 TEXT，DateTime 类型可正确处理。
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass


# 注意：schema_migrations 表由 core/migrations.py 模块自行管理（DDL + 追踪），
# 不在此处定义 ORM 映射，避免与迁移系统的 CREATE TABLE 语句冲突。


class MedicineORM(Base):
    """药材表 ORM 映射"""
    __tablename__ = 'medicines'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    alias: Mapped[Optional[str]] = mapped_column(Text, default='')
    category: Mapped[Optional[str]] = mapped_column(Text, default='')
    nature: Mapped[Optional[str]] = mapped_column(Text, default='')
    taste: Mapped[Optional[str]] = mapped_column(Text, default='')
    meridian: Mapped[Optional[str]] = mapped_column(Text, default='')
    efficacy: Mapped[Optional[str]] = mapped_column(Text, default='')
    indications: Mapped[Optional[str]] = mapped_column(Text, default='')
    usage: Mapped[Optional[str]] = mapped_column(Text, default='')
    dosage: Mapped[Optional[str]] = mapped_column(Text, default='')
    contraindication: Mapped[Optional[str]] = mapped_column(Text, default='')
    notes: Mapped[Optional[str]] = mapped_column(Text, default='')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    inventory: Mapped[Optional["InventoryORM"]] = relationship(
        back_populates='medicine', cascade='all, delete-orphan', uselist=False
    )
    prescription_items: Mapped[List["PrescriptionItemORM"]] = relationship(
        back_populates='medicine'
    )
    history: Mapped[List["InventoryHistoryORM"]] = relationship(
        back_populates='medicine'
    )

    def __repr__(self) -> str:
        return f"<MedicineORM(id={self.id}, name={self.name!r})>"


class InventoryORM(Base):
    """库存表 ORM 映射"""
    __tablename__ = 'inventory'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(Integer, ForeignKey('medicines.id', ondelete='CASCADE'),
                                              nullable=False, unique=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String, nullable=False, default='g')
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_stock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, default='')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    medicine: Mapped["MedicineORM"] = relationship(back_populates='inventory')

    def __repr__(self) -> str:
        return f"<InventoryORM(id={self.id}, medicine_id={self.medicine_id}, quantity={self.quantity})>"


class PrescriptionORM(Base):
    """处方表 ORM 映射"""
    __tablename__ = 'prescriptions'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_name: Mapped[Optional[str]] = mapped_column(Text, default='')
    patient_age: Mapped[Optional[int]] = mapped_column(Integer)
    patient_gender: Mapped[Optional[str]] = mapped_column(Text, default='')
    diagnosis: Mapped[Optional[str]] = mapped_column(Text, default='')
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_by: Mapped[Optional[str]] = mapped_column(Text, default='')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

    # 关系
    items: Mapped[List["PrescriptionItemORM"]] = relationship(
        back_populates='prescription', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"<PrescriptionORM(id={self.id}, patient_name={self.patient_name!r})>"


class PrescriptionItemORM(Base):
    """处方明细表 ORM 映射"""
    __tablename__ = 'prescription_items'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('prescriptions.id', ondelete='CASCADE'), nullable=False
    )
    medicine_id: Mapped[int] = mapped_column(Integer, ForeignKey('medicines.id'), nullable=False)
    medicine_name: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String, nullable=False, default='g')
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # 关系
    prescription: Mapped["PrescriptionORM"] = relationship(back_populates='items')
    medicine: Mapped["MedicineORM"] = relationship(back_populates='prescription_items')

    def __repr__(self) -> str:
        return f"<PrescriptionItemORM(id={self.id}, medicine_name={self.medicine_name!r})>"


class InventoryHistoryORM(Base):
    """库存变更历史表 ORM 映射"""
    __tablename__ = 'inventory_history'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(Integer, ForeignKey('medicines.id'), nullable=False)
    medicine_name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    price: Mapped[Optional[float]] = mapped_column(Float)
    total_amount: Mapped[Optional[float]] = mapped_column(Float)
    operator: Mapped[Optional[str]] = mapped_column(Text, default='')
    notes: Mapped[Optional[str]] = mapped_column(Text, default='')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

    # 关系
    medicine: Mapped["MedicineORM"] = relationship(back_populates='history')

    def __repr__(self) -> str:
        return f"<InventoryHistoryORM(id={self.id}, type={self.type!r}, quantity={self.quantity})>"


class OperationLogORM(Base):
    """操作日志表 ORM 映射"""
    __tablename__ = 'operation_logs'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_type: Mapped[str] = mapped_column(String, nullable=False)
    target_type: Mapped[str] = mapped_column(String, nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    operator: Mapped[Optional[str]] = mapped_column(Text, default='')
    details: Mapped[Optional[str]] = mapped_column(Text, default='')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<OperationLogORM(id={self.id}, op={self.operation_type!r}, target={self.target_type}:{self.target_id})>"


class DataVersionORM(Base):
    """数据版本表 ORM 映射（用于内置数据装载版本追踪）"""
    __tablename__ = 'data_version'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    medicine_count: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<DataVersionORM(id={self.id}, version={self.version!r}, count={self.medicine_count})>"


class PatientORM(Base):
    """患者档案表 ORM 映射

    注意：与 prescriptions 表通过 name 字段进行业务关联（非外键），
    因为 prescriptions.patient_name 可能存在未建档患者。

    created_at/updated_at 使用 server_default 确保新库（由 create_all 建表）
    与旧库（由迁移建表）的列默认值一致，避免插入时 NULL。
    """
    __tablename__ = 'patients'

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(Text, default='')
    age: Mapped[Optional[int]] = mapped_column(Integer)
    phone: Mapped[Optional[str]] = mapped_column(Text, default='')
    address: Mapped[Optional[str]] = mapped_column(Text, default='')
    allergy: Mapped[Optional[str]] = mapped_column(Text, default='')
    medical_history: Mapped[Optional[str]] = mapped_column(Text, default='')
    notes: Mapped[Optional[str]] = mapped_column(Text, default='')
    created_at: Mapped[Optional[str]] = mapped_column(
        Text, server_default=text("datetime('now','localtime')")
    )
    updated_at: Mapped[Optional[str]] = mapped_column(
        Text, server_default=text("datetime('now','localtime')")
    )

    def __repr__(self) -> str:
        return f"<PatientORM(id={self.id}, name={self.name!r})>"


__all__ = [
    'Base',
    'MedicineORM', 'InventoryORM', 'PrescriptionORM', 'PrescriptionItemORM',
    'InventoryHistoryORM', 'OperationLogORM', 'DataVersionORM', 'PatientORM',
]
