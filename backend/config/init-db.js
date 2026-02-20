const db = require('./db');

// 创建数据库
const createDatabase = `
CREATE DATABASE IF NOT EXISTS traditional_chinese_medicine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
`;

// 切换到数据库
const useDatabase = `USE traditional_chinese_medicine;`;

// 创建中药材表
const createMedicinesTable = `
CREATE TABLE IF NOT EXISTS medicines (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  nature VARCHAR(50),
  taste VARCHAR(50),
  meridian VARCHAR(100),
  efficacy TEXT,
  usage VARCHAR(255),
  dosage VARCHAR(100),
 禁忌症 TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_name (name)
);
`;

// 创建处方表
const createPrescriptionsTable = `
CREATE TABLE IF NOT EXISTS prescriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_name VARCHAR(100),
  patient_age INT,
  patient_gender ENUM('男', '女'),
  diagnosis TEXT,
  total_amount DECIMAL(10,2) DEFAULT 0,
  created_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
`;

// 创建处方明细表
const createPrescriptionItemsTable = `
CREATE TABLE IF NOT EXISTS prescription_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prescription_id INT NOT NULL,
  medicine_id INT NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  unit VARCHAR(20) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
  FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);
`;

// 创建库存表
const createInventoryTable = `
CREATE TABLE IF NOT EXISTS inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  medicine_id INT NOT NULL,
  quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
  unit VARCHAR(20) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  min_stock DECIMAL(10,2) NOT NULL DEFAULT 10,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (medicine_id) REFERENCES medicines(id),
  UNIQUE KEY unique_medicine (medicine_id)
);
`;

// 创建库存变动历史表
const createInventoryHistoryTable = `
CREATE TABLE IF NOT EXISTS inventory_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  medicine_id INT NOT NULL,
  type ENUM('入库', '出库', '盘点') NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  price DECIMAL(10,2),
  total_amount DECIMAL(10,2),
  operator VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);
`;

// 初始化数据库
async function initDatabase() {
  try {
    // 执行SQL语句
    await db.promise().query(createDatabase);
    console.log('数据库创建成功');
    
    await db.promise().query(useDatabase);
    console.log('切换到数据库成功');
    
    await db.promise().query(createMedicinesTable);
    console.log('中药材表创建成功');
    
    await db.promise().query(createPrescriptionsTable);
    console.log('处方表创建成功');
    
    await db.promise().query(createPrescriptionItemsTable);
    console.log('处方明细表创建成功');
    
    await db.promise().query(createInventoryTable);
    console.log('库存表创建成功');
    
    await db.promise().query(createInventoryHistoryTable);
    console.log('库存变动历史表创建成功');
    
    console.log('数据库初始化完成');
  } catch (error) {
    console.error('数据库初始化失败:', error);
  } finally {
    db.end();
  }
}

// 执行初始化
initDatabase();