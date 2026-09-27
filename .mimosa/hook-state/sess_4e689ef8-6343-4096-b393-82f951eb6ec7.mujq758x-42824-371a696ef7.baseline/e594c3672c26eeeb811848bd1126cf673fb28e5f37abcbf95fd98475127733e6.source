// CSV 解析工具：支持 RFC 4180 基本场景（含双引号转义、UTF-8 BOM 剥离）
import type { MedicineImportRecord } from '@/types';

/**
 * CSV 公式注入防护：Excel/WPS 会把以 = + - @ 开头的单元格当公式执行，
 * 对这类字段前置单引号使其按文本处理；"-3" 之类的负数不前置，避免误伤数字。
 */
function sanitizeCsvFormula(s: string): string {
  const c = s.charAt(0);
  const dangerous =
    c === '=' || c === '+' || c === '@' || c === '\t' || (c === '-' && !/^[.\d]/.test(s.slice(1)));
  return dangerous ? `'${s}` : s;
}

/**
 * 转义单个 CSV 字段：含逗号/引号/换行的字段用双引号包裹，内部双引号用 "" 转义；
 * 公式注入字符前置单引号（与后端 export_medicines_csv 防护一致）。
 *
 * 统一了原 Inventory.tsx 与 History.tsx 中两处不一致的转义实现。
 */
export function escapeCsvField(v: string | number | null | undefined): string {
  const s = v == null ? '' : String(v);
  const safe = sanitizeCsvFormula(s);
  return /[",\n]/.test(safe) ? `"${safe.replace(/"/g, '""')}"` : safe;
}

/**
 * 将二维数组转为 CSV 字符串（自动加 UTF-8 BOM，便于 Excel 正确识别中文）。
 *
 * @param rows 第一行为表头，后续为数据行
 * @param lineSeparator 行分隔符，默认 `\r\n`（Excel 友好）
 */
export function rowsToCsv(rows: (string | number | null | undefined)[][], lineSeparator = '\r\n'): string {
  const lines = rows.map((row) => row.map(escapeCsvField).join(','));
  return '\uFEFF' + lines.join(lineSeparator);
}

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

/**
 * 将 CSV 文本拆分为逻辑行：引号内的换行属于字段内容（RFC 4180），
 * 需合并到同一逻辑行，否则导出的多行字段（功效/主治等）在回导时会被裂成多条脏记录。
 */
export function splitCsvLines(text: string): string[] {
  const lines: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      current += ch;
      if (ch === '"') {
        if (text[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = false;
        }
      }
    } else if (ch === '"') {
      inQuotes = true;
      current += ch;
    } else if (ch === '\n' || (ch === '\r' && text[i + 1] === '\n')) {
      lines.push(current);
      current = '';
      if (ch === '\r') i++;
    } else {
      current += ch;
    }
  }
  lines.push(current);
  return lines;
}

/** 解析 CSV 文本为药材导入记录数组（自动剥离 UTF-8 BOM） */
export function parseCsvText(text: string): MedicineImportRecord[] {
  let normalized = text;
  if (normalized.charCodeAt(0) === 0xfeff) {
    normalized = normalized.slice(1);
  }
  const lines = splitCsvLines(normalized).filter((l) => l.trim().length > 0);
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
