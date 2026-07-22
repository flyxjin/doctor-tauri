# -*- coding: utf-8 -*-
"""
pytest 共享 fixtures
"""
import os
import shutil
import sys
import tempfile

import pytest

# 确保能导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cache import invalidate_medicine_cache
from core.database import Database


@pytest.fixture
def temp_db():
    """提供临时数据库，测试后自动清理"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    Database.reset_instance()
    db = Database(db_path)
    yield db
    db.close()
    Database.reset_instance()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def medicine_service(temp_db):
    """提供 MedicineService 实例（基于临时数据库）"""
    from core.services import MedicineService
    return MedicineService(temp_db)


@pytest.fixture(autouse=True)
def reset_cache():
    """每个测试前后清理全局缓存，避免测试间互相污染"""
    invalidate_medicine_cache()
    yield
    invalidate_medicine_cache()
