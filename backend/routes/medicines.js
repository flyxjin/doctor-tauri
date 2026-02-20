const express = require('express');
const router = express.Router();
const { db } = require('../config/db');

// 获取所有中药材
router.get('/', (req, res) => {
  const sql = 'SELECT * FROM medicines';
  const results = db.all(sql);
  res.json(results);
});

// 根据ID获取中药材
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const sql = 'SELECT * FROM medicines WHERE id = ?';
  const results = db.all(sql, [id]);
  if (results.length === 0) {
    res.status(404).json({ error: '中药材不存在' });
    return;
  }
  res.json(results[0]);
});

// 添加中药材
router.post('/', (req, res) => {
  const { name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症 } = req.body;
  const sql = 'INSERT INTO medicines (name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症) VALUES (?, ?, ?, ?, ?, ?, ?, ?)';
  const result = db.run(sql, [name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症]);
  if (!result.success) {
    res.status(500).json({ error: result.error });
    return;
  }
  // 获取新插入的记录ID
  const lastIdResult = db.all('SELECT last_insert_rowid() as id');
  const lastId = lastIdResult[0] ? lastIdResult[0][0] : 0;
  res.json({ id: lastId, ...req.body });
});

// 更新中药材
router.put('/:id', (req, res) => {
  const { id } = req.params;
  const { name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症 } = req.body;
  const sql = 'UPDATE medicines SET name = ?, nature = ?, taste = ?, meridian = ?, efficacy = ?, usage = ?, dosage = ?, 禁忌症 = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?';
  const result = db.run(sql, [name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症, id]);
  if (!result.success) {
    res.status(500).json({ error: result.error });
    return;
  }
  // 检查是否有记录被更新
  const checkResult = db.all('SELECT * FROM medicines WHERE id = ?', [id]);
  if (checkResult.length === 0) {
    res.status(404).json({ error: '中药材不存在' });
    return;
  }
  res.json({ id: parseInt(id), ...req.body });
});

// 删除中药材
router.delete('/:id', (req, res) => {
  const { id } = req.params;
  // 检查记录是否存在
  const checkResult = db.all('SELECT * FROM medicines WHERE id = ?', [id]);
  if (checkResult.length === 0) {
    res.status(404).json({ error: '中药材不存在' });
    return;
  }
  const sql = 'DELETE FROM medicines WHERE id = ?';
  const result = db.run(sql, [id]);
  if (!result.success) {
    res.status(500).json({ error: result.error });
    return;
  }
  res.json({ message: '删除成功' });
});

module.exports = router;