const express = require('express');
const router = express.Router();
const { db } = require('../config/db');

// 获取所有处方
router.get('/', (req, res) => {
  const sql = 'SELECT * FROM prescriptions ORDER BY created_at DESC';
  const results = db.all(sql);
  res.json(results);
});

// 根据ID获取处方详情
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const prescriptionSql = 'SELECT * FROM prescriptions WHERE id = ?';
  const itemsSql = 'SELECT pi.*, m.name FROM prescription_items pi JOIN medicines m ON pi.medicine_id = m.id WHERE pi.prescription_id = ?';
  
  const prescriptionResults = db.all(prescriptionSql, [id]);
  if (prescriptionResults.length === 0) {
    res.status(404).json({ error: '处方不存在' });
    return;
  }
  
  const itemsResults = db.all(itemsSql, [id]);
  
  res.json({
    prescription: prescriptionResults[0],
    items: itemsResults
  });
});

// 创建处方
router.post('/', (req, res) => {
  const { patient_name, patient_age, patient_gender, diagnosis, items, created_by } = req.body;
  
  // 计算总金额
  const total_amount = items.reduce((sum, item) => sum + item.amount, 0);
  
  // 插入处方
  const prescriptionSql = 'INSERT INTO prescriptions (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by) VALUES (?, ?, ?, ?, ?, ?)';
  const prescriptionResult = db.run(prescriptionSql, [patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by]);
  
  if (!prescriptionResult.success) {
    res.status(500).json({ error: prescriptionResult.error });
    return;
  }
  
  // 获取新插入的处方ID
  const lastIdResult = db.all('SELECT last_insert_rowid() as id');
  const prescription_id = lastIdResult[0] ? lastIdResult[0][0] : 0;
  
  // 插入处方明细
  const itemSql = 'INSERT INTO prescription_items (prescription_id, medicine_id, quantity, unit, price, amount) VALUES (?, ?, ?, ?, ?, ?)';
  for (const item of items) {
    const itemResult = db.run(itemSql, [prescription_id, item.medicine_id, item.quantity, item.unit, item.price, item.amount]);
    if (!itemResult.success) {
      res.status(500).json({ error: itemResult.error });
      return;
    }
    
    // 更新库存
    const updateInventorySql = 'UPDATE inventory SET quantity = quantity - ?, last_updated = CURRENT_TIMESTAMP WHERE medicine_id = ?';
    const inventoryResult = db.run(updateInventorySql, [item.quantity, item.medicine_id]);
    if (!inventoryResult.success) {
      res.status(500).json({ error: inventoryResult.error });
      return;
    }
    
    // 记录库存变动
    const historySql = 'INSERT INTO inventory_history (medicine_id, type, quantity, price, total_amount, operator, notes) VALUES (?, ?, ?, ?, ?, ?, ?)';
    const historyResult = db.run(historySql, [item.medicine_id, '出库', item.quantity, item.price, item.amount, created_by, `处方出库: ${prescription_id}`]);
    if (!historyResult.success) {
      res.status(500).json({ error: historyResult.error });
      return;
    }
  }
  
  res.json({ id: prescription_id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by });
});

// 删除处方
router.delete('/:id', (req, res) => {
  const { id } = req.params;
  
  // 检查处方是否存在
  const checkResult = db.all('SELECT * FROM prescriptions WHERE id = ?', [id]);
  if (checkResult.length === 0) {
    res.status(404).json({ error: '处方不存在' });
    return;
  }
  
  // 删除处方（级联删除会自动删除相关的处方明细）
  const sql = 'DELETE FROM prescriptions WHERE id = ?';
  const result = db.run(sql, [id]);
  if (!result.success) {
    res.status(500).json({ error: result.error });
    return;
  }
  
  res.json({ message: '删除成功' });
});

module.exports = router;