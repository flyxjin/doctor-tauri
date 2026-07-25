import { describe, it, expect } from 'vitest';
import { parseAllergyKeywords, checkAllergy } from './allergy';

describe('parseAllergyKeywords', () => {
  it('空字符串返回空数组', () => {
    expect(parseAllergyKeywords('')).toEqual([]);
    expect(parseAllergyKeywords(null)).toEqual([]);
    expect(parseAllergyKeywords(undefined)).toEqual([]);
    expect(parseAllergyKeywords('   ')).toEqual([]);
  });

  it('支持多种分隔符', () => {
    expect(parseAllergyKeywords('青霉素,海鲜；花生\n人参、薄荷')).toEqual([
      '青霉素',
      '海鲜',
      '花生',
      '人参',
      '薄荷',
    ]);
  });

  it('过滤过短的关键词（<2 字符）', () => {
    expect(parseAllergyKeywords('a,青,人参')).toEqual(['人参']);
  });

  it('去重', () => {
    expect(parseAllergyKeywords('人参,人参,海鲜')).toEqual(['人参', '海鲜']);
  });
});

describe('checkAllergy', () => {
  const items = [
    { medicine_id: 1, medicine_name: '人参' },
    { medicine_id: 2, medicine_name: '麻黄' },
    { medicine_id: 3, medicine_name: '甘草' },
  ];

  const medicines = new Map([
    [1, { id: 1, contraindication: '体虚者慎用' }],
    [2, { id: 2, contraindication: '青霉素过敏者禁用' }],
    [3, { id: 3, contraindication: null }],
  ]);

  it('无过敏史返回空数组', () => {
    expect(checkAllergy(items, medicines, '')).toEqual([]);
    expect(checkAllergy(items, medicines, null)).toEqual([]);
  });

  it('药材名直接命中过敏原', () => {
    const conflicts = checkAllergy(items, medicines, '人参');
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0]).toEqual({
      allergen: '人参',
      medicine_name: '人参',
      matchType: 'name',
    });
  });

  it('药材禁忌字段提及过敏原', () => {
    const conflicts = checkAllergy(items, medicines, '青霉素');
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0]).toEqual({
      allergen: '青霉素',
      medicine_name: '麻黄',
      matchType: 'contraindication',
    });
  });

  it('同时命中名称和禁忌字段时不重复', () => {
    // 人参在名称中命中，且其禁忌字段也含"人参"
    const medsWithConflict = new Map([
      [1, { id: 1, contraindication: '人参过敏者禁用' }],
    ]);
    const conflicts = checkAllergy(
      [{ medicine_id: 1, medicine_name: '人参' }],
      medsWithConflict,
      '人参',
    );
    // 名称命中优先，禁忌字段命中被去重
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].matchType).toBe('name');
  });

  it('无冲突时返回空数组', () => {
    expect(checkAllergy(items, medicines, '海鲜')).toEqual([]);
  });

  it('支持数组形式的药材库', () => {
    const medArray = [
      { id: 1, contraindication: '体虚者慎用' },
      { id: 2, contraindication: '青霉素过敏者禁用' },
    ];
    const conflicts = checkAllergy(items, medArray, '青霉素');
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].medicine_name).toBe('麻黄');
  });

  it('空处方返回空数组', () => {
    expect(checkAllergy([], medicines, '人参')).toEqual([]);
  });
});
