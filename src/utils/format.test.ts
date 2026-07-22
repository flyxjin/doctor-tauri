import { describe, it, expect } from 'vitest';
import { formatFileSize, compareVersions } from './format';

describe('formatFileSize', () => {
  it('零或负数返回"未知"', () => {
    expect(formatFileSize(0)).toBe('未知');
    expect(formatFileSize(-1)).toBe('未知');
  });

  it('小于 1KB 显示字节', () => {
    expect(formatFileSize(1)).toBe('1 B');
    expect(formatFileSize(512)).toBe('512 B');
    expect(formatFileSize(1023)).toBe('1023 B');
  });

  it('1KB ~ 1MB 显示 KB', () => {
    expect(formatFileSize(1024)).toBe('1.0 KB');
    expect(formatFileSize(1536)).toBe('1.5 KB');
    expect(formatFileSize(1024 * 1024 - 1)).toBe('1024.0 KB');
  });

  it('大于等于 1MB 显示 MB', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1.0 MB');
    expect(formatFileSize(1024 * 1024 * 5)).toBe('5.0 MB');
    expect(formatFileSize(1572864)).toBe('1.5 MB');
  });
});

describe('compareVersions', () => {
  it('相等版本返回 0', () => {
    expect(compareVersions('1.0.0', '1.0.0')).toBe(0);
    expect(compareVersions('0.2.0', '0.2.0')).toBe(0);
  });

  it('大于返回 1', () => {
    expect(compareVersions('1.0.0', '0.9.9')).toBe(1);
    expect(compareVersions('2.0.0', '1.9.9')).toBe(1);
    expect(compareVersions('1.2.0', '1.1.9')).toBe(1);
  });

  it('小于返回 -1', () => {
    expect(compareVersions('0.9.9', '1.0.0')).toBe(-1);
    expect(compareVersions('1.1.0', '1.2.0')).toBe(-1);
  });

  it('支持 v 前缀', () => {
    expect(compareVersions('v1.0.0', '1.0.0')).toBe(0);
    expect(compareVersions('v2.0.0', 'v1.0.0')).toBe(1);
    expect(compareVersions('v0.1.0', 'v0.2.0')).toBe(-1);
  });

  it('位数不齐时缺位补 0', () => {
    expect(compareVersions('1.0', '1.0.0')).toBe(0);
    expect(compareVersions('1', '1.0.0')).toBe(0);
    expect(compareVersions('1.0.1', '1.0')).toBe(1);
  });

  it('非数字字符按 0 处理', () => {
    expect(compareVersions('a.b.c', '0.0.0')).toBe(0);
  });
});
