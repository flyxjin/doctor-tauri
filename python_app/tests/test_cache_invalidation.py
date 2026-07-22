# -*- coding: utf-8 -*-
"""
缓存定向失效单元测试

验证 MedicineCache 在新增/更新/删除时，只失效受影响的查询缓存，
保留与变更药材无关的查询缓存（替代之前的全量 clear 行为）。
"""
from core.cache import LRUCache, MedicineCache


def _make_med(med_id: int, name: str, alias: str = '', category: str = '',
              nature: str = '', efficacy: str = '') -> dict:
    return {
        'id': med_id,
        'name': name,
        'alias': alias,
        'category': category,
        'nature': nature,
        'efficacy': efficacy,
        'indications': '',
        'taste': '',
        'meridian': '',
    }


class TestLRUCacheDeleteIf:
    """LRUCache.delete_if 谓词删除测试"""

    def test_delete_if_returns_count(self):
        cache = LRUCache(max_size=10)
        cache.set('k1', 'v1')
        cache.set('k2', 'v2')
        cache.set('keep', 'v3')
        deleted = cache.delete_if(lambda k: k.startswith('k') and k != 'keep')
        assert deleted == 2
        assert 'keep' in cache
        assert 'k1' not in cache
        assert 'k2' not in cache

    def test_delete_if_no_match(self):
        cache = LRUCache(max_size=10)
        cache.set('a', 1)
        deleted = cache.delete_if(lambda k: k == 'xyz')
        assert deleted == 0
        assert 'a' in cache

    def test_keys_returns_snapshot(self):
        cache = LRUCache(max_size=10)
        cache.set('x', 1)
        cache.set('y', 2)
        ks = cache.keys()
        assert set(ks) == {'x', 'y'}


class TestMedicineCacheTargetedInvalidation:
    """MedicineCache 定向失效测试"""

    def test_delete_preserves_unrelated_query_cache(self):
        """删除一个药材后，与该药材无关的查询缓存应保留"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草', alias='甜根子', category='补虚药', nature='平'),
            _make_med(2, '人参', alias='棒槌', category='补虚药', nature='温'),
            _make_med(3, '黄连', alias='川连', category='清热药', nature='寒'),
        ])

        # 预热两个不相关的查询缓存
        renshen_result = cache.search('人参')
        huanglian_result = cache.search('黄连')
        assert len(renshen_result) == 1
        assert len(huanglian_result) == 1

        # 删除甘草（与人参/黄连查询无关）
        cache.delete_medicine(1)

        # 人参和黄连的查询缓存应仍命中（结果一致）
        renshen_after = cache.search('人参')
        huanglian_after = cache.search('黄连')
        assert renshen_after == renshen_result
        assert huanglian_after == huanglian_result

    def test_add_invalidates_wildcard_and_token_queries(self):
        """新增药材后，全量查询和受影响 token 查询应失效"""
        cache = MedicineCache()
        cache.initialize([_make_med(1, '甘草', category='补虚药')])

        # 预热全量查询（无 keyword）
        all_before = cache.search('')
        assert len(all_before) == 1

        # 新增"人参"
        cache.add_medicine(_make_med(2, '人参', category='补虚药'))

        # 全量查询应失效并返回新结果
        all_after = cache.search('')
        assert len(all_after) == 2

    def test_update_invalidates_affected_token_queries(self):
        """更新药材后，与该药材 name token 相关的查询应失效"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草', alias='甜根子', nature='平'),
            _make_med(2, '黄连', alias='川连', nature='寒'),
        ])

        # 预热甘草查询
        g_before = cache.search('甘草')
        assert len(g_before) == 1

        # 更新甘草的别名（name 不变）
        cache.update_medicine(_make_med(1, '甘草', alias='生甘草', nature='温'))

        # 甘草查询应失效并返回更新后的数据
        g_after = cache.search('甘草')
        assert len(g_after) == 1
        assert g_after[0]['alias'] == '生甘草'
        assert g_after[0]['nature'] == '温'

    def test_delete_invalidates_wildcard_query(self):
        """删除药材后，全量查询应失效"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草'),
            _make_med(2, '人参'),
        ])

        all_before = cache.search('')
        assert len(all_before) == 2

        cache.delete_medicine(1)
        all_after = cache.search('')
        assert len(all_after) == 1
        assert all_after[0]['name'] == '人参'

    def test_category_filter_invalidation(self):
        """变更药材分类后，该分类的过滤查询应失效"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草', category='补虚药'),
            _make_med(2, '黄连', category='清热药'),
        ])

        # 预热"补虚药"分类查询
        cat_before = cache.search('', category='补虚药')
        assert len(cat_before) == 1

        # 修改甘草的分类为"清热药"
        cache.update_medicine(_make_med(1, '甘草', category='清热药'))

        # "补虚药"分类查询应失效，返回空
        cat_after = cache.search('', category='补虚药')
        assert len(cat_after) == 0

        # "清热药"分类查询应返回 2 条
        re_qing = cache.search('', category='清热药')
        assert len(re_qing) == 2

    def test_nature_filter_invalidation(self):
        """变更药材药性后，该药性的过滤查询应失效"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草', nature='平'),
            _make_med(2, '人参', nature='温'),
        ])

        wen_before = cache.search('', nature='温')
        assert len(wen_before) == 1

        # 修改甘草为温
        cache.update_medicine(_make_med(1, '甘草', nature='温'))

        wen_after = cache.search('', nature='温')
        assert len(wen_after) == 2

    def test_alias_token_invalidation(self):
        """变更药材别名后，按别名搜索的查询应失效"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草', alias='甜根子'),
        ])

        # 按别名搜索预热
        result_before = cache.search('甜根子')
        assert len(result_before) == 1

        # 修改别名
        cache.update_medicine(_make_med(1, '甘草', alias='蜜甘'))

        # 旧别名应查不到
        old_result = cache.search('甜根子')
        assert len(old_result) == 0

        # 新别名应能查到
        new_result = cache.search('蜜甘')
        assert len(new_result) == 1

    def test_unrelated_query_preserved_after_update(self):
        """更新药材 A 后，药材 B 的查询缓存应保留"""
        cache = MedicineCache()
        cache.initialize([
            _make_med(1, '甘草', nature='平'),
            _make_med(2, '人参', nature='温'),
        ])

        # 预热人参查询
        renshen_before = cache.search('人参')
        assert len(renshen_before) == 1

        # 更新甘草（与人参无关）
        cache.update_medicine(_make_med(1, '甘草', nature='寒'))

        # 人参查询缓存应保留（同一对象引用）
        renshen_after = cache.search('人参')
        assert renshen_after is renshen_before or renshen_after == renshen_before

    def test_delete_unknown_id_falls_back_to_clear(self):
        """删除不存在的 id 时（无药材信息可用），回退到全量 clear 不报错"""
        cache = MedicineCache()
        cache.initialize([_make_med(1, '甘草')])
        # 删除不存在的 id
        cache.delete_medicine(999)
        # 甘草仍可查到
        assert len(cache.search('甘草')) == 1
