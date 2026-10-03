import { Modal, Input, Select, List, Tag } from 'antd';
import { useState, useMemo } from 'react';
import {
  getTemplates,
  getCategories,
  searchTemplates,
  type PrescriptionTemplate,
} from '@/services/templateService';

interface Props {
  open: boolean;
  onClose: () => void;
  onSelect: (template: PrescriptionTemplate) => void;
}

/** 方剂模板选择对话框：搜索 / 分类筛选 / 点击选中后关闭并回传 */
export default function TemplateSelector({ open, onClose, onSelect }: Props) {
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string>('');

  const filtered = useMemo(() => {
    let result = keyword ? searchTemplates(keyword) : getTemplates();
    if (category) result = result.filter((t) => t.category === category);
    return result;
  }, [keyword, category]);

  return (
    <Modal
      title="选择方剂模板"
      open={open}
      onCancel={onClose}
      footer={null}
      width={720}
    >
      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索方剂名称/主治"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          allowClear
          style={{ flex: 1 }}
        />
        <Select
          placeholder="全部分类"
          value={category || undefined}
          onChange={(v) => setCategory(v ?? '')}
          allowClear
          style={{ width: 160 }}
          options={getCategories().map((c) => ({ label: c, value: c }))}
        />
      </div>
      <div style={{ marginBottom: 8, fontSize: 12, color: 'var(--text-muted)' }}>
        共 {filtered.length} 首{category ? `（${category}）` : ''}
        {keyword && ` · 关键字“${keyword}”`}
      </div>
      <List
        dataSource={filtered}
        style={{ maxHeight: 400, overflow: 'auto' }}
        renderItem={(item) => (
          <List.Item
            style={{ cursor: 'pointer', padding: '12px 16px', borderRadius: 8 }}
            onClick={() => {
              onSelect(item);
              onClose();
            }}
          >
            <div style={{ width: '100%' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  marginBottom: 4,
                }}
              >
                <span
                  style={{
                    fontFamily: 'Noto Serif SC, serif',
                    fontWeight: 600,
                    fontSize: 15,
                  }}
                >
                  {item.name}
                </span>
                <Tag color="green">{item.category}</Tag>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                组成：
                {item.items.map((i) => `${i.name}${i.quantity}${i.unit}`).join('、')}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                主治：{item.indication}
              </div>
            </div>
          </List.Item>
        )}
      />
    </Modal>
  );
}
