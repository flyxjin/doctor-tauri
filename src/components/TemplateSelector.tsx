import { Modal, Input, Select, List, Tag, Button, Empty } from 'antd';
import { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { DeleteOutlined } from '@ant-design/icons';
import {
  getTemplates,
  getCategories,
  searchTemplates,
  type PrescriptionTemplate,
} from '@/services/templateService';
import { listMyTemplates, deleteMyTemplate } from '@/api/tauri';
import type { MyTemplate } from '@/types';

interface Props {
  open: boolean;
  onClose: () => void;
  onSelect: (template: PrescriptionTemplate) => void;
}

const MY_CATEGORY = '我的方剂';

/** 方剂模板选择对话框：搜索 / 分类筛选 / 点击选中后关闭并回传。
 *  内置经典方 + 数据库"我的方剂"（个人习惯方）合并展示。 */
export default function TemplateSelector({ open, onClose, onSelect }: Props) {
  const queryClient = useQueryClient();
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string>('');

  // 我的方剂（数据库），转成与经典方一致的形状参与搜索/筛选
  const { data: myTemplates } = useQuery({
    queryKey: ['my-templates'],
    queryFn: listMyTemplates,
    enabled: open,
  });

  const myAsTemplates: PrescriptionTemplate[] = useMemo(
    () =>
      (myTemplates ?? []).map((t) => ({
        name: t.name,
        category: MY_CATEGORY,
        description: t.description,
        indication: t.indication,
        items: t.items,
      })),
    [myTemplates],
  );

  const filtered = useMemo(() => {
    // "我的方剂"分类下只搜个人方；其余走经典方搜索
    const staticResult = keyword ? searchTemplates(keyword) : getTemplates();
    const mine = keyword
      ? myAsTemplates.filter(
          (t) =>
            t.name.toLowerCase().includes(keyword.toLowerCase()) ||
            t.indication.toLowerCase().includes(keyword.toLowerCase()),
        )
      : myAsTemplates;
    const merged = category === MY_CATEGORY ? mine : [...mine, ...staticResult];
    return category && category !== MY_CATEGORY
      ? merged.filter((t) => t.category === category)
      : merged;
  }, [keyword, category, myAsTemplates]);

  const categories = useMemo(() => {
    const staticCats = getCategories().filter((c) => c !== MY_CATEGORY);
    return myAsTemplates.length > 0 ? [MY_CATEGORY, ...staticCats] : staticCats;
  }, [myAsTemplates.length]);

  const handleDeleteMine = async (mine: MyTemplate | undefined) => {
    if (!mine || mine.id === null) return;
    try {
      await deleteMyTemplate(mine.id);
      queryClient.invalidateQueries({ queryKey: ['my-templates'] });
    } catch (e) {
      console.error('删除我的方剂失败:', e);
    }
  };

  const renderItems = (item: PrescriptionTemplate) => (
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
            fontFamily: 'var(--font-display)',
            fontWeight: 600,
            fontSize: 15,
          }}
        >
          {item.name}
        </span>
        <Tag color={item.category === MY_CATEGORY ? 'gold' : 'green'}>{item.category}</Tag>
        {item.category === MY_CATEGORY && (
          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              const mine = myTemplates?.find((t) => t.name === item.name);
              handleDeleteMine(mine);
            }}
          />
        )}
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
        组成：
        {item.items.map((i) => `${i.name}${i.quantity}${i.unit}`).join('、')}
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
        主治：{item.indication || item.description || '—'}
      </div>
    </div>
  );

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
          options={categories.map((c) => ({ label: c, value: c }))}
        />
      </div>
      <div style={{ marginBottom: 8, fontSize: 12, color: 'var(--text-muted)' }}>
        共 {filtered.length} 首{category ? `（${category}）` : ''}
        {keyword && ` · 关键字“${keyword}”`}
      </div>
      <List
        dataSource={filtered}
        locale={{
          emptyText: (
            <Empty
              description={keyword ? '没有匹配的方剂' : '暂无方剂模板'}
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ),
        }}
        style={{ maxHeight: 400, overflow: 'auto' }}
        renderItem={(item) => (
          <List.Item
            style={{ cursor: 'pointer', padding: '12px 16px', borderRadius: 8 }}
            onClick={() => {
              onSelect(item);
              onClose();
            }}
          >
            {renderItems(item)}
          </List.Item>
        )}
      />
      <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-muted)' }}>
        提示：在开处方页点击「另存为我的方剂」，可把当前处方保存为个人模板。
      </div>
    </Modal>
  );
}
