// CSV 解析工具：支持 RFC 4180 基本场景（含双引号转义、UTF-8 BOM 剥离）
import type { MedicineImportRecord } from '@/types';

/**
 * 简易 CSV 行解析：支持双引号转义。
 * 兼容 RFC 4180 基本场景：含 , " \n 的字段用双引号包裹，内部双引号用 "" 转义。
 */
export function parseCsvLine(line: string): string[] {
  const fields: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        current += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      fields.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  fields.push(current);
  return fields;
}

/** 解析 CSV 文本为药材导入记录数组（自动剥离 UTF-8 BOM） */
export function parseCsvText(text: string): MedicineImportRecord[] {
  let normalized = text;
  if (normalized.charCodeAt(0) === 0xfeff) {
    normalized = normalized.slice(1);
  }
  const lines = normalized.split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length === 0) return [];

  const header = parseCsvLine(lines[0]).map((h) => h.trim().toLowerCase());
  if (!header.includes('name')) {
    throw new Error('CSV 文件必须包含 name 列');
  }

  const records: MedicineImportRecord[] = [];
  for (let i = 1; i < lines.length; i++) {
    const cells = parseCsvLine(lines[i]);
    const obj: Record<string, string> = {};
    header.forEach((key, idx) => {
      obj[key] = (cells[idx] ?? '').trim();
    });
    records.push({
      name: obj.name ?? '',
      alias: obj.alias,
      category: obj.category,
      nature: obj.nature,
      taste: obj.taste,
      meridian: obj.meridian,
      efficacy: obj.efficacy,
      indications: obj.indications,
      usage: obj.usage,
      dosage: obj.dosage,
      contraindication: obj.contraindication,
      notes: obj.notes,
      quantity: obj.quantity,
      unit: obj.unit,
      price: obj.price,
      min_stock: obj.min_stock,
    });
  }
  return records;
}
