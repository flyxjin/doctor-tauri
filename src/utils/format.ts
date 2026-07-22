// 通用格式化与比较工具函数

/**
 * 格式化文件大小为人类可读字符串。
 * @param bytes 字节数
 * @returns 如 "1.5 MB"、"320 KB"、"未知"
 */
export function formatFileSize(bytes: number): string {
  if (!bytes || bytes <= 0) return '未知';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

/**
 * 简单语义版本比较（支持 "v1.2.3" 前缀）。
 * @returns -1 表示 a<b，0 表示相等，1 表示 a>b
 */
export function compareVersions(a: string, b: string): number {
  const pa = a.replace(/^v/, '').split('.').map((n) => parseInt(n, 10) || 0);
  const pb = b.replace(/^v/, '').split('.').map((n) => parseInt(n, 10) || 0);
  const len = Math.max(pa.length, pb.length);
  for (let i = 0; i < len; i++) {
    const x = pa[i] ?? 0;
    const y = pb[i] ?? 0;
    if (x > y) return 1;
    if (x < y) return -1;
  }
  return 0;
}
