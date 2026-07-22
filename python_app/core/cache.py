# -*- coding: utf-8 -*-
"""
缓存模块 - 高效的内存缓存机制
"""
import time
from collections import OrderedDict
from threading import RLock
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

T = TypeVar('T')


class CacheEntry(Generic[T]):
    __slots__ = ('value', 'expires_at', 'hit_count', 'created_at', 'last_accessed')

    def __init__(self, value: T, ttl: float = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.hit_count = 0
        self.expires_at = None
        if ttl is not None:
            self.expires_at = self.created_at + ttl

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def access(self) -> T:
        self.last_accessed = time.time()
        self.hit_count += 1
        return self.value


class LRUCache(Generic[T]):
    def __init__(self, max_size: int = 1000, default_ttl: float = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[T]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None

            self._cache.move_to_end(key)
            self._hits += 1
            return entry.access()

    def set(self, key: str, value: T, ttl: float = None) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            elif len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            actual_ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, actual_ttl)

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)

    def delete_if(self, predicate: Callable[[str], bool]) -> int:
        """删除所有满足谓词的缓存项，返回删除数量。

        用于定向失效：传入判断 key 是否受影响的函数，避免全量 clear 造成的抖动。
        """
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if predicate(k)]
            for k in keys_to_delete:
                del self._cache[k]
            return len(keys_to_delete)

    def keys(self) -> List[str]:
        """返回当前所有缓存 key 的快照"""
        with self._lock:
            return list(self._cache.keys())

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'total_accesses': total
            }

    def __contains__(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            return not entry.is_expired()


class MedicineCache:
    def __init__(self):
        self._medicines: Dict[int, Dict[str, Any]] = {}
        self._medicines_by_name: Dict[str, Dict[str, Any]] = {}
        self._medicines_by_category: Dict[str, List[Dict[str, Any]]] = {}
        self._search_index: Dict[str, List[int]] = {}
        self._lock = RLock()
        self._initialized = False
        self._query_cache = LRUCache[List[Dict[str, Any]]](max_size=50, default_ttl=60.0)

    def initialize(self, medicines: List[Dict[str, Any]]) -> None:
        with self._lock:
            self._clear_data()

            for medicine in medicines:
                self._add_to_index(medicine)

            self._initialized = True
            self._query_cache.clear()

    def _clear_data(self) -> None:
        self._medicines.clear()
        self._medicines_by_name.clear()
        self._medicines_by_category.clear()
        self._search_index.clear()

    def _add_to_index(self, medicine: Dict[str, Any]) -> None:
        med_id = medicine.get('id')
        name = medicine.get('name', '').lower()
        category = medicine.get('category', '')

        self._medicines[med_id] = medicine

        if name:
            self._medicines_by_name[name] = medicine

        if category:
            if category not in self._medicines_by_category:
                self._medicines_by_category[category] = []
            self._medicines_by_category[category].append(medicine)

        self._index_search_terms(medicine, med_id)

    def _index_search_terms(self, medicine: Dict[str, Any], med_id: int) -> None:
        search_fields = ['name', 'alias', 'efficacy', 'indications', 'taste', 'meridian']
        for field_name in search_fields:
            value = medicine.get(field_name, '')
            if value:
                terms = self._tokenize(value)
                for term in terms:
                    if term not in self._search_index:
                        self._search_index[term] = []
                    if med_id not in self._search_index[term]:
                        self._search_index[term].append(med_id)

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = text.replace('、', ' ').replace('，', ' ').replace(',', ' ')
        words = text.split()
        result = []
        for word in words:
            if word:
                result.append(word)
                for i in range(1, len(word)):
                    result.append(word[:i+1])
        return result

    def get_by_id(self, medicine_id: int) -> Optional[Dict[str, Any]]:
        return self._medicines.get(medicine_id)

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self._medicines_by_name.get(name.lower())

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        return self._medicines_by_category.get(category, [])

    def search(self, keyword: str, category: str = None, nature: str = None) -> List[Dict[str, Any]]:
        cache_key = self._make_cache_key(keyword, category, nature)
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            return cached

        keyword = keyword.lower()

        if not keyword and not category and not nature:
            result = list(self._medicines.values())
        else:
            matched_ids = set()

            if keyword:
                terms = self._tokenize(keyword)
                for term in terms:
                    if term in self._search_index:
                        matched_ids.update(self._search_index[term])

            if category:
                category_meds = self._medicines_by_category.get(category, [])
                category_ids = {med['id'] for med in category_meds}
                if matched_ids:
                    matched_ids.intersection_update(category_ids)
                else:
                    matched_ids = category_ids

            if nature:
                nature_ids = {
                    med_id for med_id, med in self._medicines.items()
                    if med.get('nature') == nature
                }
                if matched_ids:
                    matched_ids.intersection_update(nature_ids)
                else:
                    matched_ids = nature_ids

            if keyword and not matched_ids:
                for med_id, med in self._medicines.items():
                    for field_name in ['name', 'alias', 'efficacy', 'indications']:
                        if keyword in med.get(field_name, '').lower():
                            matched_ids.add(med_id)
                            break

            result = [self._medicines[med_id] for med_id in matched_ids]

        result.sort(key=lambda x: x.get('name', ''))
        self._query_cache.set(cache_key, result)
        return result

    def _make_cache_key(self, keyword: str, category: str, nature: str) -> str:
        return f"k:{keyword}|c:{category}|n:{nature}"

    def _invalidate_query_cache_for(self, medicine: Dict[str, Any]) -> int:
        """定向失效：删除可能受该药材变更影响的查询缓存。

        相比全量 clear，定向失效避免高频搜索场景下的缓存抖动。
        受影响范围：
        - 全量查询（无 keyword、无 category、无 nature）
        - keyword 与该药材 name/alias 任何前缀 token 相关的查询
        - category 等于该药材分类的查询
        - nature 等于该药材药性的查询
        """
        name = medicine.get('name', '') or ''
        alias = medicine.get('alias', '') or ''
        category = medicine.get('category', '') or ''
        nature = medicine.get('nature', '') or ''

        # 收集该药材的所有搜索 token（name + alias 的前缀分词）
        affected_tokens = set()
        for text in (name, alias):
            if text:
                affected_tokens.update(self._tokenize(text))
        # category / nature 本身也作为受影响 token
        if category:
            affected_tokens.add(category.lower())
        if nature:
            affected_tokens.add(nature.lower())

        # 全量查询的 key（所有过滤项为 None）
        wildcard_key = self._make_cache_key(None, None, None)

        def _is_affected(key: str) -> bool:
            if key == wildcard_key:
                return True
            # 解析 key 的三段：k:xxx|c:yyy|n:zzz
            try:
                parts = key.split('|')
                kw_part = parts[0][2:] if parts[0].startswith('k:') else parts[0]
                cat_part = parts[1][2:] if len(parts) > 1 and parts[1].startswith('c:') else ''
                nat_part = parts[2][2:] if len(parts) > 2 and parts[2].startswith('n:') else ''
            except Exception:
                return True  # 解析失败保守失效

            # keyword 为 None（全量）→ 受影响
            if kw_part == 'None' or kw_part == '':
                return True
            # keyword 是受影响 token 的子串或超串 → 可能命中该药材
            kw_lower = kw_part.lower()
            for token in affected_tokens:
                if token and (token in kw_lower or kw_lower in token):
                    return True
            # category 等于变更药材分类 → 该分类列表受影响
            if cat_part != 'None' and cat_part and cat_part.lower() == category.lower():
                return True
            # nature 等于变更药材药性 → 该药性列表受影响
            if nat_part != 'None' and nat_part and nat_part.lower() == nature.lower():
                return True
            return False

        return self._query_cache.delete_if(_is_affected)

    def add_medicine(self, medicine: Dict[str, Any]) -> None:
        with self._lock:
            self._add_to_index(medicine)
            self._invalidate_query_cache_for(medicine)

    def update_medicine(self, medicine: Dict[str, Any]) -> None:
        with self._lock:
            med_id = medicine.get('id')
            old_medicine = None
            if med_id in self._medicines:
                # 保留旧药材信息用于失效旧 token 相关的查询缓存
                old_medicine = dict(self._medicines.get(med_id) or {})
                # 先移除旧索引，再添加新索引，避免全量重建
                self._remove_from_index(med_id)
                self._add_to_index(medicine)
            else:
                self._add_to_index(medicine)
            # 先用旧药材信息失效（覆盖旧 alias/category/nature 相关查询）
            if old_medicine:
                self._invalidate_query_cache_for(old_medicine)
            # 再用新药材信息失效（覆盖新 alias/category/nature 相关查询）
            self._invalidate_query_cache_for(medicine)

    def delete_medicine(self, medicine_id: int) -> None:
        with self._lock:
            medicine = self._medicines.get(medicine_id)
            if medicine_id in self._medicines:
                self._remove_from_index(medicine_id)
            # 删除时基于被删除药材的信息做定向失效
            if medicine:
                self._invalidate_query_cache_for(medicine)
            else:
                self._query_cache.clear()

    def _remove_from_index(self, medicine_id: int) -> None:
        """从所有索引中移除指定药材（O(1) 定向移除，无需全量重建）"""
        medicine = self._medicines.pop(medicine_id, None)
        if not medicine:
            return

        name = medicine.get('name', '').lower()
        if name and self._medicines_by_name.get(name) is medicine:
            del self._medicines_by_name[name]

        category = medicine.get('category', '')
        if category and category in self._medicines_by_category:
            self._medicines_by_category[category] = [
                m for m in self._medicines_by_category[category] if m.get('id') != medicine_id
            ]
            if not self._medicines_by_category[category]:
                del self._medicines_by_category[category]

        # 从搜索索引中移除该药材 id
        for term, id_list in list(self._search_index.items()):
            if medicine_id in id_list:
                id_list.remove(medicine_id)
                if not id_list:
                    del self._search_index[term]

    def _rebuild_index(self) -> None:
        meds = list(self._medicines.values())
        self._clear_data()
        for medicine in meds:
            self._add_to_index(medicine)

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._medicines.values())

    def get_categories(self) -> List[str]:
        return sorted(self._medicines_by_category.keys())

    def is_initialized(self) -> bool:
        return self._initialized

    def get_stats(self) -> Dict[str, Any]:
        return {
            'medicine_count': len(self._medicines),
            'category_count': len(self._medicines_by_category),
            'search_terms_count': len(self._search_index),
            'query_cache': self._query_cache.get_stats()
        }


_medicine_cache: Optional[MedicineCache] = None


def get_medicine_cache() -> MedicineCache:
    global _medicine_cache
    if _medicine_cache is None:
        _medicine_cache = MedicineCache()
    return _medicine_cache


def invalidate_medicine_cache() -> None:
    global _medicine_cache
    _medicine_cache = None
