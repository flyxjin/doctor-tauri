const fs = require('fs');
const path = require('path');

// 导入数据库配置
const { initializeDB, db } = require('../config/db');

// 初始化库存数据
async function initInventory() {
  try {
    console.log('开始初始化库存数据...');
    
    // 初始化数据库
    await initializeDB();
    
    // 获取所有中药材
    const medicinesSql = 'SELECT id, name FROM medicines';
    const medicines = db.all(medicinesSql);
    
    console.log(`共找到 ${medicines.length} 种中药材`);
    
    let addedCount = 0;
    let skippedCount = 0;
    
    // 为每种中药材设置库存
    for (const medicine of medicines) {
      const medicineId = medicine[0]; // id是第一个字段
      const medicineName = medicine[1]; // name是第二个字段
      
      try {
        // 检查库存是否已存在
        const checkSql = 'SELECT * FROM inventory WHERE medicine_id = ?';
        const existingInventory = db.all(checkSql, [medicineId]);
        
        if (existingInventory.length > 0) {
          console.log(`跳过已存在库存的中药材: ${medicineName}`);
          skippedCount++;
          continue;
        }
        
        // 随机设置库存数量（100-500克）
        const randomQuantity = Math.floor(Math.random() * 400) + 100;
        
        // 随机设置价格（5-50元/克）
        const randomPrice = (Math.random() * 45 + 5).toFixed(2);
        
        // 随机设置最小库存预警（10-50克）
        const randomMinStock = Math.floor(Math.random() * 40) + 10;
        
        // 插入库存数据
        const insertSql = `
          INSERT INTO inventory (
            medicine_id, quantity, unit, price, min_stock
          ) VALUES (?, ?, 'g', ?, ?)
        `;
        
        const result = db.run(insertSql, [
          medicineId,
          randomQuantity,
          randomPrice,
          randomMinStock
        ]);
        
        if (result.success) {
          console.log(`库存初始化成功: ${medicineName} (${randomQuantity}g, ¥${randomPrice}/g)`);
          addedCount++;
        } else {
          console.log(`库存初始化失败: ${medicineName}, 错误: ${result.error}`);
          skippedCount++;
        }
        
      } catch (error) {
        console.log(`处理中药材 ${medicineName} 库存时出错: ${error.message}`);
        skippedCount++;
      }
    }
    
    console.log('\n库存初始化完成!');
    console.log(`成功添加: ${addedCount} 种中药材库存`);
    console.log(`跳过: ${skippedCount} 种中药材`);
    console.log(`总处理: ${addedCount + skippedCount} 种中药材`);
    
  } catch (error) {
    console.error('初始化库存过程中出错:', error.message);
  }
}

// 执行初始化
initInventory();
