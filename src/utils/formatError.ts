// 统一错误提示格式化
//
// 后端 Rust 命令返回 Err(String) 时，前端拿到的错误字符串往往技术化
// （如 "记录操作日志失败: ..."），直接展示给用户体验差。
// 本工具负责：
// 1. 识别常见后端错误模式，映射为友好中文提示
// 2. 其他未知错误统一加"操作失败："前缀，避免裸露堆栈

/** 常见后端错误模式 → 友好提示 */
const ERROR_PATTERNS: Array<{ pattern: RegExp; message: string }> = [
  // 库存相关
  { pattern: /库存不足|insufficient.?stock/i, message: '库存不足，请检查库存余量' },
  { pattern: /数量必须大于|invalid.?quantity/i, message: '数量必须大于 0' },
  // 唯一约束冲突
  { pattern: /UNIQUE constraint failed|Duplicate entry/i, message: '该记录已存在，请勿重复添加' },
  // 外键约束
  {
    pattern: /FOREIGN KEY constraint failed|foreign key/i,
    message: '该记录被其他数据引用，无法删除',
  },
  // 网络相关
  { pattern: /网络|network|timeout|超时/i, message: '网络连接异常，请检查网络后重试' },
  { pattern: /请求 Gitee API 失败|Gitee API/i, message: '检查更新失败，请稍后重试' },
  // 数据库
  { pattern: /数据库|database|sqlite/i, message: '数据库操作失败，请稍后重试' },
  { pattern: /获取数据库锁失败|database is locked/i, message: '系统繁忙，请稍后重试' },
  // 文件操作
  { pattern: /创建.*目录失败|创建.*文件失败|写入.*失败/i, message: '文件操作失败，请检查磁盘空间和权限' },
  // 路径遍历
  { pattern: /路径遍历|filename.*invalid/i, message: '文件名包含非法字符' },
];

/**
 * 格式化错误为用户友好的提示文案
 *
 * @param e 后端 invoke 抛出的错误（通常是 string 或 Error）
 * @returns 友好的中文提示
 */
export function formatError(e: unknown): string {
  let raw: string;
  if (typeof e === 'string') {
    raw = e;
  } else if (e instanceof Error) {
    raw = e.message;
  } else {
    raw = String(e);
  }

  // 去除可能的 "Error: " 或 "Error invoking command: " 前缀
  const cleaned = raw.replace(/^Error(?:\s*invoking\s*command)?:\s*/i, '');

  // 匹配已知模式
  for (const { pattern, message } of ERROR_PATTERNS) {
    if (pattern.test(cleaned)) {
      return message;
    }
  }

  // 未知错误：截断过长的技术细节，加统一前缀
  const truncated = cleaned.length > 80 ? `${cleaned.slice(0, 80)}...` : cleaned;
  return `操作失败：${truncated}`;
}
