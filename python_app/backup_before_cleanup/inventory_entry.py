
import csv
from datetime import datetime


class InventoryEntrySystem:
    def __init__(self, db):
        self.db = db
    
    def validate_inventory_data(self, data):
        errors = []
        
        required_fields = ['name', 'quantity', 'price']
        for field in required_fields:
            if not data.get(field):
                errors.append("缺少必填字段: " + field)
        
        if 'quantity' in data and data['quantity']:
            try:
                qty = float(data['quantity'])
                if qty < 0:
                    errors.append("库存数量不能为负数")
            except ValueError:
                errors.append("库存数量格式错误")
        
        if 'price' in data and data['price']:
            try:
                price = float(data['price'])
                if price < 0:
                    errors.append("价格不能为负数")
            except ValueError:
                errors.append("价格格式错误")
        
        return len(errors) == 0, errors
    
    def add_inventory_item(self, data):
        is_valid, errors = self.validate_inventory_data(data)
        
        if not is_valid:
            return False, '; '.join(errors), 0
        
        try:
            self.db.begin_transaction()
            
            existing = self.db.fetchone('SELECT id FROM medicines WHERE name = ?', (data['name'],))
            
            if existing:
                medicine_id = existing[0]
                self.db.execute('''
                    UPDATE medicines 
                    SET alias=?, category=?, nature=?, taste=?, meridian=?, 
                        efficacy=?, indications=?, usage=?, dosage=?, 
                        contraindication=?, notes=?
                    WHERE id=?
                ''', (
                    data.get('alias', ''),
                    data.get('category', ''),
                    data.get('nature', ''),
                    data.get('taste', ''),
                    data.get('meridian', ''),
                    data.get('efficacy', ''),
                    data.get('indications', ''),
                    data.get('usage', ''),
                    data.get('dosage', ''),
                    data.get('contraindication', ''),
                    data.get('notes', ''),
                    medicine_id
                ))
                
                inv_existing = self.db.fetchone('SELECT id, quantity FROM inventory WHERE medicine_id = ?', (medicine_id,))
                if inv_existing:
                    inv_id, current_qty = inv_existing
                    new_qty = current_qty + float(data.get('quantity', 0))
                    self.db.execute('''
                        UPDATE inventory 
                        SET quantity=?, price=?, min_stock=?, notes=?
                        WHERE id=?
                    ''', (
                        new_qty,
                        float(data.get('price', 0)),
                        float(data.get('min_stock', 0)),
                        data.get('notes', ''),
                        inv_id
                    ))
                else:
                    self.db.execute('''
                        INSERT INTO inventory (
                            medicine_id, quantity, unit, price, min_stock, notes
                        ) VALUES (?, ?, 'g', ?, ?, ?)
                    ''', (
                        medicine_id,
                        float(data.get('quantity', 0)),
                        float(data.get('price', 0)),
                        float(data.get('min_stock', 0)),
                        data.get('notes', '')
                    ))
            else:
                self.db.execute('''
                    INSERT INTO medicines (
                        name, alias, category, nature, taste, meridian,
                        efficacy, indications, usage, dosage, contraindication, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['name'],
                    data.get('alias', ''),
                    data.get('category', ''),
                    data.get('nature', ''),
                    data.get('taste', ''),
                    data.get('meridian', ''),
                    data.get('efficacy', ''),
                    data.get('indications', ''),
                    data.get('usage', ''),
                    data.get('dosage', ''),
                    data.get('contraindication', ''),
                    data.get('notes', '')
                ))
                
                medicine_id = self.db.cursor.lastrowid
                
                self.db.execute('''
                    INSERT INTO inventory (
                        medicine_id, quantity, unit, price, min_stock, notes
                    ) VALUES (?, ?, 'g', ?, ?, ?)
                ''', (
                    medicine_id,
                    float(data.get('quantity', 0)),
                    float(data.get('price', 0)),
                    float(data.get('min_stock', 0)),
                    data.get('notes', '')
                ))
            
            self.db.execute('''
                INSERT INTO inventory_history (
                    medicine_id, medicine_name, type, quantity, price, 
                    total_amount, operator, notes
                ) VALUES (?, ?, '入库', ?, ?, ?, ?, ?)
            ''', (
                medicine_id,
                data['name'],
                float(data.get('quantity', 0)),
                float(data.get('price', 0)),
                float(data.get('quantity', 0)) * float(data.get('price', 0)),
                '系统录入',
                data.get('notes', '')
            ))
            
            self.db.commit()
            return True, '录入成功', medicine_id
            
        except Exception as e:
            self.db.rollback()
            return False, '录入失败: ' + str(e), 0
    
    def batch_import_from_csv(self, file_path, operator='管理员'):
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors': [],
            'start_time': datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                data_list = list(reader)
            
            results['total'] = len(data_list)
            
            for idx, data in enumerate(data_list):
                row_num = idx + 1
                
                success, message, med_id = self.add_inventory_item(data)
                
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'row': row_num,
                        'name': data.get('name', '未知'),
                        'error': message
                    })
            
            results['end_time'] = datetime.now().isoformat()
            results['duration'] = (datetime.fromisoformat(results['end_time']) - 
                                   datetime.fromisoformat(results['start_time'])).total_seconds()
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results
    
    def generate_entry_report(self, results):
        report = []
        report.append('=' * 60)
        report.append('          大药房中草药库存录入报告')
        report.append('=' * 60)
        report.append('报告生成时间: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.append('')
        
        if 'start_time' in results:
            report.append('录入开始时间: ' + results["start_time"])
        if 'end_time' in results:
            report.append('录入结束时间: ' + results["end_time"])
        if 'duration' in results:
            report.append('总耗时: ' + str(round(results["duration"], 2)) + ' 秒')
        
        report.append('')
        report.append('-' * 60)
        report.append('录入统计')
        report.append('-' * 60)
        report.append('总记录数: ' + str(results.get("total", 0)))
        report.append('成功录入: ' + str(results.get("success", 0)))
        report.append('失败记录: ' + str(results.get("failed", 0)))
        
        if results.get('errors'):
            report.append('')
            report.append('-' * 60)
            report.append('错误详情')
            report.append('-' * 60)
            for err in results['errors'][:20]:
                report.append('行' + str(err.get("row", "?")) + ': ' + err.get("name", "未知") + ' - ' + err.get("error", ""))
            
            if len(results['errors']) > 20:
                report.append('... 还有 ' + str(len(results["errors"]) - 20) + ' 条错误')
        
        report.append('')
        report.append('=' * 60)
        report.append('报告结束')
        report.append('=' * 60)
        
        return '\n'.join(report)
    
    def get_inventory_template(self):
        headers = [
            'name', 'alias', 'category', 'nature', 'taste', 'meridian',
            'efficacy', 'indications', 'usage', 'dosage', 'contraindication',
            'quantity', 'unit', 'price', 'min_stock', 'notes'
        ]
        return ','.join(headers) + '\n'
    
    def get_full_inventory_list(self):
        rows = self.db.fetchall('''
            SELECT m.id, m.name, m.alias, m.category, m.nature, m.taste,
                   m.meridian, m.efficacy, m.indications, m.usage, m.dosage,
                   m.contraindication, m.notes,
                   i.quantity, i.unit, i.price, i.min_stock
            FROM medicines m
            JOIN inventory i ON m.id = i.medicine_id
            ORDER BY m.name
        ''')
        
        inventory_list = []
        for row in rows:
            inventory_list.append({
                'id': row[0],
                'name': row[1],
                'alias': row[2],
                'category': row[3],
                'nature': row[4],
                'taste': row[5],
                'meridian': row[6],
                'efficacy': row[7],
                'indications': row[8],
                'usage': row[9],
                'dosage': row[10],
                'contraindication': row[11],
                'notes': row[12],
                'quantity': row[13],
                'unit': row[14],
                'price': row[15],
                'min_stock': row[16]
            })
        
        return inventory_list
