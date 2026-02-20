const initSqlJs = require('sql.js');
const fs = require('fs');
const path = require('path');

// 确定数据库文件路径，适配pkg打包环境
let dbPath;
if (process.pkg) {
  // 在pkg打包环境中，使用当前工作目录
  dbPath = path.join(process.cwd(), 'database.db');
} else {
  // 在开发环境中，使用相对路径
  dbPath = path.resolve(__dirname, '../../database.db');
}

console.log(`数据库文件路径: ${dbPath}`);

let db;
let SQL;

// 初始化数据库连接
async function initializeDB() {
  try {
    SQL = await initSqlJs({
      locateFile: file => path.resolve(__dirname, '../node_modules/sql.js/dist/', file)
    });
    
    let dbBuffer;
    try {
      // 尝试读取现有数据库文件
      dbBuffer = fs.readFileSync(dbPath);
      db = new SQL.Database(dbBuffer);
    } catch (error) {
      // 如果文件不存在，创建新数据库
      db = new SQL.Database();
      // 保存新数据库到文件
      const data = db.export();
      const buffer = Buffer.from(data);
      fs.writeFileSync(dbPath, buffer);
    }
    
    console.log('数据库连接成功');
    
    // 初始化数据库表结构
    await initDatabase();
    
    return db;
  } catch (error) {
    console.error('数据库初始化失败:', error.message);
    throw error;
  }
}

// 保存数据库更改
function saveDB() {
  if (db) {
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(dbPath, buffer);
    console.log('数据库已保存');
  }
}

// 初始化数据库表结构
async function initDatabase() {
  try {
    // 创建中药材表
    const createMedicinesTable = `
    CREATE TABLE IF NOT EXISTS medicines (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      nature TEXT,
      taste TEXT,
      meridian TEXT,
      efficacy TEXT,
      usage TEXT,
      dosage TEXT,
      禁忌症 TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    `;
    
    // 创建处方表
    const createPrescriptionsTable = `
    CREATE TABLE IF NOT EXISTS prescriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient_name TEXT,
      patient_age INTEGER,
      patient_gender TEXT,
      diagnosis TEXT,
      total_amount REAL DEFAULT 0,
      created_by TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    `;
    
    // 创建处方明细表
    const createPrescriptionItemsTable = `
    CREATE TABLE IF NOT EXISTS prescription_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      prescription_id INTEGER NOT NULL,
      medicine_id INTEGER NOT NULL,
      quantity REAL NOT NULL,
      unit TEXT NOT NULL,
      price REAL NOT NULL,
      amount REAL NOT NULL,
      FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
    );
    `;
    
    // 创建库存表
    const createInventoryTable = `
    CREATE TABLE IF NOT EXISTS inventory (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      medicine_id INTEGER NOT NULL UNIQUE,
      quantity REAL NOT NULL DEFAULT 0,
      unit TEXT NOT NULL,
      price REAL NOT NULL,
      min_stock REAL NOT NULL DEFAULT 10,
      last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    );
    `;
    
    // 创建库存变动历史表
    const createInventoryHistoryTable = `
    CREATE TABLE IF NOT EXISTS inventory_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      medicine_id INTEGER NOT NULL,
      type TEXT NOT NULL,
      quantity REAL NOT NULL,
      price REAL,
      total_amount REAL,
      operator TEXT,
      notes TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    );
    `;
    
    // 执行创建表的SQL语句
    db.run(createMedicinesTable);
    db.run(createPrescriptionsTable);
    db.run(createPrescriptionItemsTable);
    db.run(createInventoryTable);
    db.run(createInventoryHistoryTable);
    
    console.log('数据库表结构初始化完成');
    
    // 插入初始数据
    await insertInitialData();
    
  } catch (error) {
    console.error('初始化数据库表结构失败:', error.message);
  }
}

// 插入初始数据
async function insertInitialData() {
  try {
    // 检查是否已有数据
    const result = db.exec('SELECT COUNT(*) as count FROM medicines');
    
    if (result && result[0] && result[0].values && result[0].values[0][0] === 0) {
      // 插入初始中药材数据
      const medicines = [
        {
          name: '人参',
          nature: '温',
          taste: '甘、微苦',
          meridian: '归脾、肺、心经',
          efficacy: '大补元气，复脉固脱，益精，安神',
          usage: '煎服',
          dosage: '3-9g',
          禁忌症: '实证、热证而正气不虚者忌服'
        },
        {
          name: '黄芪',
          nature: '微温',
          taste: '甘',
          meridian: '归脾、肺经',
          efficacy: '补气升阳，固表止汗，利水消肿，生肌',
          usage: '煎服',
          dosage: '9-30g',
          禁忌症: '表实邪盛，气滞湿阻，食积停滞者忌服'
        },
        {
          name: '当归',
          nature: '温',
          taste: '甘、辛',
          meridian: '归肝、心、脾经',
          efficacy: '补血活血，调经止痛，润肠通便',
          usage: '煎服',
          dosage: '3-10g',
          禁忌症: '湿阻中满及大便溏泄者慎服'
        }
      ];
      
      // 插入中药材数据
      medicines.forEach(medicine => {
        const sql = `
        INSERT INTO medicines (name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `;
        db.run(sql, [
          medicine.name,
          medicine.nature,
          medicine.taste,
          medicine.meridian,
          medicine.efficacy,
          medicine.usage,
          medicine.dosage,
          medicine.禁忌症
        ]);
      });
      
      // 插入初始库存数据
      const inventoryData = [
        { medicine_id: 1, quantity: 100, unit: 'g', price: 10, min_stock: 10 },
        { medicine_id: 2, quantity: 200, unit: 'g', price: 5, min_stock: 10 },
        { medicine_id: 3, quantity: 150, unit: 'g', price: 8, min_stock: 10 }
      ];
      
      inventoryData.forEach(item => {
        const sql = `
        INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock)
        VALUES (?, ?, ?, ?, ?)
        `;
        db.run(sql, [
          item.medicine_id,
          item.quantity,
          item.unit,
          item.price,
          item.min_stock
        ]);
      });
      
      console.log('初始数据插入完成');
      
      // 保存数据库更改
      saveDB();
    }
  } catch (error) {
    console.error('插入初始数据失败:', error.message);
  }
}

// 封装查询方法
const dbWrapper = {
  // 执行查询，返回所有结果
  all: (sql, params = []) => {
    try {
      const result = db.exec(sql, {
        bind: params,
        rowMode: 'object'
      });
      return result && result[0] ? result[0].values : [];
    } catch (error) {
      console.error('查询失败:', error.message);
      return [];
    }
  },
  
  // 执行查询，返回第一行结果
  get: (sql, params = []) => {
    try {
      const result = db.exec(sql, {
        bind: params,
        rowMode: 'object'
      });
      return result && result[0] && result[0].values && result[0].values.length > 0 ? result[0].values[0] : null;
    } catch (error) {
      console.error('查询失败:', error.message);
      return null;
    }
  },
  
  // 执行非查询操作
  run: (sql, params = []) => {
    try {
      db.run(sql, params);
      // 保存数据库更改
      saveDB();
      return { success: true };
    } catch (error) {
      console.error('执行失败:', error.message);
      return { success: false, error: error.message };
    }
  },
  
  // 执行多个SQL语句
  exec: (sql) => {
    try {
      db.exec(sql);
      // 保存数据库更改
      saveDB();
      return { success: true };
    } catch (error) {
      console.error('执行失败:', error.message);
      return { success: false, error: error.message };
    }
  }
};

// 导出模块
module.exports = {
  initializeDB,
  saveDB,
  getDB: () => db,
  db: dbWrapper
};
