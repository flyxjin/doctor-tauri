import sqlite3
import os
import json

class Database:
    def __init__(self, db_path='medicine_system.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.init_default_data()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                alias TEXT,
                category TEXT,
                nature TEXT,
                taste TEXT,
                meridian TEXT,
                efficacy TEXT,
                indications TEXT,
                usage TEXT,
                dosage TEXT,
                contraindication TEXT,
                notes TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL UNIQUE,
                quantity REAL NOT NULL DEFAULT 0,
                unit TEXT NOT NULL DEFAULT 'g',
                price REAL NOT NULL DEFAULT 0,
                min_stock REAL NOT NULL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                patient_age INTEGER,
                patient_gender TEXT,
                diagnosis TEXT,
                total_amount REAL DEFAULT 0,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescription_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL,
                total_amount REAL,
                operator TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                operator TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines (category)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id)')
        
        self.conn.commit()
    
    def init_default_data(self):
        self.cursor.execute('SELECT COUNT(*) FROM medicines')
        if self.cursor.fetchone()[0] == 0:
            default_medicines = [
                ('人参', '黄参、地精、神草', '补虚药', '温', '甘、微苦', '归脾、肺、心经', 
                 '大补元气，复脉固脱，补脾益肺，生津，安神', 
                 '体虚欲脱，肢冷脉微，脾虚食少，肺虚喘咳，津伤口渴，内热消渴，久病虚羸，惊悸失眠，阳痿宫冷', 
                 '煎服', '3-9g；挽救虚脱可用15-30g', '实证、热证而正气不虚者忌服', ''),
                ('黄芪', '黄耆', '补虚药', '微温', '甘', '归脾、肺经', 
                 '补气升阳，固表止汗，利水消肿，生津养血，行滞通痹，托毒排脓，敛疮生肌', 
                 '气虚乏力，食少便溏，中气下陷，久泻脱肛，便血崩漏，表虚自汗，气虚水肿，内热消渴，血虚萎黄，半身不遂，痹痛麻木，痈疽难溃，久溃不敛', 
                 '煎服', '9-30g', '表实邪盛，气滞湿阻，食积停滞，痈疽初起或溃后热毒尚盛等实证，以及阴虚阳亢者，均须禁服', ''),
                ('当归', '干归', '补虚药', '温', '甘、辛', '归肝、心、脾经', 
                 '补血活血，调经止痛，润肠通便', 
                 '血虚萎黄，眩晕心悸，月经不调，经闭痛经，虚寒腹痛，风湿痹痛，跌扑损伤，痈疽疮疡，肠燥便秘', 
                 '煎服', '6-12g', '湿阻中满及大便溏泄者慎服', ''),
                ('白术', '于术', '补虚药', '温', '苦、甘', '归脾、胃经', 
                 '健脾益气，燥湿利水，止汗，安胎', 
                 '脾虚食少，腹胀泄泻，痰饮眩悸，水肿，自汗，胎动不安', 
                 '煎服', '6-12g', '阴虚内热，津液亏耗者慎服', ''),
                ('茯苓', '云苓', '利水渗湿药', '平', '甘、淡', '归心、脾、肾经', 
                 '利水渗湿，健脾，宁心', 
                 '水肿尿少，痰饮眩悸，脾虚食少，便溏泄泻，心神不安，惊悸失眠', 
                 '煎服', '10-15g', '阴虚而无湿热、虚寒滑精、气虚下陷者慎服', ''),
                ('甘草', '国老', '补虚药', '平', '甘', '归心、肺、脾、胃经', 
                 '补脾益气，清热解毒，祛痰止咳，缓急止痛，调和诸药', 
                 '脾胃虚弱，倦怠乏力，心悸气短，咳嗽痰多，脘腹、四肢挛急疼痛，痈肿疮毒，缓解药物毒性、烈性', 
                 '煎服', '2-10g', '湿盛胀满，浮肿者不宜使用，不宜与海藻、京大戟、红大戟、甘遂、芫花同用', ''),
                ('金银花', '忍冬花', '清热药', '寒', '甘', '归肺、心、胃经', 
                 '清热解毒，疏散风热', 
                 '痈肿疔疮，喉痹，丹毒，热毒血痢，风热感冒，温病发热', 
                 '煎服', '6-15g', '脾胃虚寒及气虚疮疡脓清者忌服', ''),
                ('连翘', '连壳', '清热药', '微寒', '苦', '归肺、心、小肠经', 
                 '清热解毒，消肿散结，疏散风热', 
                 '痈疽，瘰疬，乳痈，丹毒，风热感冒，温病初起，温热入营，高热烦渴，神昏发斑，热淋涩痛', 
                 '煎服', '6-15g', '脾胃虚寒及气虚脓清者不宜', ''),
                ('板蓝根', '靛青根', '清热药', '寒', '苦', '归心、胃经', 
                 '清热解毒，凉血利咽', 
                 '温疫时毒，发热咽痛，温毒发斑，痄腮，烂喉丹痧，大头瘟疫，丹毒，痈肿', 
                 '煎服', '9-15g', '体虚而无实火热毒者忌服', ''),
                ('黄芩', '条芩', '清热药', '寒', '苦', '归肺、胆、脾、大肠、小肠经', 
                 '清热燥湿，泻火解毒，止血，安胎', 
                 '湿温、暑湿，胸闷呕恶，湿热痞满，泻痢，黄疸，肺热咳嗽，高热烦渴，血热吐衄，痈肿疮毒，胎动不安', 
                 '煎服', '3-10g', '脾胃虚寒者不宜使用', ''),
            ]
            
            for medicine in default_medicines:
                self.cursor.execute('''
                    INSERT INTO medicines (name, alias, category, nature, taste, meridian, 
                                         efficacy, indications, usage, dosage, contraindication, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', medicine)
            
            for i in range(1, 11):
                self.cursor.execute('''
                    INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
                    VALUES (?, ?, 'g', ?, 10, '')
                ''', (i, 100 + i * 50, 10 + i * 5))
            
            self.conn.commit()
    
    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor
    
    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def begin_transaction(self):
        self.cursor.execute('BEGIN TRANSACTION')
    
    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()
