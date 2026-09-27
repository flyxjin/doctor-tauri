// 过敏史校验工具：开方时检测处方药材与患者过敏史的冲突
//
// 设计思路：
// - 过敏史为自由文本（如"青霉素、海鲜、花生"），按常见分隔符拆分为关键词
// - 校验两个维度：
//   1) 药材名称直接命中过敏关键词（如患者对"人参"过敏，处方含"人参"）
//   2) 药材的 contraindication 字段提及过敏关键词（如药材禁忌写"青霉素过敏者禁用"）
// - 采用子串匹配（非医学级 NLP），目的是提供安全提醒而非替代医生判断

export interface AllergyConflict {
  /** 命中的过敏关键词 */
  allergen: string;
  /** 命中的药材名 */
  medicine_name: string;
  /** 命中类型：name=药材名直接匹配，contraindication=禁忌字段提及 */
  matchType: 'name' | 'contraindication';
}

/**
 * 将过敏史文本拆分为关键词数组。
 *
 * 支持的分隔符：中文逗号、英文逗号、分号、中文分号、换行、空格
 * 过短（<2 字符）的关键词会被过滤，避免"对"、"等"等无意义词误命中。
 */
export function parseAllergyKeywords(allergy?: string | null): string[] {
  if (!allergy || !allergy.trim()) return [];
  const raw = allergy
    .split(/[,，;；\n\s、]+/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 2);
  // 去重
  return Array.from(new Set(raw));
}

/** 处方明细项（只需 medicine_id 和 medicine_name） */
interface ItemLike {
  medicine_id: number;
  medicine_name: string;
}

/** 药材库条目（只需 id 和 contraindication） */
interface MedicineLibLike {
  id: number | null;
  contraindication?: string | null;
}

/**
 * 校验处方药材与患者过敏史的冲突。
 *
 * @param items 处方明细
 * @param medicines 药材库（用于查询 contraindication 字段）
 * @param patientAllergy 患者过敏史文本
 * @returns 冲突列表；空数组表示无冲突
 */
export function checkAllergy(
  items: ItemLike[],
  medicines: Map<number, MedicineLibLike> | MedicineLibLike[],
  patientAllergy?: string | null,
): AllergyConflict[] {
  const keywords = parseAllergyKeywords(patientAllergy);
  if (keywords.length === 0) return [];

  // 构建 O(1) 查找表：medicine_id → contraindication
  const contraindicationMap = new Map<number, string | null | undefined>();
  if (Array.isArray(medicines)) {
    for (const m of medicines) {
      if (m.id != null) contraindicationMap.set(m.id, m.contraindication);
    }
  } else {
    for (const [id, m] of medicines) contraindicationMap.set(id, m.contraindication);
  }

  const conflicts: AllergyConflict[] = [];

  for (const item of items) {
    // 1) 药材名直接匹配过敏关键词
    for (const kw of keywords) {
      if (item.medicine_name.includes(kw)) {
        conflicts.push({
          allergen: kw,
          medicine_name: item.medicine_name,
          matchType: 'name',
        });
        continue;
      }
    }

    // 2) 药材 contraindication 字段提及过敏关键词
    const contraindication = contraindicationMap.get(item.medicine_id);
    if (contraindication) {
      for (const kw of keywords) {
        if (contraindication.includes(kw)) {
          // 避免与"名称命中"重复
          const already = conflicts.some(
            (c) => c.medicine_name === item.medicine_name && c.allergen === kw,
          );
          if (!already) {
            conflicts.push({
              allergen: kw,
              medicine_name: item.medicine_name,
              matchType: 'contraindication',
            });
          }
        }
      }
    }
  }

  return conflicts;
}
