# -*- coding: utf-8 -*-
"""
验证器 - 数据验证逻辑
"""
from typing import List, Dict, Any, Optional, Tuple
import re


class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"验证失败: {', '.join(errors)}")


class MedicineValidator:
    VALID_NATURES = ['寒', '热', '温', '凉', '平', '微寒', '微温', '大寒', '大热']
    VALID_TASTES = ['酸', '苦', '甘', '辛', '咸', '淡', '涩', '微酸', '微苦', '微甘', '微辛']
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        name = data.get('name', '').strip()
        if not name:
            errors.append("药材名称不能为空")
        elif len(name) > 50:
            errors.append("药材名称长度不能超过50个字符")
        
        category = data.get('category', '').strip()
        if not category:
            errors.append("药材分类不能为空")
        
        nature = data.get('nature', '').strip()
        if nature:
            if not cls._validate_nature(nature):
                errors.append(f"无效的药性: {nature}")
        else:
            errors.append("药性不能为空")
        
        taste = data.get('taste', '').strip()
        if taste:
            if not cls._validate_taste(taste):
                errors.append(f"无效的药味: {taste}")
        else:
            errors.append("药味不能为空")
        
        meridian = data.get('meridian', '').strip()
        if not meridian:
            errors.append("归经不能为空")
        
        efficacy = data.get('efficacy', '').strip()
        if not efficacy:
            errors.append("功效不能为空")
        
        indications = data.get('indications', '').strip()
        if not indications:
            errors.append("主治不能为空")
        
        dosage = data.get('dosage', '').strip()
        if dosage:
            if not cls._validate_dosage(dosage):
                errors.append(f"无效的用量格式: {dosage}")
        
        quantity = data.get('quantity')
        if quantity is not None:
            try:
                q = float(quantity)
                if q < 0:
                    errors.append("库存数量不能为负数")
            except (ValueError, TypeError):
                errors.append("库存数量必须是数字")
        
        price = data.get('price')
        if price is not None:
            try:
                p = float(price)
                if p < 0:
                    errors.append("价格不能为负数")
            except (ValueError, TypeError):
                errors.append("价格必须是数字")
        
        min_stock = data.get('min_stock')
        if min_stock is not None:
            try:
                m = float(min_stock)
                if m < 0:
                    errors.append("最低库存不能为负数")
            except (ValueError, TypeError):
                errors.append("最低库存必须是数字")
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_nature(cls, nature: str) -> bool:
        for valid_nature in cls.VALID_NATURES:
            if valid_nature in nature:
                return True
        return False
    
    @classmethod
    def _validate_taste(cls, taste: str) -> bool:
        tastes = re.split(r'[、,，\s]+', taste)
        for t in tastes:
            t = t.strip()
            if t and t not in cls.VALID_TASTES and not any(v in t for v in cls.VALID_TASTES):
                return False
        return True
    
    @classmethod
    def _validate_dosage(cls, dosage: str) -> bool:
        patterns = [
            r'^\d+(-\d+)?\s*[g克]?$',
            r'^\d+~\d+\s*[g克]?$',
            r'^\d+-\d+[g克]$',
        ]
        for pattern in patterns:
            if re.match(pattern, dosage):
                return True
        return False


class PrescriptionValidator:
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        patient_name = data.get('patient_name', '').strip()
        if patient_name and len(patient_name) > 50:
            errors.append("患者姓名长度不能超过50个字符")
        
        patient_age = data.get('patient_age')
        if patient_age is not None:
            try:
                age = int(patient_age)
                if age < 0 or age > 150:
                    errors.append("患者年龄必须在0-150之间")
            except (ValueError, TypeError):
                errors.append("患者年龄必须是整数")
        
        patient_gender = data.get('patient_gender', '').strip()
        if patient_gender and patient_gender not in ['男', '女', '其他', '']:
            errors.append(f"无效的性别: {patient_gender}")
        
        items = data.get('items', [])
        if not items:
            errors.append("处方必须包含至少一个药材")
        else:
            for i, item in enumerate(items):
                item_errors = cls._validate_item(item, i + 1)
                errors.extend(item_errors)
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_item(cls, item: Dict[str, Any], index: int) -> List[str]:
        errors = []
        
        medicine_name = item.get('medicine_name', '').strip()
        if not medicine_name:
            errors.append(f"第{index}项: 药材名称不能为空")
        
        quantity = item.get('quantity')
        if quantity is not None:
            try:
                q = float(quantity)
                if q <= 0:
                    errors.append(f"第{index}项: 数量必须大于0")
            except (ValueError, TypeError):
                errors.append(f"第{index}项: 数量必须是数字")
        else:
            errors.append(f"第{index}项: 数量不能为空")
        
        price = item.get('price')
        if price is not None:
            try:
                p = float(price)
                if p < 0:
                    errors.append(f"第{index}项: 价格不能为负数")
            except (ValueError, TypeError):
                errors.append(f"第{index}项: 价格必须是数字")
        
        return errors


class DataIntegrityValidator:
    @classmethod
    def validate_medicine_data(cls, data: List[Dict[str, Any]]) -> Tuple[bool, List[str], List[str]]:
        errors = []
        warnings = []
        
        names = set()
        duplicates = []
        
        for i, item in enumerate(data):
            name = item.get('name', '').strip()
            if not name:
                errors.append(f"第{i+1}项: 缺少药材名称")
                continue
            
            if name in names:
                duplicates.append(name)
            names.add(name)
            
            is_valid, item_errors = MedicineValidator.validate(item)
            if not is_valid:
                for err in item_errors:
                    errors.append(f"'{name}': {err}")
            
            required_fields = ['category', 'nature', 'taste', 'meridian', 'efficacy', 'indications']
            for field in required_fields:
                if not item.get(field, '').strip():
                    warnings.append(f"'{name}': 缺少{field}字段")
        
        if duplicates:
            errors.append(f"发现重复的药材名称: {', '.join(set(duplicates))}")
        
        return len(errors) == 0, errors, warnings
