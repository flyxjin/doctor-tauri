const express = require('express');
const router = express.Router();
const { db } = require('../config/db');

// 获取所有库存
router.get('/', (req, res) => {
  const sql = 'SELECT i.*, m.name FROM inventory i JOIN medicines m ON i.medicine_id = m.id';
  const results = db.all(sql);
  res.json(results);
});

// 获取低库存预警
router.get('/low-stock', (req, res) => {
  const sql = 'SELECT i.*, m.name FROM inventory i JOIN medicines m ON i.medicine_id = m.id WHERE i.quantity <= i.min_stock';
  const results = db.all(sql);
  res.json(results);
});

// 获取库存变动历史
router.get('/history', (req, res) => {
  const sql = 'SELECT ih.*, m.name FROM inventory_history ih JOIN medicines m ON ih.medicine_id = m.id ORDER BY ih.created_at DESC';
  const results = db.all(sql);
  res.json(results);
});

// 入库操作
router.post('/inbound', (req, res) => {
  const { medicine_id, quantity, price, operator, notes } = req.body;
  const total_amount = quantity * price;
  
  // 检查库存是否存在
  const checkSql = 'SELECT * FROM inventory WHERE medicine_id = ?';
  const checkResult = db.all(checkSql, [medicine_id]);
  
  if (checkResult.length > 0) {
    // 更新库存
    const updateSql = 'UPDATE inventory SET quantity = quantity + ?, price = ?, last_updated = CURRENT_TIMESTAMP WHERE medicine_id = ?';
    const updateResult = db.run(updateSql, [quantity, price, medicine_id]);
    if (!updateResult.success) {
      res.status(500).json({ error: updateResult.error });
      return;
    }
  } else {
    // 新增库存记录
    const insertSql = 'INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?, ?, ?, ?, ?)';
    const insertResult = db.run(insertSql, [medicine_id, quantity, 'g', price, 10]);
    if (!insertResult.success) {
      res.status(500).json({ error: insertResult.error });
      return;
    }
  }
  
  // 记录库存变动
  const historySql = 'INSERT INTO inventory_history (medicine_id, type, quantity, price, total_amount, operator, notes) VALUES (?, ?, ?, ?, ?, ?, ?)';
  const historyResult = db.run(historySql, [medicine_id, '入库', quantity, price, total_amount, operator, notes]);
  if (!historyResult.success) {
    res.status(500).json({ error: historyResult.error });
    return;
  }
  
  res.json({ message: '入库成功' });
});

// 出库操作
router.post('/outbound', (req, res) => {
  const { medicine_id, quantity, price, operator, notes } = req.body;
  const total_amount = quantity * price;
  
  // 检查库存是否足够
  const checkSql = 'SELECT * FROM inventory WHERE medicine_id = ?';
  const checkResult = db.all(checkSql, [medicine_id]);
  
  if (checkResult.length === 0) {
    res.status(404).json({ error: '库存不存在' });
    return;
  }
  
  const currentStock = checkResult[0][2]; // quantity is at index 2
  if (currentStock < quantity) {
    res.status(400).json({ error: '库存不足' });
    return;
  }
  
  // 更新库存
  const updateSql = 'UPDATE inventory SET quantity = quantity - ?, last_updated = CURRENT_TIMESTAMP WHERE medicine_id = ?';
  const updateResult = db.run(updateSql, [quantity, medicine_id]);
  if (!updateResult.success) {
    res.status(500).json({ error: updateResult.error });
    return;
  }
  
  // 记录库存变动
  const historySql = 'INSERT INTO inventory_history (medicine_id, type, quantity, price, total_amount, operator, notes) VALUES (?, ?, ?, ?, ?, ?, ?)';
  const historyResult = db.run(historySql, [medicine_id, '出库', quantity, price, total_amount, operator, notes]);
  if (!historyResult.success) {
    res.status(500).json({ error: historyResult.error });
    return;
  }
  
  res.json({ message: '出库成功' });
});

// 盘点操作
router.post('/inventory-check', (req, res) => {
  const { medicine_id, actual_quantity, operator, notes } = req.body;
  
  // 获取当前库存
  const checkSql = 'SELECT * FROM inventory WHERE medicine_id = ?';
  const checkResult = db.all(checkSql, [medicine_id]);
  
  if (checkResult.length === 0) {
    res.status(404).json({ error: '库存不存在' });
    return;
  }
  
  const current_quantity = checkResult[0][2]; // quantity is at index 2
  const price = checkResult[0][4]; // price is at index 4
  const difference = actual_quantity - current_quantity;
  const total_amount = difference * price;
  
  // 更新库存
  const updateSql = 'UPDATE inventory SET quantity = ?, last_updated = CURRENT_TIMESTAMP WHERE medicine_id = ?';
  const updateResult = db.run(updateSql, [actual_quantity, medicine_id]);
  if (!updateResult.success) {
    res.status(500).json({ error: updateResult.error });
    return;
  }
  
  // 记录库存变动
  const historySql = 'INSERT INTO inventory_history (medicine_id, type, quantity, price, total_amount, operator, notes) VALUES (?, ?, ?, ?, ?, ?, ?)';
  const historyResult = db.run(historySql, [medicine_id, '盘点', difference, price, total_amount, operator, notes]);
  if (!historyResult.success) {
    res.status(500).json({ error: historyResult.error });
    return;
  }
  
  res.json({ message: '盘点成功', difference });
});

module.exports = router;