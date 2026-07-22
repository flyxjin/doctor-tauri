import { describe, it, expect } from 'vitest';
import { getTemplates, getCategories, searchTemplates, getByName } from './templateService';

describe('templateService', () => {
  it('getTemplates 返回非空数组', () => {
    const templates = getTemplates();
    expect(Array.isArray(templates)).toBe(true);
    expect(templates.length).toBeGreaterThan(0);
  });

  it('每个模板包含必要字段', () => {
    const templates = getTemplates();
    for (const t of templates) {
      expect(typeof t.name).toBe('string');
      expect(t.name.length).toBeGreaterThan(0);
      expect(typeof t.category).toBe('string');
      expect(Array.isArray(t.items)).toBe(true);
      expect(t.items.length).toBeGreaterThan(0);
    }
  });

  it('每个模板的 items 字段完整', () => {
    const templates = getTemplates();
    for (const t of templates) {
      for (const item of t.items) {
        expect(typeof item.name).toBe('string');
        expect(item.name.length).toBeGreaterThan(0);
        expect(typeof item.quantity).toBe('number');
        expect(item.quantity).toBeGreaterThan(0);
        expect(typeof item.unit).toBe('string');
      }
    }
  });

  it('getCategories 返回去重的分类列表', () => {
    const cats = getCategories();
    const unique = [...new Set(cats)];
    expect(cats.length).toBe(unique.length);
    expect(cats.length).toBeGreaterThan(0);
  });

  it('searchTemplates 空关键字返回全部', () => {
    const all = getTemplates();
    expect(searchTemplates('')).toHaveLength(all.length);
    expect(searchTemplates('   ')).toHaveLength(all.length);
  });

  it('searchTemplates 按名称匹配', () => {
    const results = searchTemplates('归脾');
    expect(results.length).toBeGreaterThan(0);
    expect(results.some((t) => t.name.includes('归脾'))).toBe(true);
  });

  it('searchTemplates 不匹配时返回空数组', () => {
    const results = searchTemplates('不存在的方剂名XYZ');
    expect(results).toEqual([]);
  });

  it('searchTemplates 大小写不敏感', () => {
    const lower = searchTemplates('si').length;
    const upper = searchTemplates('SI').length;
    expect(lower).toBe(upper);
  });

  it('getByName 精确查找存在', () => {
    const templates = getTemplates();
    const first = templates[0];
    const found = getByName(first.name);
    expect(found).toBeDefined();
    expect(found?.name).toBe(first.name);
  });

  it('getByName 查找不存在返回 undefined', () => {
    expect(getByName('这个方剂不存在XYZ')).toBeUndefined();
  });
});
