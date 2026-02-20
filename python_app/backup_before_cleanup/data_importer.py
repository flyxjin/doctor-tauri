
import json
import csv
import re


class DataValidator:
    REQUIRED_FIELDS = ['name']
    
    VALID_NATURES = ['寒', '热', '温', '凉', '平']
    VALID_TASTES = ['酸', '苦', '甘', '辛', '咸', '淡', '涩']
    
    @staticmethod
    def validate_name(name):
        if not name or not name.strip():
            return False, '药材名称不能为空'
        if len(name) &gt; 100:
            return False, '药材名称过长'
        return True, ''
    
    @staticmethod
    def validate_nature(nature):
        if not nature:
            return True, ''
        nature = nature.strip()
        if nature not in DataValidator.VALID_NATURES:
            return False, '药性必须是: 寒、热、温、凉、平'
        return True, ''
    
    @staticmethod
    def validate_taste(taste):
        if not taste:
            return True, ''
        tastes = [t.strip() for t in re.split('[、,，]', taste) if t.strip()]
        for t in tastes:
            if t not in DataValidator.VALID_TASTES:
                return False, '药味无效，必须是: 酸、苦、甘、辛、咸、淡、涩'
        return True, ''
    
    @staticmethod
    def standardize_name(name):
        name = name.strip()
        name = re.sub(r'\s+', ' ', name)
        return name
    
    @staticmethod
    def clean_text(text):
        if not text:
            return ''
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text


class DataImporter:
    def __init__(self, db):
        self.db = db
        self.validator = DataValidator()
    
    def import_from_csv(self, file_path, task_name, 
                        progress_callback=None,
                        skip_existing=True):
        return self._import_file(file_path, task_name, 'csv', 
                                progress_callback, skip_existing)
    
    def import_from_json(self, file_path, task_name,
                        progress_callback=None,
                        skip_existing=True):
        return self._import_file(file_path, task_name, 'json',
                                progress_callback, skip_existing)
    
    def _import_file(self, file_path, task_name, source_type,
                    progress_callback, skip_existing):
        data_list = self._read_file(file_path, source_type)
        total_count = len(data_list)
        
        task_id = self.db.create_import_task(task_name, source_type, file_path, total_count)
        
        success_count = 0
        failed_count = 0
        errors = []
        
        try:
            self.db.begin_transaction()
            
            for idx, item in enumerate(data_list):
                row_num = idx + 1
                
                try:
                    result = self._process_item(item, row_num, task_id, skip_existing)
                    if result['success']:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(result)
                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    self.db.add_import_log(task_id, row_num, 
                                         item.get('name', '未知'), 'error', 
                                         error_msg, item)
                    errors.append({
                        'row': row_num,
                        'name': item.get('name', '未知'),
                        'error': error_msg
                    })
                
                if progress_callback:
                    progress_callback(idx + 1, total_count, success_count, failed_count)
                
                if (idx + 1) % 100 == 0:
                    self.db.update_import_task(task_id, idx + 1, success_count, failed_count)
            
            self.db.commit()
            self.db.complete_import_task(task_id, success_count, failed_count)
            
            return {
                'success': True,
                'task_id': task_id,
                'total': total_count,
                'success_count': success_count,
                'failed_count': failed_count,
                'errors': errors
            }
            
        except Exception as e:
            self.db.rollback()
            self.db.update_import_task(task_id, status='failed')
            raise
    
    def _read_file(self, file_path, source_type):
        if source_type == 'csv':
            return self._read_csv(file_path)
        elif source_type == 'json':
            return self._read_json(file_path)
        else:
            raise ValueError('不支持的文件类型')
    
    def _read_csv(self, file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(self._normalize_row(row))
        return data
    
    def _read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'data' in data:
                data = data['data']
            return [self._normalize_row(item) for item in data]
    
    def _normalize_row(self, row):
        key_mapping = {
            '药材名称': 'name',
            '名称': 'name',
            '别名': 'alias',
            '分类': 'category',
            '类别': 'category',
            '药性': 'nature',
            '四气': 'nature',
            '药味': 'taste',
            '五味': 'taste',
            '归经': 'meridian',
            '功效': 'efficacy',
            '功能': 'efficacy',
            '主治': 'indications',
            '主治病症': 'indications',
            '用法': 'usage',
            '用量': 'dosage',
            '用法用量': 'dosage',
            '禁忌': 'contraindication',
            '注意事项': 'contraindication',
            '备注': 'notes',
            '来源': 'source'
        }
        
        normalized = {}
        for key, value in row.items():
            new_key = key_mapping.get(key, key)
            normalized[new_key] = value
        return normalized
    
    def _process_item(self, item, row_num, task_id, skip_existing):
        name = item.get('name', '')
        
        name_valid, name_error = self.validator.validate_name(name)
        if not name_valid:
            self.db.add_import_log(task_id, row_num, name, 'error', name_error, item)
            return {'success': False, 'row': row_num, 'name': name, 'error': name_error}
        
        standardized_name = self.validator.standardize_name(name)
        
        if skip_existing:
            existing = self.db.fetchone('SELECT id FROM medicines WHERE name = ?', (standardized_name,))
            if existing:
                self.db.add_import_log(task_id, row_num, standardized_name, 'skipped', '药材已存在', item)
                return {'success': True, 'row': row_num, 'name': standardized_name, 'skipped': True}
        
        try:
            self.db.execute('''
                INSERT INTO medicines (
                    name, alias, category, nature, taste, meridian, 
                    efficacy, indications, usage, dosage, contraindication, 
                    notes, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                standardized_name,
                self.validator.clean_text(item.get('alias', '')),
                self.validator.clean_text(item.get('category', '')),
                self.validator.clean_text(item.get('nature', '')),
                self.validator.clean_text(item.get('taste', '')),
                self.validator.clean_text(item.get('meridian', '')),
                self.validator.clean_text(item.get('efficacy', '')),
                self.validator.clean_text(item.get('indications', '')),
                self.validator.clean_text(item.get('usage', '')),
                self.validator.clean_text(item.get('dosage', '')),
                self.validator.clean_text(item.get('contraindication', '')),
                self.validator.clean_text(item.get('notes', '')),
                self.validator.clean_text(item.get('source', ''))
            ))
            
            med_id = self.db.cursor.lastrowid
            
            price = float(item.get('price', 10)) if item.get('price') else 10
            quantity = float(item.get('quantity', 0)) if item.get('quantity') else 0
            min_stock = float(item.get('min_stock', 10)) if item.get('min_stock') else 10
            
            self.db.execute('''
                INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock)
                VALUES (?, ?, 'g', ?, ?)
            ''', (med_id, quantity, price, min_stock))
            
            self.db.add_import_log(task_id, row_num, standardized_name, 'success', None, item)
            return {'success': True, 'row': row_num, 'name': standardized_name}
            
        except Exception as e:
            error_msg = str(e)
            self.db.add_import_log(task_id, row_num, standardized_name, 'error', error_msg, item)
            return {'success': False, 'row': row_num, 'name': standardized_name, 'error': error_msg}
    
    def get_template_csv(self):
        headers = [
            'name', 'alias', 'category', 'nature', 'taste', 'meridian',
            'efficacy', 'indications', 'usage', 'dosage', 'contraindication',
            'notes', 'source', 'price', 'quantity', 'min_stock'
        ]
        return ','.join(headers) + '\n'

