from typing import List, Dict, Any, Optional
from medicines_data_300 import medicines_300


class MedicineQueryService:
    def __init__(self):
        self.medicines = medicines_300
        self._build_indexes()
    
    def _build_indexes(self):
        self._name_index = {m['name']: m for m in self.medicines}
        self._alias_index = {}
        for m in self.medicines:
            if m.get('alias'):
                for alias in m['alias'].split('、'):
                    self._alias_index[alias.strip()] = m
        self._category_index = {}
        for m in self.medicines:
            cat = m.get('category', '未分类')
            if cat not in self._category_index:
                self._category_index[cat] = []
            self._category_index[cat].append(m)
        self._nature_index = {}
        for m in self.medicines:
            nature = m.get('nature', '')
            if nature not in self._nature_index:
                self._nature_index[nature] = []
            self._nature_index[nature].append(m)
        self._taste_index = {}
        for m in self.medicines:
            taste = m.get('taste', '')
            if taste:
                for t in taste.replace('、', ',').split(','):
                    t = t.strip()
                    if t and t not in self._taste_index:
                        self._taste_index[t] = []
                    if t:
                        self._taste_index[t].append(m)
        self._meridian_index = {}
        for m in self.medicines:
            meridian = m.get('meridian', '')
            if meridian:
                for mer in meridian.replace('归', '').replace('经', '').split('、'):
                    mer = mer.strip()
                    if mer and mer not in self._meridian_index:
                        self._meridian_index[mer] = []
                    if mer:
                        self._meridian_index[mer].append(m)
    
    def get_all(self) -> List[Dict[str, Any]]:
        return self.medicines
    
    def get_count(self) -> int:
        return len(self.medicines)
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        result = self._name_index.get(name)
        if result:
            return result
        return self._alias_index.get(name)
    
    def search_by_name(self, keyword: str) -> List[Dict[str, Any]]:
        keyword = keyword.lower()
        results = []
        for m in self.medicines:
            if keyword in m['name'].lower():
                results.append(m)
            elif m.get('alias') and keyword in m['alias'].lower():
                results.append(m)
        return results
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        return self._category_index.get(category, [])
    
    def get_categories(self) -> List[str]:
        return list(self._category_index.keys())
    
    def get_by_nature(self, nature: str) -> List[Dict[str, Any]]:
        return self._nature_index.get(nature, [])
    
    def get_natures(self) -> List[str]:
        return list(self._nature_index.keys())
    
    def get_by_taste(self, taste: str) -> List[Dict[str, Any]]:
        return self._taste_index.get(taste, [])
    
    def get_tastes(self) -> List[str]:
        return list(self._taste_index.keys())
    
    def get_by_meridian(self, meridian: str) -> List[Dict[str, Any]]:
        return self._meridian_index.get(meridian, [])
    
    def get_meridians(self) -> List[str]:
        return list(self._meridian_index.keys())
    
    def search_by_efficacy(self, keyword: str) -> List[Dict[str, Any]]:
        keyword = keyword.lower()
        results = []
        for m in self.medicines:
            if m.get('efficacy') and keyword in m['efficacy'].lower():
                results.append(m)
        return results
    
    def search_by_indication(self, keyword: str) -> List[Dict[str, Any]]:
        keyword = keyword.lower()
        results = []
        for m in self.medicines:
            if m.get('indications') and keyword in m['indications'].lower():
                results.append(m)
        return results
    
    def advanced_search(self, 
                       name: str = None,
                       category: str = None,
                       nature: str = None,
                       taste: str = None,
                       meridian: str = None,
                       efficacy: str = None,
                       indication: str = None) -> List[Dict[str, Any]]:
        results = self.medicines
        if name:
            name = name.lower()
            results = [m for m in results if name in m['name'].lower() or 
                      (m.get('alias') and name in m['alias'].lower())]
        if category:
            results = [m for m in results if m.get('category') == category]
        if nature:
            results = [m for m in results if m.get('nature') == nature]
        if taste:
            taste = taste.lower()
            results = [m for m in results if m.get('taste') and taste in m['taste'].lower()]
        if meridian:
            meridian = meridian.lower()
            results = [m for m in results if m.get('meridian') and meridian in m['meridian'].lower()]
        if efficacy:
            efficacy = efficacy.lower()
            results = [m for m in results if m.get('efficacy') and efficacy in m['efficacy'].lower()]
        if indication:
            indication = indication.lower()
            results = [m for m in results if m.get('indications') and indication in m['indications'].lower()]
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            'total': len(self.medicines),
            'by_category': {k: len(v) for k, v in self._category_index.items()},
            'by_nature': {k: len(v) for k, v in self._nature_index.items()}
        }


def validate_medicine_data(medicine: Dict[str, Any]) -> List[str]:
    errors = []
    required_fields = ['name', 'category', 'nature', 'taste', 'meridian', 'efficacy', 'indications']
    for field in required_fields:
        if not medicine.get(field):
            errors.append(f"缺少必填字段: {field}")
    valid_natures = ['寒', '热', '温', '凉', '平', '微寒', '微温', '大寒', '大热']
    if medicine.get('nature') and medicine['nature'] not in valid_natures:
        errors.append(f"药性值无效: {medicine['nature']}")
    return errors


def validate_all_medicines() -> Dict[str, List[str]]:
    errors = {}
    for m in medicines_300:
        med_errors = validate_medicine_data(m)
        if med_errors:
            errors[m.get('name', '未知')] = med_errors
    return errors


medicine_service = MedicineQueryService()
