// 药材剂量解析工具：从 Medicine.dosage 自由文本中推导推荐起始用量
//
// 设计思路：
// - dosage 字段为自由文本，常见格式："3-9g"、"9-30g"、"6-15g"、"10g"
// - 优先解析"范围"取下限（保守起始剂量，符合 TCM 先小量后加量的原则）
// - 无范围时取单个数值
// - 无法解析时返回 null，由调用方使用兜底默认值

/**
 * 从剂量文本中解析推荐起始用量。
 *
 * 解析规则：
 * 1. 优先匹配范围模式（如 "3-9g"、"9～30g"），取下限
 * 2. 无范围时取第一个数值（如 "10g" → 10）
 * 3. 无数值时返回 null
 *
 * @example
 *   parseDefaultDosage('3-9g')     // 3
 *   parseDefaultDosage('9-30g')    // 9
 *   parseDefaultDosage('10g')      // 10
 *   parseDefaultDosage('水煎服')    // null
 *   parseDefaultDosage(undefined)  // null
 */
export function parseDefaultDosage(dosage?: string | null): number | null {
  if (!dosage || !dosage.trim()) return null;

  // 1) 范围模式：数字 + 分隔符(-～~) + 数字
  //    支持：3-9g、9～30g、6~15g、0.5-1g
  const rangeMatch = dosage.match(/(\d+(?:\.\d+)?)\s*[-~～]\s*(\d+(?:\.\d+)?)/);
  if (rangeMatch) {
    const low = parseFloat(rangeMatch[1]);
    if (!Number.isNaN(low) && low > 0) return low;
  }

  // 2) 单个数值模式：取第一个数值
  const numMatch = dosage.match(/(\d+(?:\.\d+)?)/);
  if (numMatch) {
    const v = parseFloat(numMatch[1]);
    if (!Number.isNaN(v) && v > 0) return v;
  }

  return null;
}
