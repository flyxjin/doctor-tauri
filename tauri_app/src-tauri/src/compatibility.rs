// 配伍禁忌检查 - 十八反、十九畏
//
// 基于中医传统配伍禁忌理论，检查处方中是否存在冲突的药材组合。
// 匹配采用"包含"策略，以兼容炮制前后缀（如"生甘草"、"炙甘草"均匹配"甘草"）。
// 规则与原 Python 项目 core/compatibility.py 完全一致。

use crate::models::CompatibilityConflict;

/// 十八反、十九畏禁忌配对（双向禁忌）
///
/// 完整保留：
/// - 十八反·甘草反甘遂/大戟/海藻/芫花（4 对）
/// - 十八反·乌头（川乌/草乌/附子）反贝母/瓜蒌/半夏/白蔹/白及（20 对）
/// - 十八反·藜芦反人参/沙参/丹参/玄参/苦参/细辛/芍药（7 对）
/// - 十九畏（10 对）
pub const INCOMPATIBLE_PAIRS: &[(&str, &str)] = &[
    // 十八反 - 甘草反甘遂、大戟、海藻、芫花
    ("甘草", "甘遂"),
    ("甘草", "大戟"),
    ("甘草", "海藻"),
    ("甘草", "芫花"),
    // 十八反 - 乌头（川乌、草乌、附子）反贝母、瓜蒌、半夏、白蔹、白及
    ("乌头", "贝母"),
    ("乌头", "瓜蒌"),
    ("乌头", "半夏"),
    ("乌头", "白蔹"),
    ("乌头", "白及"),
    ("川乌", "贝母"),
    ("川乌", "瓜蒌"),
    ("川乌", "半夏"),
    ("川乌", "白蔹"),
    ("川乌", "白及"),
    ("草乌", "贝母"),
    ("草乌", "瓜蒌"),
    ("草乌", "半夏"),
    ("草乌", "白蔹"),
    ("草乌", "白及"),
    ("附子", "贝母"),
    ("附子", "瓜蒌"),
    ("附子", "半夏"),
    ("附子", "白蔹"),
    ("附子", "白及"),
    // 十八反 - 藜芦反人参、沙参、丹参、玄参、苦参、细辛、芍药
    ("藜芦", "人参"),
    ("藜芦", "沙参"),
    ("藜芦", "丹参"),
    ("藜芦", "玄参"),
    ("藜芦", "苦参"),
    ("藜芦", "细辛"),
    ("藜芦", "芍药"),
    // 十九畏
    ("硫黄", "朴硝"),
    ("水银", "砒霜"),
    ("狼毒", "密陀僧"),
    ("巴豆", "牵牛"),
    ("丁香", "郁金"),
    ("川乌", "犀角"),
    ("草乌", "犀角"),
    ("牙硝", "三棱"),
    ("官桂", "石脂"),
    ("人参", "五灵脂"),
];

/// 标准化药材名称：去首尾空白并转小写，与原 Python 项目保持一致
fn normalize(name: &str) -> String {
    name.trim().to_lowercase()
}

/// 判断药材名是否包含关键词（兼容炮制前后缀，如"生甘草"匹配"甘草"）
fn matches(name: &str, keyword: &str) -> bool {
    normalize(name).contains(&normalize(keyword))
}

/// 判断两味药是否构成配伍禁忌
pub fn check_pair(name_a: &str, name_b: &str) -> bool {
    for (kw_a, kw_b) in INCOMPATIBLE_PAIRS {
        if (matches(name_a, kw_a) && matches(name_b, kw_b))
            || (matches(name_a, kw_b) && matches(name_b, kw_a))
        {
            return true;
        }
    }
    false
}

/// 检查处方药材列表中的配伍禁忌
///
/// 返回冲突列表，每项包含 medicine1 / medicine2 / description
pub fn check_compatibility(medicine_names: &[String]) -> Vec<CompatibilityConflict> {
    let mut conflicts = Vec::new();
    let n = medicine_names.len();
    for i in 0..n {
        for j in (i + 1)..n {
            let name_a = &medicine_names[i];
            let name_b = &medicine_names[j];
            if check_pair(name_a, name_b) {
                conflicts.push(CompatibilityConflict {
                    medicine1: name_a.clone(),
                    medicine2: name_b.clone(),
                    description: format!(
                        "\"{}\" 与 \"{}\" 存在配伍禁忌（十八反/十九畏）",
                        name_a, name_b
                    ),
                });
            }
        }
    }
    conflicts
}

#[cfg(test)]
mod tests {
    use super::*;

    // ==================== 甘草反甘遂/大戟/海藻/芫花（4 个独立测试） ====================

    #[test]
    fn test_licorice_incompatible_with_gansui() {
        // 十八反：甘草反甘遂（双向禁忌）
        assert!(check_pair("甘草", "甘遂"));
        assert!(check_pair("甘遂", "甘草"));
    }

    #[test]
    fn test_licorice_incompatible_with_daji() {
        // 十八反：甘草反大戟（双向禁忌）
        assert!(check_pair("甘草", "大戟"));
        assert!(check_pair("大戟", "甘草"));
    }

    #[test]
    fn test_licorice_incompatible_with_haizao() {
        // 十八反：甘草反海藻（双向禁忌）
        assert!(check_pair("甘草", "海藻"));
        assert!(check_pair("海藻", "甘草"));
    }

    #[test]
    fn test_licorice_incompatible_with_yuanhua() {
        // 十八反：甘草反芫花（双向禁忌）
        assert!(check_pair("甘草", "芫花"));
        assert!(check_pair("芫花", "甘草"));
    }

    // ==================== 乌头类反（4 个测试，验证十八反中乌头类的 3 种变体） ====================

    #[test]
    fn test_wutou_incompatible_with_beimu() {
        // 十八反：乌头（通用名）反贝母
        assert!(check_pair("乌头", "贝母"));
        assert!(check_pair("贝母", "乌头"));
    }

    #[test]
    fn test_chuanwu_incompatible_with_banxia() {
        // 十八反：川乌反半夏
        assert!(check_pair("川乌", "半夏"));
        assert!(check_pair("半夏", "川乌"));
    }

    #[test]
    fn test_caowu_incompatible_with_bailian() {
        // 十八反：草乌反白蔹
        assert!(check_pair("草乌", "白蔹"));
        assert!(check_pair("白蔹", "草乌"));
    }

    #[test]
    fn test_fuzi_incompatible_with_baiji() {
        // 十八反：附子反白及
        assert!(check_pair("附子", "白及"));
        assert!(check_pair("白及", "附子"));
    }

    // ==================== 藜芦反人参、芍药（2 个测试） ====================

    #[test]
    fn test_lilu_incompatible_with_renshen() {
        // 十八反：藜芦反人参
        assert!(check_pair("藜芦", "人参"));
        assert!(check_pair("人参", "藜芦"));
    }

    #[test]
    fn test_lilu_incompatible_with_shaoyao() {
        // 十八反：藜芦反芍药
        assert!(check_pair("藜芦", "芍药"));
        assert!(check_pair("芍药", "藜芦"));
    }

    // ==================== 十九畏（3 个测试） ====================

    #[test]
    fn test_nineteen_avoidance_liuhuang_poxiao() {
        // 十九畏：硫黄畏朴硝
        assert!(check_pair("硫黄", "朴硝"));
        assert!(check_pair("朴硝", "硫黄"));
    }

    #[test]
    fn test_nineteen_avoidance_badou_qianniu() {
        // 十九畏：巴豆畏牵牛
        assert!(check_pair("巴豆", "牵牛"));
        assert!(check_pair("牵牛", "巴豆"));
    }

    #[test]
    fn test_nineteen_avoidance_renshen_wulingzhi() {
        // 十九畏：人参畏五灵脂
        assert!(check_pair("人参", "五灵脂"));
        assert!(check_pair("五灵脂", "人参"));
    }

    // ==================== 炮制前后缀匹配 ====================

    #[test]
    fn test_processing_prefix_suffix_conflict() {
        // 生甘草与甘遂应冲突（"生甘草" 包含 "甘草"）
        assert!(check_pair("生甘草", "甘遂"));
        // 炙甘草与大戟应冲突（"炙甘草" 包含 "甘草"）
        assert!(check_pair("炙甘草", "大戟"));
        // 炮制前后缀同样适用于禁忌对的另一侧
        assert!(check_pair("甘草", "制甘遂"));
        assert!(check_pair("生甘草", "炙甘遂"));
    }

    // ==================== check_compatibility 多药材组合 ====================

    #[test]
    fn test_check_compatibility_no_conflict_returns_empty() {
        // [甘草, 人参] 无配伍禁忌，应返回空列表
        let names = vec!["甘草".to_string(), "人参".to_string()];
        let conflicts = check_compatibility(&names);
        assert!(conflicts.is_empty());
    }

    #[test]
    fn test_check_compatibility_with_conflict_returns_descriptions() {
        // [甘草, 甘遂] 有冲突，返回描述列表
        let names = vec!["甘草".to_string(), "甘遂".to_string()];
        let conflicts = check_compatibility(&names);
        assert_eq!(conflicts.len(), 1);
        assert_eq!(conflicts[0].medicine1, "甘草");
        assert_eq!(conflicts[0].medicine2, "甘遂");
        // 描述应包含双方药名及"配伍禁忌"字样
        assert!(conflicts[0].description.contains("甘草"));
        assert!(conflicts[0].description.contains("甘遂"));
        assert!(conflicts[0].description.contains("配伍禁忌"));
    }

    // ==================== 大小写/空格标准化 ====================

    #[test]
    fn test_normalize_case_and_space() {
        // '  甘草  ' 与 '甘遂' 应冲突（去首尾空白后即"甘草"）
        assert!(check_pair("  甘草  ", "甘遂"));
        // normalize 函数本身验证
        assert_eq!(normalize("  甘草  "), "甘草");
        assert_eq!(normalize("\t甘草\n"), "甘草");
        // ASCII 大小写归一化
        assert_eq!(normalize("RenShen"), "renshen");
        assert_eq!(normalize("  GAN CAO  "), "gan cao");
    }

    // ==================== 不冲突的药材组合返回 false ====================

    #[test]
    fn test_no_conflict_pair_returns_false() {
        // 甘草与人参不构成禁忌
        assert!(!check_pair("甘草", "人参"));
        assert!(!check_pair("人参", "甘草"));
        // 黄芪与当归也不冲突
        assert!(!check_pair("黄芪", "当归"));
        // 不在禁忌表中的药材组合
        assert!(!check_pair("白术", "茯苓"));
    }
}
