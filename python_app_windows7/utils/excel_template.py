# -*- coding: utf-8 -*-
"""
Excel模板生成器 - Windows 7兼容版本
生成标准化的药材导入Excel模板文件
"""
import os
import csv
from datetime import datetime
from typing import List, Dict, Any

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class ExcelTemplateGenerator:
    """Excel模板生成器"""
    
    HEADERS = [
        {'name': 'name', 'label': '药材名称', 'required': True, 'type': 'text', 'width': 15,
         'description': '必填，药材的正式名称'},
        {'name': 'alias', 'label': '别名', 'required': False, 'type': 'text', 'width': 12,
         'description': '药材的别名或俗称'},
        {'name': 'category', 'label': '分类', 'required': False, 'type': 'text', 'width': 10,
         'description': '如：补虚药、清热药、泻下药等'},
        {'name': 'nature', 'label': '药性', 'required': False, 'type': 'text', 'width': 8,
         'description': '寒、热、温、凉、平'},
        {'name': 'taste', 'label': '药味', 'required': False, 'type': 'text', 'width': 10,
         'description': '酸、苦、甘、辛、咸、淡、涩'},
        {'name': 'meridian', 'label': '归经', 'required': False, 'type': 'text', 'width': 15,
         'description': '如：归脾、肺、心经'},
        {'name': 'efficacy', 'label': '功效', 'required': False, 'type': 'text', 'width': 25,
         'description': '药材的主要功效'},
        {'name': 'indications', 'label': '主治', 'required': False, 'type': 'text', 'width': 25,
         'description': '主要治疗的疾病或症状'},
        {'name': 'usage', 'label': '用法', 'required': False, 'type': 'text', 'width': 10,
         'description': '如：煎服、研末、外用'},
        {'name': 'dosage', 'label': '用量', 'required': False, 'type': 'text', 'width': 10,
         'description': '如：3-9g'},
        {'name': 'contraindication', 'label': '禁忌', 'required': False, 'type': 'text', 'width': 20,
         'description': '使用禁忌和注意事项'},
        {'name': 'notes', 'label': '备注', 'required': False, 'type': 'text', 'width': 20,
         'description': '其他补充说明'},
        {'name': 'quantity', 'label': '库存数量', 'required': False, 'type': 'number', 'width': 10,
         'description': '数值，单位默认为克(g)'},
        {'name': 'unit', 'label': '单位', 'required': False, 'type': 'text', 'width': 6,
         'description': '默认为g'},
        {'name': 'price', 'label': '单价(元)', 'required': False, 'type': 'number', 'width': 10,
         'description': '数值，每克价格'},
        {'name': 'min_stock', 'label': '最低库存', 'required': False, 'type': 'number', 'width': 10,
         'description': '数值，库存预警阈值'},
    ]
    
    SAMPLE_DATA = [
        {
            'name': '人参',
            'alias': '黄参、地精',
            'category': '补虚药',
            'nature': '温',
            'taste': '甘、微苦',
            'meridian': '归脾、肺、心经',
            'efficacy': '大补元气、复脉固脱、补脾益肺、生津养血、安神益智',
            'indications': '体虚欲脱、肢冷脉微、脾虚食少、肺虚喘咳、津伤口渴',
            'usage': '煎服',
            'dosage': '3-9g',
            'contraindication': '实证、热证忌服',
            'notes': '不宜与藜芦同用',
            'quantity': 500,
            'unit': 'g',
            'price': 85.00,
            'min_stock': 50
        },
        {
            'name': '黄芪',
            'alias': '黄耆',
            'category': '补虚药',
            'nature': '微温',
            'taste': '甘',
            'meridian': '归脾、肺经',
            'efficacy': '补气升阳、固表止汗、利水消肿、生津养血',
            'indications': '气虚乏力、食少便溏、中气下陷、久泻脱肛',
            'usage': '煎服',
            'dosage': '9-30g',
            'contraindication': '实证禁服',
            'notes': '',
            'quantity': 600,
            'unit': 'g',
            'price': 42.00,
            'min_stock': 60
        },
        {
            'name': '当归',
            'alias': '秦归、云归',
            'category': '补血药',
            'nature': '温',
            'taste': '甘、辛',
            'meridian': '归肝、心、脾经',
            'efficacy': '补血活血、调经止痛、润肠通便',
            'indications': '血虚萎黄、眩晕心悸、月经不调、经闭痛经',
            'usage': '煎服',
            'dosage': '6-12g',
            'contraindication': '湿盛中满者慎服',
            'notes': '',
            'quantity': 400,
            'unit': 'g',
            'price': 56.00,
            'min_stock': 40
        },
    ]
    
    @classmethod
    def generate_excel_template(cls, filepath: str) -> bool:
        """生成Excel模板文件"""
        if not HAS_OPENPYXL:
            return False
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = '药材导入模板'
            
            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF', size=11)
            required_fill = PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid')
            required_font = Font(bold=True, color='FFFFFF', size=11)
            
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for col_idx, header in enumerate(cls.HEADERS, 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.value = header['label']
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                
                if header['required']:
                    cell.fill = required_fill
                    cell.font = required_font
                else:
                    cell.fill = header_fill
                    cell.font = header_font
                
                ws.column_dimensions[get_column_letter(col_idx)].width = header['width']
            
            for row_idx, sample in enumerate(cls.SAMPLE_DATA, 2):
                for col_idx, header in enumerate(cls.HEADERS, 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    value = sample.get(header['name'], '')
                    cell.value = value
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = thin_border
            
            ws.row_dimensions[1].height = 25
            
            ws_desc = wb.create_sheet(title='字段说明')
            ws_desc.cell(row=1, column=1, value='字段名称')
            ws_desc.cell(row=1, column=2, value='是否必填')
            ws_desc.cell(row=1, column=3, value='数据类型')
            ws_desc.cell(row=1, column=4, value='说明')
            
            for col in range(1, 5):
                cell = ws_desc.cell(row=1, column=col)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
            
            for row_idx, header in enumerate(cls.HEADERS, 2):
                ws_desc.cell(row=row_idx, column=1, value=header['label'])
                ws_desc.cell(row=row_idx, column=2, value='是' if header['required'] else '否')
                ws_desc.cell(row=row_idx, column=3, value='数值' if header['type'] == 'number' else '文本')
                ws_desc.cell(row=row_idx, column=4, value=header['description'])
            
            ws_desc.column_dimensions['A'].width = 12
            ws_desc.column_dimensions['B'].width = 10
            ws_desc.column_dimensions['C'].width = 10
            ws_desc.column_dimensions['D'].width = 40
            
            wb.save(filepath)
            return True
            
        except Exception as e:
            print(f"生成Excel模板失败: {e}")
            return False
    
    @classmethod
    def generate_csv_template(cls, filepath: str) -> bool:
        """生成CSV模板文件"""
        try:
            headers = [h['name'] for h in cls.HEADERS]
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for sample in cls.SAMPLE_DATA:
                    row = [sample.get(h['name'], '') for h in cls.HEADERS]
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"生成CSV模板失败: {e}")
            return False
    
    @classmethod
    def get_field_descriptions(cls) -> List[Dict[str, Any]]:
        """获取字段描述列表"""
        return cls.HEADERS.copy()


class DataValidator:
    """数据验证器"""
    
    VALID_NATURES = ['寒', '热', '温', '凉', '平', '']
    VALID_TASTES = ['酸', '苦', '甘', '辛', '咸', '淡', '涩', '']
    
    @classmethod
    def validate_row(cls, row_data: Dict[str, Any], row_num: int) -> List[str]:
        """验证单行数据"""
        errors = []
        
        name = str(row_data.get('name', '')).strip()
        if not name:
            errors.append(f"第{row_num}行: 药材名称不能为空")
        elif len(name) > 50:
            errors.append(f"第{row_num}行: 药材名称过长（最多50字符）")
        
        nature = str(row_data.get('nature', '')).strip()
        if nature and nature not in cls.VALID_NATURES:
            errors.append(f"第{row_num}行: 药性'{nature}'无效，应为：寒/热/温/凉/平")
        
        quantity = row_data.get('quantity')
        if quantity is not None:
            try:
                qty = float(quantity)
                if qty < 0:
                    errors.append(f"第{row_num}行: 库存数量不能为负数")
            except (ValueError, TypeError):
                errors.append(f"第{row_num}行: 库存数量'{quantity}'不是有效数字")
        
        price = row_data.get('price')
        if price is not None:
            try:
                p = float(price)
                if p < 0:
                    errors.append(f"第{row_num}行: 单价不能为负数")
            except (ValueError, TypeError):
                errors.append(f"第{row_num}行: 单价'{price}'不是有效数字")
        
        min_stock = row_data.get('min_stock')
        if min_stock is not None:
            try:
                ms = float(min_stock)
                if ms < 0:
                    errors.append(f"第{row_num}行: 最低库存不能为负数")
            except (ValueError, TypeError):
                errors.append(f"第{row_num}行: 最低库存'{min_stock}'不是有效数字")
        
        return errors
    
    @classmethod
    def validate_all(cls, data_list: List[Dict[str, Any]]) -> tuple:
        """验证所有数据"""
        all_errors = []
        valid_data = []
        
        for i, row_data in enumerate(data_list, 1):
            errors = cls.validate_row(row_data, i)
            if errors:
                all_errors.extend(errors)
            else:
                valid_data.append(row_data)
        
        return valid_data, all_errors
