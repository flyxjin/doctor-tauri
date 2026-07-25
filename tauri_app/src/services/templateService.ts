// 处方模板库 Service：加载中医经典方剂模板，供处方开具页快速调用
// 数据来源：src/data/prescription_templates.json（与 Python 端 core/data/prescription_templates.json 对齐）

export interface TemplateItem {
  name: string;
  quantity: number;
  unit: string;
}

export interface PrescriptionTemplate {
  name: string;
  category: string;
  description: string;
  indication: string;
  items: TemplateItem[];
}

// 静态导入 JSON（Vite 支持）
import templatesData from '@/data/prescription_templates.json';

/**
 * 类型守卫：判断未知值是否为 PrescriptionTemplate[]。
 *
 * 替代 `as unknown as` 强制断言，让 JSON 数据形状在运行时得到校验，
 * 避免模板文件结构变更时静默传入脏数据。
 */
function isTemplatesArray(v: unknown): v is PrescriptionTemplate[] {
  if (!Array.isArray(v)) return false;
  return v.every(
    (t) =>
      t != null &&
      typeof t === 'object' &&
      'name' in t &&
      typeof (t as { name: unknown }).name === 'string' &&
      'items' in t &&
      Array.isArray((t as { items: unknown }).items),
  );
}

// 优先识别 { templates: [...] } 包装结构；否则直接将整体视为数组（需通过类型守卫校验）
const wrapped = (templatesData as { templates?: unknown }).templates;
const templates: PrescriptionTemplate[] = isTemplatesArray(wrapped)
  ? wrapped
  : isTemplatesArray(templatesData)
    ? templatesData
    : [];

/** 返回全部方剂模板 */
export function getTemplates(): PrescriptionTemplate[] {
  return templates;
}

/** 返回全部分类（去重） */
export function getCategories(): string[] {
  return [...new Set(templates.map((t) => t.category))];
}

/** 按关键字搜索方剂（名称 / 主治 / 描述） */
export function searchTemplates(keyword: string): PrescriptionTemplate[] {
  if (!keyword.trim()) return templates;
  const k = keyword.toLowerCase();
  return templates.filter(
    (t) =>
      t.name.toLowerCase().includes(k) ||
      t.indication.toLowerCase().includes(k) ||
      t.description.toLowerCase().includes(k),
  );
}

/** 按方剂名精确查找 */
export function getByName(name: string): PrescriptionTemplate | undefined {
  return templates.find((t) => t.name === name);
}
