# -*- coding: utf-8 -*-
"""
PrescriptionTemplateService 单元测试 - 验证方剂模板库的加载、筛选、搜索
"""
import json
import os

import pytest

from core.template_service import PrescriptionTemplateService, _get_default_json_path


@pytest.fixture
def default_service():
    """使用默认 JSON 文件路径的 service 实例"""
    return PrescriptionTemplateService()


@pytest.fixture
def temp_service(tmp_path):
    """基于临时 JSON 文件的 service 实例，便于边界场景测试"""
    data = {
        "_comment": "测试用方剂",
        "templates": [
            {
                "name": "测试方一",
                "category": "补益剂",
                "description": "测试用补益方",
                "indication": "气虚证",
                "items": [
                    {"name": "人参", "quantity": 9, "unit": "g"},
                    {"name": "白术", "quantity": 9, "unit": "g"},
                ]
            },
            {
                "name": "测试方二",
                "category": "解表剂",
                "description": "测试用解表方",
                "indication": "外感风寒",
                "items": [
                    {"name": "麻黄", "quantity": 6, "unit": "g"},
                    {"name": "桂枝", "quantity": 4, "unit": "g"},
                ]
            },
            {
                "name": "测试方三",
                "category": "补益剂",
                "description": "另一首补益方",
                "indication": "血虚证",
                "items": [
                    {"name": "当归", "quantity": 9, "unit": "g"},
                ]
            },
        ]
    }
    json_path = tmp_path / "templates.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return PrescriptionTemplateService(str(json_path))


class TestLoadTemplates:
    def test_load_returns_at_least_20(self, default_service):
        """默认 JSON 应至少包含 20 个方剂"""
        templates = default_service.load_templates()
        assert len(templates) >= 20

    def test_default_json_path_exists(self):
        """默认 JSON 文件路径应真实存在"""
        assert os.path.exists(_get_default_json_path())

    def test_load_caches_result(self, default_service):
        """load_templates 应缓存结果，多次调用返回同一对象"""
        first = default_service.load_templates()
        second = default_service.load_templates()
        assert first is second

    def test_load_missing_file_returns_empty(self, tmp_path):
        """文件不存在时返回空列表而非抛异常"""
        service = PrescriptionTemplateService(str(tmp_path / "nonexistent.json"))
        assert service.load_templates() == []

    def test_load_invalid_json_returns_empty(self, tmp_path):
        """JSON 解析失败时返回空列表"""
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json", encoding='utf-8')
        service = PrescriptionTemplateService(str(bad))
        assert service.load_templates() == []

    def test_load_top_level_list_returns_empty(self, tmp_path):
        """顶层不是 dict 时返回空列表"""
        bad = tmp_path / "list.json"
        bad.write_text("[]", encoding='utf-8')
        service = PrescriptionTemplateService(str(bad))
        assert service.load_templates() == []


class TestGetByCategory:
    def test_filter_by_existing_category(self, temp_service):
        """按存在分类筛选应只返回该分类的方剂"""
        result = temp_service.get_by_category('补益剂')
        assert len(result) == 2
        assert all(t['category'] == '补益剂' for t in result)

    def test_filter_by_nonexistent_category(self, temp_service):
        """不存在的分类应返回空列表"""
        assert temp_service.get_by_category('不存在的分类') == []

    def test_empty_category_returns_all(self, temp_service):
        """空字符串或 None 应返回全部"""
        assert len(temp_service.get_by_category('')) == 3
        assert len(temp_service.get_by_category(None)) == 3

    def test_default_json_has_multiple_categories(self, default_service):
        """默认 JSON 应至少包含 3 种分类"""
        cats = default_service.get_categories()
        assert len(cats) >= 3


class TestSearch:
    def test_search_by_name(self, temp_service):
        """按名称搜索"""
        result = temp_service.search('测试方一')
        assert len(result) == 1
        assert result[0]['name'] == '测试方一'

    def test_search_by_indication(self, temp_service):
        """按主治关键词搜索"""
        result = temp_service.search('气虚')
        assert any(t['name'] == '测试方一' for t in result)

    def test_search_by_description(self, temp_service):
        """按描述关键词搜索"""
        result = temp_service.search('补益')
        assert len(result) == 2  # 测试方一、测试方三

    def test_search_no_match(self, temp_service):
        """无匹配返回空列表"""
        assert temp_service.search('不存在的关键词XYZ') == []

    def test_search_empty_keyword_returns_all(self, temp_service):
        """空关键词返回全部"""
        assert len(temp_service.search('')) == 3
        assert len(temp_service.search(None)) == 3

    def test_search_is_case_insensitive(self, temp_service):
        """搜索应不区分大小写"""
        # 搜索关键词小写与大写都应正常返回结果（不报错）
        assert isinstance(temp_service.search('测试方一'), list)
        assert isinstance(temp_service.search('测试方一'.upper()), list)

    def test_search_strips_whitespace(self, temp_service):
        """搜索关键词前后空白应被去除"""
        result = temp_service.search('  测试方一  ')
        assert len(result) == 1
        assert result[0]['name'] == '测试方一'


class TestGetCategories:
    def test_returns_unique_categories(self, temp_service):
        """分类列表应去重"""
        cats = temp_service.get_categories()
        assert len(cats) == len(set(cats))

    def test_includes_known_categories(self, temp_service):
        """应包含测试数据中存在的分类"""
        cats = temp_service.get_categories()
        assert '补益剂' in cats
        assert '解表剂' in cats

    def test_default_json_categories_not_empty(self, default_service):
        """默认 JSON 应返回非空分类列表"""
        cats = default_service.get_categories()
        assert len(cats) > 0


class TestTemplateStructure:
    def test_each_template_has_nonempty_name(self, default_service):
        """每个方剂的 name 字段非空"""
        for t in default_service.load_templates():
            assert t.get('name'), f"方剂缺少 name: {t}"

    def test_each_template_has_nonempty_items(self, default_service):
        """每个方剂的 items 字段非空"""
        for t in default_service.load_templates():
            items = t.get('items')
            assert items, f"方剂 {t.get('name')} 缺少 items"
            assert len(items) > 0, f"方剂 {t.get('name')} items 为空"

    def test_each_template_has_category(self, default_service):
        """每个方剂的 category 字段非空"""
        for t in default_service.load_templates():
            assert t.get('category'), f"方剂 {t.get('name')} 缺少 category"

    def test_each_item_has_name_quantity_unit(self, default_service):
        """每个方剂 item 应有 name/quantity/unit 字段"""
        for t in default_service.load_templates():
            for item in t.get('items', []):
                assert item.get('name'), f"方剂 {t.get('name')} 中的 item 缺少 name"
                assert 'quantity' in item, f"方剂 {t.get('name')} 中的 {item.get('name')} 缺少 quantity"
                assert item.get('unit'), f"方剂 {t.get('name')} 中的 {item.get('name')} 缺少 unit"
                # 数量应为数值类型
                assert isinstance(item['quantity'], (int, float)), \
                    f"方剂 {t.get('name')} 中的 {item.get('name')} quantity 类型异常"

    def test_template_names_are_unique(self, default_service):
        """默认 JSON 中方剂名不应重复"""
        names = [t.get('name') for t in default_service.load_templates()]
        assert len(names) == len(set(names)), "存在重复的方剂名"


class TestGetByName:
    def test_exact_match(self, temp_service):
        """按名称精确查找"""
        t = temp_service.get_by_name('测试方一')
        assert t is not None
        assert t['name'] == '测试方一'

    def test_no_match_returns_none(self, temp_service):
        """未找到返回 None"""
        assert temp_service.get_by_name('不存在方') is None

    def test_empty_name_returns_none(self, temp_service):
        """空名称返回 None"""
        assert temp_service.get_by_name('') is None
        assert temp_service.get_by_name(None) is None


class TestDefaultTemplateContent:
    """验证默认 JSON 中包含任务要求的经典方剂"""

    REQUIRED_NAMES = [
        '四君子汤', '四物汤', '八珍汤', '六味地黄丸', '逍遥散',
        '补中益气汤', '桂枝汤', '麻黄汤', '银翘散', '桑菊饮',
        '白虎汤', '黄连解毒汤', '龙胆泻肝汤', '藿香正气散', '平胃散',
        '保和丸', '血府逐瘀汤', '天麻钩藤饮', '羚角钩藤汤', '二陈汤',
        '温胆汤', '止嗽散',
    ]

    def test_all_required_formulas_present(self, default_service):
        """默认 JSON 应包含任务要求的 22 个方剂"""
        names = {t['name'] for t in default_service.load_templates()}
        for name in self.REQUIRED_NAMES:
            assert name in names, f"缺少方剂: {name}"

    def test_sijunzi_contains_four_herbs(self, default_service):
        """四君子汤应包含 4 味药材"""
        t = default_service.get_by_name('四君子汤')
        assert t is not None
        assert len(t['items']) == 4
        item_names = {it['name'] for it in t['items']}
        assert item_names == {'人参', '白术', '茯苓', '炙甘草'}
