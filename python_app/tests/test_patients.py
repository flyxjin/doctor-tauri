# -*- coding: utf-8 -*-
"""
患者档案模块单元测试

覆盖：
- CRUD 操作
- 搜索功能
- 按姓名查询
- 获取处方历史
- 统计数据
- 重复姓名允许（不同人可能同名）
"""
import pytest

from core.models import Patient
from core.services import PatientService, ServiceError


def _make_patient(name='张三', **kwargs):
    """构造一个通过验证的患者对象"""
    defaults = dict(
        name=name,
        gender='男',
        age=45,
        phone='13800000000',
        address='北京市朝阳区',
        allergy='青霉素过敏',
        medical_history='高血压',
        notes='定期复诊',
    )
    defaults.update(kwargs)
    return Patient(**defaults)


@pytest.fixture
def patient_service(temp_db):
    """提供 PatientService 实例（基于临时数据库）"""
    return PatientService(temp_db)


def _insert_prescription_direct(db, patient_name, diagnosis='感冒', total_amount=100.0):
    """直接插入一条处方记录（绕过 Service 层，仅用于测试数据准备）。

    患者档案的处方历史通过 patient_name 关联，不依赖外键，
    所以可以直接插入 prescriptions 表构造测试数据。
    """
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = db.execute(
        '''INSERT INTO prescriptions
           (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (patient_name, 45, '男', diagnosis, total_amount, '测试医生', now)
    )
    return cursor.lastrowid


class TestPatientCRUD:
    """测试 CRUD 操作"""

    def test_create_and_get(self, patient_service):
        patient = _make_patient('李四')
        patient_id = patient_service.create(patient)
        assert patient_id > 0

        result = patient_service.get_by_id(patient_id)
        assert result is not None
        assert result.name == '李四'
        assert result.gender == '男'
        assert result.age == 45
        assert result.phone == '13800000000'
        assert result.allergy == '青霉素过敏'

    def test_update(self, patient_service):
        patient = _make_patient('王五')
        patient_id = patient_service.create(patient)

        patient.id = patient_id
        patient.phone = '13900000000'
        patient.notes = '已更新备注'
        patient_service.update(patient)

        result = patient_service.get_by_id(patient_id)
        assert result.phone == '13900000000'
        assert result.notes == '已更新备注'
        # 未修改的字段保持不变
        assert result.name == '王五'
        assert result.allergy == '青霉素过敏'

    def test_delete(self, patient_service):
        patient = _make_patient('赵六')
        patient_id = patient_service.create(patient)

        patient_service.delete(patient_id)
        assert patient_service.get_by_id(patient_id) is None

    def test_delete_nonexistent_raises(self, patient_service):
        with pytest.raises(ServiceError):
            patient_service.delete(99999)

    def test_update_nonexistent_raises(self, patient_service):
        patient = _make_patient('钱七')
        patient.id = 99999
        with pytest.raises(ServiceError):
            patient_service.update(patient)

    def test_create_invalid_name_raises(self, patient_service):
        patient = _make_patient('')
        with pytest.raises(ServiceError):
            patient_service.create(patient)

    def test_create_invalid_gender_raises(self, patient_service):
        patient = _make_patient('孙八', gender='未知')
        with pytest.raises(ServiceError):
            patient_service.create(patient)


class TestPatientSearch:
    """测试搜索功能"""

    def test_search_empty_returns_all(self, patient_service):
        patient_service.create(_make_patient('张三'))
        patient_service.create(_make_patient('李四'))

        results = patient_service.search()
        assert len(results) >= 2

    def test_search_by_name(self, patient_service):
        patient_service.create(_make_patient('王搜索', phone='11111111111'))
        patient_service.create(_make_patient('李搜索', phone='22222222222'))
        patient_service.create(_make_patient('赵无关', phone='33333333333'))

        results = patient_service.search('搜索')
        assert len(results) == 2
        names = {p.name for p in results}
        assert names == {'王搜索', '李搜索'}

    def test_search_by_phone(self, patient_service):
        patient_service.create(_make_patient('张电话', phone='13900000000'))
        patient_service.create(_make_patient('李其他', phone='13800000000'))

        results = patient_service.search('139')
        assert len(results) == 1
        assert results[0].name == '张电话'

    def test_search_no_match(self, patient_service):
        patient_service.create(_make_patient('张三'))
        results = patient_service.search('不存在的关键字')
        assert len(results) == 0


class TestPatientByName:
    """测试按姓名精确查询"""

    def test_get_by_name_found(self, patient_service):
        patient_service.create(_make_patient('查询患者'))
        result = patient_service.get_by_name('查询患者')
        assert result is not None
        assert result.name == '查询患者'

    def test_get_by_name_not_found(self, patient_service):
        result = patient_service.get_by_name('不存在')
        assert result is None

    def test_get_by_name_returns_first_match(self, patient_service):
        """同名患者返回第一条"""
        patient_service.create(_make_patient('同名', phone='111'))
        patient_service.create(_make_patient('同名', phone='222'))

        result = patient_service.get_by_name('同名')
        assert result is not None
        assert result.name == '同名'
        # 应返回第一条（id 较小者）
        assert result.phone == '111'


class TestPatientPrescriptions:
    """测试获取处方历史"""

    def test_get_prescriptions_empty(self, patient_service):
        patient = _make_patient('无处方')
        patient_id = patient_service.create(patient)

        prescriptions = patient_service.get_prescriptions(patient_id)
        assert prescriptions == []

    def test_get_prescriptions_with_data(self, patient_service, temp_db):
        patient = _make_patient('有处方')
        patient_id = patient_service.create(patient)

        _insert_prescription_direct(temp_db, patient_name='有处方', diagnosis='感冒', total_amount=50.0)
        _insert_prescription_direct(temp_db, patient_name='有处方', diagnosis='咳嗽', total_amount=80.0)

        prescriptions = patient_service.get_prescriptions(patient_id)
        assert len(prescriptions) == 2
        # 按时间倒序
        diagnoses = {p['diagnosis'] for p in prescriptions}
        assert diagnoses == {'感冒', '咳嗽'}
        # 每条记录应包含必要字段
        first = prescriptions[0]
        assert 'prescription_id' in first
        assert 'total_amount' in first
        assert 'created_at' in first

    def test_get_prescriptions_nonexistent_patient(self, patient_service):
        """查询不存在患者的处方应返回空列表"""
        prescriptions = patient_service.get_prescriptions(99999)
        assert prescriptions == []

    def test_get_prescriptions_filtered_by_name(self, patient_service, temp_db):
        """处方历史只返回与患者姓名匹配的处方"""
        patient = _make_patient('张三')
        patient_id = patient_service.create(patient)

        _insert_prescription_direct(temp_db, patient_name='张三', diagnosis='感冒')
        _insert_prescription_direct(temp_db, patient_name='李四', diagnosis='咳嗽')

        prescriptions = patient_service.get_prescriptions(patient_id)
        assert len(prescriptions) == 1
        assert prescriptions[0]['patient_name'] == '张三'


class TestPatientStatistics:
    """测试统计数据"""

    def test_statistics_no_prescriptions(self, patient_service):
        patient = _make_patient('无统计')
        patient_id = patient_service.create(patient)

        stats = patient_service.get_statistics(patient_id)
        assert stats['prescription_count'] == 0
        assert stats['total_amount'] == 0.0
        assert stats['first_visit'] is None
        assert stats['last_visit'] is None

    def test_statistics_with_prescriptions(self, patient_service, temp_db):
        patient = _make_patient('有统计')
        patient_id = patient_service.create(patient)

        _insert_prescription_direct(temp_db, patient_name='有统计', diagnosis='病1', total_amount=100.0)
        _insert_prescription_direct(temp_db, patient_name='有统计', diagnosis='病2', total_amount=200.0)

        stats = patient_service.get_statistics(patient_id)
        assert stats['prescription_count'] == 2
        assert stats['total_amount'] == 300.0
        assert stats['first_visit'] is not None
        assert stats['last_visit'] is not None

    def test_statistics_nonexistent_patient(self, patient_service):
        stats = patient_service.get_statistics(99999)
        assert stats['prescription_count'] == 0
        assert stats['total_amount'] == 0.0


class TestDuplicateNames:
    """测试重复姓名允许"""

    def test_create_duplicate_name_allowed(self, patient_service):
        """不同人可能同名，应允许创建"""
        p1 = _make_patient('张三', phone='11111111111')
        p2 = _make_patient('张三', phone='22222222222')

        id1 = patient_service.create(p1)
        id2 = patient_service.create(p2)

        assert id1 > 0
        assert id2 > 0
        assert id1 != id2

        # 两条记录都存在
        results = patient_service.search('张三')
        assert len(results) == 2
        phones = {p.phone for p in results}
        assert phones == {'11111111111', '22222222222'}

    def test_update_duplicate_name_allowed(self, patient_service):
        """更新姓名为已有姓名也允许（不同人可能同名）"""
        patient_service.create(_make_patient('李四', phone='111'))
        p2 = _make_patient('王五', phone='222')
        p2_id = patient_service.create(p2)

        p2.id = p2_id
        p2.name = '李四'  # 改成已存在的名字
        # 应允许，不抛异常
        patient_service.update(p2)

        result = patient_service.get_by_id(p2_id)
        assert result.name == '李四'
        assert result.phone == '222'
