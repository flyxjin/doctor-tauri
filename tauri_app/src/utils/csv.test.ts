import { describe, it, expect } from 'vitest';
import { parseCsvLine, parseCsvText } from './csv';

describe('parseCsvLine', () => {
  it('简单逗号分隔', () => {
    expect(parseCsvLine('a,b,c')).toEqual(['a', 'b', 'c']);
  });

  it('空行返回单元素空字符串数组', () => {
    expect(parseCsvLine('')).toEqual(['']);
  });

  it('包含逗号的字段用双引号包裹', () => {
    expect(parseCsvLine('"a,b",c')).toEqual(['a,b', 'c']);
  });

  it('字段内双引号用 "" 转义', () => {
    expect(parseCsvLine('"he said ""hi""",x')).toEqual(['he said "hi"', 'x']);
  });

  it('末尾空字段保留', () => {
    expect(parseCsvLine('a,b,')).toEqual(['a', 'b', '']);
  });

  it('单字段', () => {
    expect(parseCsvLine('hello')).toEqual(['hello']);
  });
});

describe('parseCsvText', () => {
  it('空文本返回空数组', () => {
    expect(parseCsvText('')).toEqual([]);
  });

  it('只有空白行返回空数组', () => {
    expect(parseCsvText('  \n  \n')).toEqual([]);
  });

  it('缺少 name 列抛错', () => {
    expect(() => parseCsvText('alias,category\nfoo,bar')).toThrow(
      'CSV 文件必须包含 name 列',
    );
  });

  it('标准 CSV 解析正确', () => {
    const csv = 'name,alias,category\n人参,百草,补虚药\n黄芪,北芪,补虚药';
    const records = parseCsvText(csv);
    expect(records).toHaveLength(2);
    expect(records[0].name).toBe('人参');
    expect(records[0].alias).toBe('百草');
    expect(records[0].category).toBe('补虚药');
    expect(records[1].name).toBe('黄芪');
  });

  it('剥离 UTF-8 BOM', () => {
    const csv = '\uFEFFname,category\n人参,补虚药';
    const records = parseCsvText(csv);
    expect(records).toHaveLength(1);
    expect(records[0].name).toBe('人参');
  });

  it('兼容 CRLF 换行', () => {
    const csv = 'name\r\n人参\r\n黄芪\r\n';
    const records = parseCsvText(csv);
    expect(records).toHaveLength(2);
  });

  it('忽略空行', () => {
    const csv = 'name\n人参\n\n黄芪\n\n';
    const records = parseCsvText(csv);
    expect(records).toHaveLength(2);
  });

  it('header 大小写不敏感（转小写）', () => {
    const csv = 'NAME,Category\n人参,补虚药';
    const records = parseCsvText(csv);
    expect(records[0].name).toBe('人参');
    expect(records[0].category).toBe('补虚药');
  });

  it('字段数量不足时缺省为空字符串', () => {
    const csv = 'name,alias,category\n人参';
    const records = parseCsvText(csv);
    expect(records[0].name).toBe('人参');
    expect(records[0].alias).toBe('');
  });
});
