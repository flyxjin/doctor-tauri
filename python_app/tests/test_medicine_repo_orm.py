# -*- coding: utf-8 -*-
"""
MedicineRepository ORM 切换后的回归测试

验证阶段 2.2：只读方法走 SQLAlchemy ORM 后，行为与原 SQL 路径一致。
"""
from core.models import Medicine
from core.repositories import MedicineRepository
from core.services import MedicineService


def _make_med(name, **kw):
    defaults = dict(
        name=name, category='补虚药', nature='温', taste='甘',
        meridian='归脾经', efficacy='补气', indications='体虚',
    )
    defaults.update(kw)
    return Medicine(**defaults)


class TestMedicineRepoORMReads:
    """验证只读方法走 ORM 后的正确性。"""

    def test_find_all_returns_inventory_fields(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('人参'))

        repo = MedicineRepository(temp_db)
        rows = repo.find_all()
        assert len(rows) == 1
        # ORM 联查应包含库存字段
        assert rows[0]['name'] == '人参'
        assert rows[0]['quantity'] == 0
        assert rows[0]['unit'] == 'g'
        assert rows[0]['price'] == 0

    def test_find_by_id_returns_none_when_missing(self, temp_db):
        repo = MedicineRepository(temp_db)
        assert repo.find_by_id(99999) is None

    def test_find_by_name(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('黄芪'))

        repo = MedicineRepository(temp_db)
        row = repo.find_by_name('黄芪')
        assert row is not None
        assert row['id'] == med_id
        assert row['name'] == '黄芪'

    def test_find_by_name_missing(self, temp_db):
        repo = MedicineRepository(temp_db)
        assert repo.find_by_name('不存在') is None

    def test_search_multi_field(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('黄连', efficacy='清热燥湿'))
        svc.create(_make_med('黄芪', efficacy='补气升阳'))

        repo = MedicineRepository(temp_db)
        # 按 efficacy 搜索
        results = repo.search('清热', fields=['efficacy'])
        assert len(results) == 1
        assert results[0]['name'] == '黄连'

        # 默认字段搜索
        results = repo.search('黄')
        assert len(results) == 2

    def test_search_empty_keyword(self, temp_db):
        repo = MedicineRepository(temp_db)
        assert repo.search('') == []

    def test_find_categories(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('A', category='补虚药'))
        svc.create(_make_med('B', category='清热药'))
        svc.create(_make_med('C', category='补虚药'))

        repo = MedicineRepository(temp_db)
        cats = repo.find_categories()
        assert cats == ['清热药', '补虚药']  # 排序后去重

    def test_find_all_as_dicts_no_none(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('人参'))

        repo = MedicineRepository(temp_db)
        rows = repo.find_all_as_dicts()
        assert len(rows) == 1
        # 确保无 None 值（缓存要求）
        for v in rows[0].values():
            assert v is not None or isinstance(v, (int, type(rows[0]['id'])))

    def test_find_id_by_name(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('当归'))

        repo = MedicineRepository(temp_db)
        assert repo.find_id_by_name('当归') == med_id
        assert repo.find_id_by_name('不存在') is None

    def test_count_medicines(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('A'))
        svc.create(_make_med('B'))

        repo = MedicineRepository(temp_db)
        assert repo.count_medicines() == 2

    def test_find_medicines_without_inventory(self, temp_db):
        """正常路径下（insert_medicine 会建库存），不应有无库存药材。"""
        svc = MedicineService(temp_db)
        svc.create(_make_med('人参'))

        repo = MedicineRepository(temp_db)
        orphans = repo.find_medicines_without_inventory()
        assert orphans == []

    def test_find_latest_data_version_none(self, temp_db):
        repo = MedicineRepository(temp_db)
        assert repo.find_latest_data_version() is None

    def test_find_all_with_category_filter(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('A', category='补虚药'))
        svc.create(_make_med('B', category='清热药'))

        repo = MedicineRepository(temp_db)
        rows = repo.find_all(category='补虚药')
        assert len(rows) == 1
        assert rows[0]['name'] == 'A'

    def test_find_all_with_keyword(self, temp_db):
        svc = MedicineService(temp_db)
        svc.create(_make_med('人参', alias='黄参'))
        svc.create(_make_med('黄芪', alias='黄耆'))

        repo = MedicineRepository(temp_db)
        rows = repo.find_all(keyword='黄')
        assert len(rows) == 2


class TestMedicineRepoORMMixed:
    """验证 ORM 只读 + SQL 写的混合工作正常（事务边界兼容）。"""

    def test_create_then_read_via_orm(self, temp_db):
        """SQL 写入后，ORM 读取应能立即看到（不同连接，但同一文件）。"""
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('测试混合'))

        repo = MedicineRepository(temp_db)
        # SQL 写已 commit（Service.create 内部），ORM 读应看到
        row = repo.find_by_id(med_id)
        assert row is not None
        assert row['name'] == '测试混合'

    def test_delete_then_read_via_orm(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('待删'))

        svc.delete(med_id)

        repo = MedicineRepository(temp_db)
        assert repo.find_by_id(med_id) is None
        assert repo.count_medicines() == 0
