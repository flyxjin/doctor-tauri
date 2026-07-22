# -*- coding: utf-8 -*-
"""
配伍禁忌检查测试 - 验证十八反、十九畏预警
"""
from core.compatibility import check_against_existing, check_compatibility, check_pair


class TestEighteenIncompatibilities:
    """十八反测试"""

    def test_licorice_group(self):
        """甘草反甘遂、大戟、海藻、芫花"""
        assert check_pair('甘草', '甘遂')
        assert check_pair('甘草', '大戟')
        assert check_pair('甘草', '海藻')
        assert check_pair('甘草', '芫花')

    def test_acomite_group(self):
        """乌头反贝母、瓜蒌、半夏、白蔹、白及"""
        assert check_pair('乌头', '半夏')
        assert check_pair('川乌', '贝母')
        assert check_pair('附子', '瓜蒌')

    def test_veratrum_group(self):
        """藜芦反人参、沙参、丹参等"""
        assert check_pair('藜芦', '人参')
        assert check_pair('藜芦', '沙参')
        assert check_pair('藜芦', '细辛')

    def test_processed_herbs_match(self):
        """炮制后缀应能匹配（如"生甘草"匹配"甘草"）"""
        assert check_pair('生甘草', '甘遂')
        assert check_pair('炙甘草', '海藻')
        assert check_pair('制川乌', '半夏')


class TestNineteenMutualAversion:
    """十九畏测试"""

    def test_classic_pairs(self):
        """经典十九畏配对"""
        assert check_pair('硫黄', '朴硝')
        assert check_pair('巴豆', '牵牛')
        assert check_pair('丁香', '郁金')
        assert check_pair('人参', '五灵脂')
        assert check_pair('官桂', '石脂')


class TestNoConflict:
    """无冲突场景测试"""

    def test_compatible_herbs(self):
        """常见配伍不应报冲突"""
        assert not check_pair('人参', '黄芪')
        assert not check_pair('当归', '川芎')
        assert not check_pair('白术', '茯苓')

    def test_same_herb_no_conflict(self):
        """相同药材不应自冲突"""
        assert not check_pair('甘草', '甘草')


class TestCheckCompatibility:
    """处方整体检查测试"""

    def test_detect_conflict_in_prescription(self):
        """处方中检测到冲突"""
        conflicts = check_compatibility(['甘草', '甘遂', '人参'])
        assert len(conflicts) == 1
        assert '甘草' in conflicts[0]['description']
        assert '甘遂' in conflicts[0]['description']

    def test_no_conflict_in_normal_prescription(self):
        """正常处方无冲突"""
        conflicts = check_compatibility(['人参', '黄芪', '当归', '白术'])
        assert len(conflicts) == 0

    def test_multiple_conflicts(self):
        """多处冲突"""
        conflicts = check_compatibility(['甘草', '甘遂', '乌头', '半夏'])
        assert len(conflicts) == 2


class TestCheckAgainstExisting:
    """新增药材检查测试"""

    def test_new_herb_conflicts_with_existing(self):
        """新药材与已有药材冲突"""
        conflicts = check_against_existing('甘遂', ['甘草', '人参'])
        assert len(conflicts) == 1
        assert conflicts[0]['medicine1'] == '甘遂'
        assert conflicts[0]['medicine2'] == '甘草'

    def test_new_herb_no_conflict(self):
        """新药材无冲突"""
        conflicts = check_against_existing('黄芪', ['人参', '当归'])
        assert len(conflicts) == 0
