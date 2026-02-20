const fs = require('fs');
const path = require('path');

// 导入数据库配置
const { initializeDB, db } = require('../config/db');

// 读取中药材数据
const medicinesDataPath = path.join(__dirname, 'medicines_data.json');
const medicinesData = JSON.parse(fs.readFileSync(medicinesDataPath, 'utf8'));

// 导入中药材数据
async function importMedicines() {
  try {
    console.log('开始导入中药材数据...');
    
    // 初始化数据库
    await initializeDB();
    
    console.log(`共 ${medicinesData.length} 种中药材需要导入`);
    
    let importedCount = 0;
    let skippedCount = 0;
    
    // 遍历中药材数据
    for (const medicine of medicinesData) {
      try {
        // 检查中药材是否已存在
        const checkSql = 'SELECT * FROM medicines WHERE name = ?';
        const existingMedicines = db.all(checkSql, [medicine.name]);
        
        if (existingMedicines.length > 0) {
          console.log(`跳过已存在的中药材: ${medicine.name}`);
          skippedCount++;
          continue;
        }
        
        // 插入中药材数据
        const insertSql = `
          INSERT INTO medicines (
            name, nature, taste, meridian, efficacy, usage, dosage, 禁忌症
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `;
        
        const result = db.run(insertSql, [
          medicine.name,
          medicine.nature,
          medicine.taste,
          medicine.meridian,
          medicine.efficacy,
          medicine.usage,
          medicine.dosage,
          medicine.禁忌症
        ]);
        
        if (result.success) {
          console.log(`导入成功: ${medicine.name}`);
          importedCount++;
        } else {
          console.log(`导入失败: ${medicine.name}, 错误: ${result.error}`);
          skippedCount++;
        }
        
      } catch (error) {
        console.log(`处理中药材 ${medicine.name} 时出错: ${error.message}`);
        skippedCount++;
      }
    }
    
    console.log('\n导入完成!');
    console.log(`成功导入: ${importedCount} 种中药材`);
    console.log(`跳过: ${skippedCount} 种中药材`);
    console.log(`总处理: ${importedCount + skippedCount} 种中药材`);
    
  } catch (error) {
    console.error('导入过程中出错:', error.message);
  }
}

// 执行导入
importMedicines();
