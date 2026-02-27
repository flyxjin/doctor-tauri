import sqlite3
import os
import json
import sys


def get_app_data_dir():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(app_data, 'MedicineSystem')
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    
    return app_dir


def get_db_path():
    app_dir = get_app_data_dir()
    return os.path.join(app_dir, 'medicine_system.db')


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = get_db_path()
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
            from medicines_data_300 import medicines_300
            
            for m in medicines_300:
                self.cursor.execute('''
                    INSERT INTO medicines (name, alias, category, nature, taste, meridian, 
                                         efficacy, indications, usage, dosage, contraindication, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    m['name'],
                    m.get('alias', ''),
                    m['category'],
                    m['nature'],
                    m['taste'],
                    m['meridian'],
                    m['efficacy'],
                    m['indications'],
                    m.get('usage', ''),
                    m.get('dosage', ''),
                    m.get('contraindication', ''),
                    m.get('notes', '')
                ))
                
                medicine_id = self.cursor.lastrowid
                
                self.cursor.execute('''
                    INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    medicine_id,
                    m.get('quantity', 100),
                    m.get('unit', 'g'),
                    m.get('price', 0),
                    m.get('min_stock', 10),
                    ''
                ))
            
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
