import { describe, it, expect } from 'vitest';
import { parseDefaultDosage } from './dosage';

describe('parseDefaultDosage', () => {
  it('空值返回 null', () => {
    expect(parseDefaultDosage('')).toBeNull();
    expect(parseDefaultDosage(null)).toBeNull();
    expect(parseDefaultDosage(undefined)).toBeNull();
    expect(parseDefaultDosage('   ')).toBeNull();
  });

  it('范围格式取下限', () => {
    expect(parseDefaultDosage('3-9g')).toBe(3);
    expect(parseDefaultDosage('9-30g')).toBe(9);
    expect(parseDefaultDosage('6-15g')).toBe(6);
  });

  it('支持中文波浪号和英文波浪号', () => {
    expect(parseDefaultDosage('3～9g')).toBe(3);
    expect(parseDefaultDosage('3~9g')).toBe(3);
  });

  it('支持小数', () => {
    expect(parseDefaultDosage('0.5-1g')).toBe(0.5);
    expect(parseDefaultDosage('0.3g')).toBe(0.3);
  });

  it('单个数值直接返回', () => {
    expect(parseDefaultDosage('10g')).toBe(10);
    expect(parseDefaultDosage('15')).toBe(15);
  });

  it('从带前缀的文本中提取数值', () => {
    expect(parseDefaultDosage('用量 3-9g')).toBe(3);
    expect(parseDefaultDosage('煎服，3-9g')).toBe(3);
  });

  it('无数值返回 null', () => {
    expect(parseDefaultDosage('水煎服')).toBeNull();
    expect(parseDefaultDosage('适量')).toBeNull();
    expect(parseDefaultDosage('遵医嘱')).toBeNull();
  });
});
