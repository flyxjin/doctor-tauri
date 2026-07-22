# -*- coding: utf-8 -*-
"""
处方模板服务 - 管理经典方剂模板库

从 core/data/prescription_templates.json 加载经典方剂数据，提供
加载、分类筛选、关键词搜索等只读 API，供处方开具页快速调用。

设计原则：
- 纯只读服务，不依赖数据库，不参与处方写入流程
- JSON 文件外置，可在不修改代码的前提下扩展方剂
- 加载失败时回退到空列表，由调用方决定如何提示用户
"""
import json
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger('MedicineSystem')


def _get_default_json_path() -> str:
    """获取默认方剂模板 JSON 文件的绝对路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'data', 'prescription_templates.json')


class PrescriptionTemplateService:
    """处方方剂模板服务"""

    def __init__(self, json_path: Optional[str] = None):
        self.json_path = json_path or _get_default_json_path()
        # 模块级缓存：JSON 文件只在首次加载时读取一次
        self._templates: Optional[List[Dict]] = None

    def load_templates(self) -> List[Dict]:
        """加载所有模板。

        Returns:
            方剂列表，每项包含 name/category/description/indication/items 字段。
            加载失败时返回空列表，并记录日志。
        """
        if self._templates is not None:
            return self._templates

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            templates = data.get('templates', []) if isinstance(data, dict) else []
            self._templates = templates
            logger.info(f"加载方剂模板 {len(templates)} 个: {self.json_path}")
            return templates
        except FileNotFoundError:
            logger.warning(f"方剂模板文件不存在: {self.json_path}")
            self._templates = []
            return []
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"方剂模板文件解析失败: {e}")
            self._templates = []
            return []
        except Exception as e:
            logger.error(f"加载方剂模板异常: {e}")
            self._templates = []
            return []

    def get_by_category(self, category: str) -> List[Dict]:
        """按分类筛选方剂。

        Args:
            category: 分类名称（如"补益剂"），空字符串或 None 返回全部。

        Returns:
            匹配分类的方剂列表
        """
        if not category:
            return self.load_templates()
        return [t for t in self.load_templates() if t.get('category') == category]

    def search(self, keyword: str) -> List[Dict]:
        """按名称/主治/描述搜索方剂（包含匹配，不区分大小写）。

        Args:
            keyword: 搜索关键词，空字符串返回全部。

        Returns:
            匹配关键词的方剂列表
        """
        if not keyword:
            return self.load_templates()
        kw = keyword.strip().lower()
        if not kw:
            return self.load_templates()
        results = []
        for t in self.load_templates():
            name = (t.get('name') or '').lower()
            indication = (t.get('indication') or '').lower()
            description = (t.get('description') or '').lower()
            if kw in name or kw in indication or kw in description:
                results.append(t)
        return results

    def get_categories(self) -> List[str]:
        """获取所有分类（按出现顺序去重）。

        Returns:
            分类名称列表
        """
        seen = set()
        categories: List[str] = []
        for t in self.load_templates():
            cat = t.get('category')
            if cat and cat not in seen:
                seen.add(cat)
                categories.append(cat)
        return categories

    def get_by_name(self, name: str) -> Optional[Dict]:
        """按方剂名精确查找单个方剂。

        Args:
            name: 方剂名称

        Returns:
            匹配的方剂 dict；未找到返回 None
        """
        if not name:
            return None
        for t in self.load_templates():
            if t.get('name') == name:
                return t
        return None
