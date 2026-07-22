# -*- coding: utf-8 -*-
"""
配伍禁忌检查模块 - 十八反、十九畏

基于中医传统配伍禁忌理论，检查处方中是否存在冲突的药材组合。
匹配采用"包含"策略，以兼容炮制前后缀（如"生甘草"、"炙甘草"均匹配"甘草"）。

规则外置到 data/compatibility_rules.json，可在不修改代码的前提下动态调整。
若 JSON 文件加载失败，回退到内置硬编码规则，保证系统可用性。
"""
import json
import logging
import os
from typing import Dict, List, Tuple

logger = logging.getLogger('MedicineSystem')

# 内置硬编码规则（fallback，与 compatibility_rules.json 保持一致）
_FALLBACK_PAIRS: List[Tuple[str, str]] = [
    # 十八反 - 甘草反甘遂、大戟、海藻、芫花
    ('甘草', '甘遂'), ('甘草', '大戟'), ('甘草', '海藻'), ('甘草', '芫花'),
    # 十八反 - 乌头（川乌、草乌、附子）反贝母、瓜蒌、半夏、白蔹、白及
    ('乌头', '贝母'), ('乌头', '瓜蒌'), ('乌头', '半夏'), ('乌头', '白蔹'), ('乌头', '白及'),
    ('川乌', '贝母'), ('川乌', '瓜蒌'), ('川乌', '半夏'), ('川乌', '白蔹'), ('川乌', '白及'),
    ('草乌', '贝母'), ('草乌', '瓜蒌'), ('草乌', '半夏'), ('草乌', '白蔹'), ('草乌', '白及'),
    ('附子', '贝母'), ('附子', '瓜蒌'), ('附子', '半夏'), ('附子', '白蔹'), ('附子', '白及'),
    # 十八反 - 藜芦反人参、沙参、丹参、玄参、苦参、细辛、芍药
    ('藜芦', '人参'), ('藜芦', '沙参'), ('藜芦', '丹参'), ('藜芦', '玄参'),
    ('藜芦', '苦参'), ('藜芦', '细辛'), ('藜芦', '芍药'),
    # 十九畏
    ('硫黄', '朴硝'),
    ('水银', '砒霜'),
    ('狼毒', '密陀僧'),
    ('巴豆', '牵牛'),
    ('丁香', '郁金'),
    ('川乌', '犀角'),
    ('草乌', '犀角'),
    ('牙硝', '三棱'),
    ('官桂', '石脂'),
    ('人参', '五灵脂'),
]


def _get_rules_file_path() -> str:
    """获取配伍规则 JSON 文件的绝对路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'data', 'compatibility_rules.json')


def _load_incompatible_pairs() -> List[Tuple[str, str]]:
    """从 JSON 文件加载禁忌配对；加载失败时回退到内置硬编码规则"""
    rules_path = _get_rules_file_path()
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        pairs = [
            (item['a'], item['b'])
            for item in data.get('pairs', [])
            if 'a' in item and 'b' in item
        ]
        if not pairs:
            logger.warning(f"配伍规则文件 {rules_path} 中无有效配对，使用内置规则")
            return _FALLBACK_PAIRS
        return pairs
    except FileNotFoundError:
        logger.warning(f"配伍规则文件不存在: {rules_path}，使用内置规则")
        return _FALLBACK_PAIRS
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"配伍规则文件解析失败: {e}，使用内置规则")
        return _FALLBACK_PAIRS
    except Exception as e:
        logger.error(f"加载配伍规则异常: {e}，使用内置规则")
        return _FALLBACK_PAIRS


# 模块加载时初始化（仅一次）
INCOMPATIBLE_PAIRS: List[Tuple[str, str]] = _load_incompatible_pairs()


def reload_rules() -> None:
    """重新加载配伍规则（运行时修改 JSON 后调用，便于热更新）"""
    global INCOMPATIBLE_PAIRS
    INCOMPATIBLE_PAIRS = _load_incompatible_pairs()


def _normalize(name: str) -> str:
    """标准化药材名称：去空白、转小写"""
    return (name or '').strip().lower()


def _matches(name: str, keyword: str) -> bool:
    """判断药材名是否包含关键词（兼容炮制前后缀，如"生甘草"匹配"甘草"）"""
    return keyword in _normalize(name)


def check_pair(name_a: str, name_b: str) -> bool:
    """判断两味药是否构成配伍禁忌"""
    for kw_a, kw_b in INCOMPATIBLE_PAIRS:
        if (_matches(name_a, kw_a) and _matches(name_b, kw_b)) or \
           (_matches(name_a, kw_b) and _matches(name_b, kw_a)):
            return True
    return False


def check_compatibility(medicine_names: List[str]) -> List[Dict[str, str]]:
    """
    检查处方药材列表中的配伍禁忌。

    Args:
        medicine_names: 处方中所有药材名称列表

    Returns:
        冲突列表，每项包含:
        - medicine1: 药材1名称
        - medicine2: 药材2名称
        - description: 冲突描述
    """
    conflicts: List[Dict[str, str]] = []
    n = len(medicine_names)

    for i in range(n):
        for j in range(i + 1, n):
            name_a = medicine_names[i]
            name_b = medicine_names[j]
            if check_pair(name_a, name_b):
                conflicts.append({
                    'medicine1': name_a,
                    'medicine2': name_b,
                    'description': f'"{name_a}" 与 "{name_b}" 存在配伍禁忌（十八反/十九畏）'
                })

    return conflicts


def check_against_existing(new_name: str, existing_names: List[str]) -> List[Dict[str, str]]:
    """
    检查新增药材与已有药材列表的配伍禁忌。

    Args:
        new_name: 待添加的药材名称
        existing_names: 处方中已有的药材名称列表

    Returns:
        冲突列表
    """
    conflicts: List[Dict[str, str]] = []
    for existing in existing_names:
        if check_pair(new_name, existing):
            conflicts.append({
                'medicine1': new_name,
                'medicine2': existing,
                'description': f'"{new_name}" 与 "{existing}" 存在配伍禁忌（十八反/十九畏）'
            })
    return conflicts
