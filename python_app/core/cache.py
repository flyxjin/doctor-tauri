# -*- coding: utf-8 -*-
"""
缓存模块 - 高效的内存缓存机制
"""
from typing import Dict, List, Any, Optional, Callable, Generic, TypeVar
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock
import time
import hashlib

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
        for field in search_fields:
            value = medicine.get(field, '')
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
                    for field in ['name', 'alias', 'efficacy', 'indications']:
                        if keyword in med.get(field, '').lower():
                            matched_ids.add(med_id)
                            break
            
            result = [self._medicines[med_id] for med_id in matched_ids]
        
        result.sort(key=lambda x: x.get('name', ''))
        self._query_cache.set(cache_key, result)
        return result
    
    def _make_cache_key(self, keyword: str, category: str, nature: str) -> str:
        key_data = f"k:{keyword}|c:{category}|n:{nature}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def add_medicine(self, medicine: Dict[str, Any]) -> None:
        with self._lock:
            self._add_to_index(medicine)
            self._query_cache.clear()
    
    def update_medicine(self, medicine: Dict[str, Any]) -> None:
        with self._lock:
            med_id = medicine.get('id')
            if med_id in self._medicines:
                self._medicines[med_id] = medicine
                self._rebuild_index()
            else:
                self._add_to_index(medicine)
            self._query_cache.clear()
    
    def delete_medicine(self, medicine_id: int) -> None:
        with self._lock:
            if medicine_id in self._medicines:
                del self._medicines[medicine_id]
                self._rebuild_index()
            self._query_cache.clear()
    
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
    if _medicine_cache:
        _medicine_cache.clear()
        _medicine_cache = None
