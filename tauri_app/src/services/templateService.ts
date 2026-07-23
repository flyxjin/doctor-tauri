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

interface TemplatesFile {
  templates: PrescriptionTemplate[];
}

const templates: PrescriptionTemplate[] =
  (templatesData as TemplatesFile).templates ?? (templatesData as unknown as PrescriptionTemplate[]);

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
