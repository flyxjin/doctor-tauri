import { describe, it, expect } from 'vitest';
import { escapeCsvField, parseCsvLine, parseCsvText, recordsFromRows, rowsToCsv, splitCsvLines } from './csv';

describe('escapeCsvField 公式注入防护', () => {
  it('公式字符前置单引号', () => {
    expect(escapeCsvField('=SUM(A1)')).toBe("'=SUM(A1)");
    expect(escapeCsvField('+8613800138000')).toBe("'+8613800138000");
    expect(escapeCsvField('@cmd')).toBe("'@cmd");
  });

  it('负数不误伤', () => {
    expect(escapeCsvField(-3)).toBe('-3');
    expect(escapeCsvField(-3.5)).toBe('-3.5');
    expect(escapeCsvField('-cmd')).toBe("'-cmd");
  });

  it('普通文本与数字不变', () => {
    expect(escapeCsvField('甘草')).toBe('甘草');
    expect(escapeCsvField(3.14)).toBe('3.14');
    expect(escapeCsvField(null)).toBe('');
  });
});

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
      '导入文件必须包含 name 列',
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

  it('引号内的换行不拆行（RFC 4180 多行字段）', () => {
    const csv = 'name,efficacy\n甘草,"补脾益气\n清热解毒"\n黄芪,补气';
    const records = parseCsvText(csv);
    expect(records).toHaveLength(2);
    expect(records[0].name).toBe('甘草');
    expect(records[0].efficacy).toBe('补脾益气\n清热解毒');
    expect(records[1].name).toBe('黄芪');
  });

  it('rowsToCsv + parseCsvText 往返：多行字段不丢数据', () => {
    const records = parseCsvText(
      rowsToCsv([
        ['name', 'efficacy', 'indications'],
        ['甘草', '补脾益气\r\n清热解毒', '脾虚\r\n咳嗽'],
        ['黄芪', '补气固表', '自汗'],
      ]),
    );
    expect(records).toHaveLength(2);
    expect(records[0].efficacy).toBe('补脾益气\r\n清热解毒');
    expect(records[0].indications).toBe('脾虚\r\n咳嗽');
    expect(records[1].efficacy).toBe('补气固表');
  });
});

describe('splitCsvLines', () => {
  it('LF/CRLF 正常拆行', () => {
    expect(splitCsvLines('a\nb\r\nc')).toEqual(['a', 'b', 'c']);
  });

  it('引号内的换行合并为同一逻辑行', () => {
    expect(splitCsvLines('a,"b\nc",d')).toEqual(['a,"b\nc",d']);
  });

  it('引号内转义引号后仍继续合并换行', () => {
    expect(splitCsvLines('"x\n""y""\n"\nz')).toEqual(['"x\n""y""\n"', 'z']);
  });
});

describe('recordsFromRows（Excel/CSV 共用行转换）', () => {
  it('首行表头转字段，数值单元格转字符串', () => {
    const records = recordsFromRows([
      ['name', 'quantity', 'price', 'min_stock'],
      ['甘草', 50, 0.11, 30],
    ]);
    expect(records).toHaveLength(1);
    expect(records[0].name).toBe('甘草');
    expect(records[0].quantity).toBe('50');
    expect(records[0].price).toBe('0.11');
    expect(records[0].min_stock).toBe('30');
  });

  it('null/缺失单元格转空字符串，表头大小写不敏感', () => {
    const records = recordsFromRows([
      ['NAME', 'alias'],
      ['黄芪', null],
      ['当归', '秦归'],
    ]);
    expect(records[0].alias).toBe('');
    expect(records[1].alias).toBe('秦归');
  });

  it('缺少 name 列抛错', () => {
    expect(() => recordsFromRows([['alias'], ['x']])).toThrow(
      '导入文件必须包含 name 列',
    );
  });

  it('空行数组返回空记录', () => {
    expect(recordsFromRows([])).toEqual([]);
  });
});
